"""
agent/monitor.py — SafeNet Kids Child Monitoring Agent
Runs on the child's device. Monitors keyboard, browser, apps, and screen.
"""
import asyncio, time, os, base64, platform, sys, secrets, subprocess
import httpx
import psutil
from datetime import datetime
from dotenv import load_dotenv

# Load settings from .env file
load_dotenv()

# Optional imports with graceful fallbacks
try:
    from pynput import keyboard as kb_hook
    PYNPUT = True
except Exception:
    PYNPUT = False

try:
    import pygetwindow as gw
    PYGETWINDOW = True
except Exception:
    PYGETWINDOW = False

try:
    from PIL import ImageGrab
    PILLOW = True
except Exception:
    PILLOW = False

try:
    import pytesseract
    OCR = True
except Exception:
    OCR = False

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE  = os.getenv("SAFENET_API", "https://safenetkidsproject-production.up.railway.app")

LINK_CODE = os.getenv("LINK_CODE", "")      # Set by child during setup
CHILD_ID  = None
PARENT_ID = None
DEVICE_ID = secrets.token_hex(8)

KEYBOARD_BUFFER   = []
LAST_WINDOW       = ""
SCREEN_INTERVAL   = 300  # seconds between periodic screenshots (5 min)

# ── Device state tracking (avoids re-locking every heartbeat) ─────────────────
_device_locked    = False
_internet_paused  = False


def close_active_window():
    """Identifies the active browser window and closes it."""
    if not PYGETWINDOW:
        return
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            return
        title = active_window.title.lower()
        browsers = ["chrome", "edge", "firefox", "opera", "safari", "brave", "incognito"]
        if any(b in title for b in browsers):
            print(f"[SafeNet Agent] 🛡️ ACTIVE DEFENSE: Closing Browser — {active_window.title}")
            active_window.close()
    except Exception as e:
        print(f"[SafeNet Agent] 🛡️ Active Defense Error: {e}")


# ── OS-Level Control Enforcement ──────────────────────────────────────────────

def lock_device():
    """Lock the Windows workstation screen immediately."""
    print("[SafeNet Agent] 🔒 Locking device...")
    try:
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        elif platform.system() == "Darwin":
            os.system("pmset displaysleepnow")
        else:
            os.system("loginctl lock-session")
    except Exception as e:
        print(f"[SafeNet Agent] Lock error: {e}")


def _get_active_adapters() -> list:
    """Return list of enabled Wi-Fi / Ethernet adapter names on Windows."""
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "show", "interface"],
            text=True, errors="ignore"
        )
        adapters = []
        for line in out.splitlines():
            # Lines look like: 'Enabled    Connected    Dedicated     Wi-Fi'
            parts = line.split()
            if len(parts) >= 4 and parts[0] in ("Enabled", "Disabled"):
                name = " ".join(parts[3:])
                adapters.append((parts[0], name))
        return adapters
    except Exception:
        return []


def pause_internet():
    """Disable all active network adapters to pause internet access."""
    print("[SafeNet Agent] 📵 Pausing internet...")
    if platform.system() != "Windows":
        print("[SafeNet Agent] Internet pause only supported on Windows.")
        return
    try:
        for state, name in _get_active_adapters():
            if state == "Enabled":
                subprocess.run(
                    ["netsh", "interface", "set", "interface", name, "disable"],
                    capture_output=True
                )
                print(f"[SafeNet Agent]   Disabled adapter: {name}")
    except Exception as e:
        print(f"[SafeNet Agent] Pause internet error: {e}")


def resume_internet():
    """Re-enable all disabled network adapters."""
    print("[SafeNet Agent] 🌐 Resuming internet...")
    if platform.system() != "Windows":
        return
    try:
        for state, name in _get_active_adapters():
            if state == "Disabled":
                subprocess.run(
                    ["netsh", "interface", "set", "interface", name, "enable"],
                    capture_output=True
                )
                print(f"[SafeNet Agent]   Enabled adapter: {name}")
    except Exception as e:
        print(f"[SafeNet Agent] Resume internet error: {e}")


def enforce_blocked_urls(blocked_urls: list):
    """Close browser if its title/URL contains a blocked domain."""
    if not PYGETWINDOW or not blocked_urls:
        return
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            return
        title = active_window.title.lower()
        for url in blocked_urls:
            domain = url.lower().replace("https://", "").replace("http://", "").split("/")[0]
            if domain and domain in title:
                print(f"[SafeNet Agent] 🚫 Blocked URL detected in title: {domain}")
                active_window.close()
                show_warning_popup(f"Blocked Website: {domain}")
                break
    except Exception as e:
        print(f"[SafeNet Agent] URL enforce error: {e}")



# ── Startup: Link Device ──────────────────────────────────────────────────────
def link_device():
    global CHILD_ID, PARENT_ID, LINK_CODE
    if not LINK_CODE:
        LINK_CODE = input("Enter your Parent Linking Code: ").strip().upper()
    try:
        r = httpx.post(f"{API_BASE}/api/child/link",
                       json={"link_code": LINK_CODE, "device_id": DEVICE_ID}, timeout=10)
        r.raise_for_status()
        data      = r.json()
        CHILD_ID  = data["child_id"]
        PARENT_ID = data["parent_id"]
        print(f"[SafeNet Agent] Linked as {data['child_name']} (ID={CHILD_ID})")
        return True
    except Exception as e:
        print(f"[SafeNet Agent] Link failed: {e}")
        return False


# ── Send Activity ─────────────────────────────────────────────────────────────
async def send_activity(log_type: str, value: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(f"{API_BASE}/api/child/activity",
                                  json={"child_id": CHILD_ID, "log_type": log_type, "value": value})
            return r.json()
        except Exception:
            return {}


# Gemini Vision for agent-side image analysis (new google-genai SDK)
_gemini_agent_client = None
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if _GEMINI_KEY:
    try:
        from google import genai as google_genai
        _gemini_agent_client = google_genai.Client(api_key=_GEMINI_KEY)
        print("[SafeNet Agent] Gemini Vision enabled (gemini-2.0-flash).")
    except Exception as e:
        print(f"[SafeNet Agent] Gemini Vision unavailable: {e}")


# ── Send Screenshot ───────────────────────────────────────────────────────────
async def send_screenshot(reason: str = "monitoring"):
    if not PILLOW:
        return
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.thumbnail((1280, 720))

        # Gemini Vision — direct image analysis (most accurate)
        if _gemini_agent_client:
            try:
                import io, re
                from google.genai import types as genai_types
                buf2 = io.BytesIO()
                img.save(buf2, format="PNG")
                prompt = (
                    "You are SafeNet Kids, a child safety AI. Look at this screenshot and "
                    "determine if it contains harmful content for a child.\n"
                    "Categories: Adult Content, Gambling, Drug Related, Cyberbullying, Self Harm, Violence, Safe\n"
                    "Respond ONLY in this format:\n"
                    "CATEGORY: <category>\nCONFIDENCE: <0.0-1.0>\nIS_THREAT: <true|false>"
                )
                response = _gemini_agent_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        prompt,
                        genai_types.Part.from_bytes(data=buf2.getvalue(), mime_type="image/png"),
                    ],
                )
                raw = response.text.strip()
                cat_m  = re.search(r"CATEGORY:\s*(.+)", raw)
                thr_m  = re.search(r"IS_THREAT:\s*(true|false)", raw, re.IGNORECASE)
                if cat_m and thr_m:
                    category  = cat_m.group(1).strip()
                    is_threat = thr_m.group(1).lower() == "true"
                    if is_threat and category != "Safe":
                        reason = f"Gemini Detected: {category}"
                        await send_activity("screenshot_vision", f"[Gemini Vision] {category}")
                        close_active_window() # 🛡️ INSTANT ACTION
                        show_warning_popup(category)
            except Exception as ve:
                print(f"[Agent] Gemini Vision error: {ve}")

        # OCR text fallback
        ocr_text = ""
        if OCR:
            try:
                ocr_text = pytesseract.image_to_string(img, config="--psm 11")
            except Exception:
                pass

        # Upload screenshot to backend as evidence
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True, quality=70)
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(f"{API_BASE}/api/child/screenshot",
                              json={"child_id": CHILD_ID, "image_b64": img_b64, "reason": reason})

        # Also analyze OCR text for threats via backend AI
        if ocr_text.strip():
            result = await send_activity("screenshot_ocr", ocr_text[:1000])
            if result.get("is_threat") and not _gemini_agent_client:
                close_active_window() # 🛡️ INSTANT ACTION
                show_warning_popup(result.get("threat_type", "Unsafe Content"))

    except Exception as e:
        print(f"[Agent] Screenshot error: {e}")


# ── Warning Popup ─────────────────────────────────────────────────────────────
def show_warning_popup(category: str):
    msg = (
        f"⚠️  SafeNet Kids — Warning\n\n"
        f"Unsafe content detected.\nCategory: {category}\n\n"
        "Access blocked. Your parent has been notified."
    )
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg, "SafeNet Kids — Warning", 0x30 | 0x1000)
        except Exception:
            print(f"[POPUP] {msg}")
    elif platform.system() == "Darwin":
        os.system(f'osascript -e \'display alert "SafeNet Kids" message "{msg}"\'')
    else:
        try:
            os.system(f'notify-send "SafeNet Kids" "{category} detected"')
        except Exception:
            print(f"[POPUP] {msg}")


# ── Heartbeat + Command Enforcement ──────────────────────────────────────────
async def heartbeat_loop():
    global _device_locked, _internet_paused
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(f"{API_BASE}/api/child/heartbeat",
                                      json={"child_id": CHILD_ID, "is_online": True})
                data = r.json()

            should_lock   = data.get("device_locked", False)
            should_pause  = data.get("internet_paused", False)

            # ── Lock / Unlock enforcement ──
            if should_lock and not _device_locked:
                _device_locked = True
                lock_device()
                show_warning_popup("Device Locked by Parent")
            elif not should_lock and _device_locked:
                _device_locked = False
                print("[SafeNet Agent] 🔓 Device unlocked by parent.")
                # Windows auto-unlocks when parent lifts the Lock flag;
                # nothing to do here — the lock screen is already up and the
                # user simply logs back in after the parent unlocks.

            # ── Internet pause / resume enforcement ──
            if should_pause and not _internet_paused:
                _internet_paused = True
                pause_internet()
            elif not should_pause and _internet_paused:
                _internet_paused = False
                resume_internet()

        except Exception as e:
            print(f"[SafeNet Agent] Heartbeat error: {e}")
        await asyncio.sleep(15)  # Poll every 15 s for faster response


# ── Keyboard Monitor ─────────────────────────────────────────────────────────
def start_keyboard_listener():
    if not PYNPUT:
        return

    buffer = []

    def on_press(key):
        try:
            ch = key.char
        except AttributeError:
            if key == kb_hook.Key.space:
                ch = " "
            elif key == kb_hook.Key.enter:
                text = "".join(buffer).strip()
                buffer.clear()
                if text and len(text) > 3:
                    asyncio.run_coroutine_threadsafe(
                        _process_keyboard(text), _loop
                    )
                return
            else:
                return
        if ch:
            buffer.append(ch)

    listener = kb_hook.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

_loop = None

async def _process_keyboard(text: str):
    result = await send_activity("keyboard", text)
    if result.get("is_threat"):
        # Take immediate screenshot before closing window as evidence
        await send_screenshot(f"Keylog Threat: {result.get('threat_type')}")
        close_active_window() # 🛡️ INSTANT ACTION
        show_warning_popup(result.get("threat_type", "Unsafe Content"))



# ── App + URL Monitor ────────────────────────────────────────────────────────
async def app_monitor_loop():
    config = {}
    while True:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{API_BASE}/api/child/config/{CHILD_ID}")
                config = r.json()
        except Exception:
            pass

        blocked_apps = config.get("blocked_apps", [])
        blocked_urls = config.get("blocked_urls", [])

        # ── Kill blocked applications ──
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                pname = proc.info["name"].lower()
                for bapp in blocked_apps:
                    if bapp.lower() in pname:
                        proc.kill()
                        await send_activity("app_blocked", pname)
                        show_warning_popup(f"Blocked Application: {pname}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # ── Enforce blocked URLs via window title ──
        enforce_blocked_urls(blocked_urls)

        await asyncio.sleep(10)  # Check every 10 s


# ── Screen Monitor ────────────────────────────────────────────────────────────
async def screen_monitor_loop():
    while True:
        await send_screenshot("periodic")
        await asyncio.sleep(SCREEN_INTERVAL)


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    global _loop
    _loop = asyncio.get_event_loop()

    print("[SafeNet Kids Monitoring Agent] Starting...")
    if not link_device():
        sys.exit(1)

    start_keyboard_listener()

    await asyncio.gather(
        heartbeat_loop(),
        app_monitor_loop(),
        screen_monitor_loop(),
    )


if __name__ == "__main__":
    asyncio.run(main())
