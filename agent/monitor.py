"""
agent/monitor.py — SafeNet Kids Child Monitoring Agent
Runs on the child's device. Monitors keyboard, browser, apps, and screen.
"""
import asyncio, time, os, base64, platform, sys, secrets
import httpx
import psutil
from datetime import datetime

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
API_BASE  = os.getenv("SAFENET_API", "http://localhost:8000")
LINK_CODE = os.getenv("LINK_CODE", "")      # Set by child during setup
CHILD_ID  = None
PARENT_ID = None
DEVICE_ID = secrets.token_hex(8)

KEYBOARD_BUFFER = []
LAST_WINDOW     = ""
SCREEN_INTERVAL = 30   # seconds between periodic screenshots


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
            if result.get("is_threat") and not _gemini_agent_model:
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


# ── Heartbeat ─────────────────────────────────────────────────────────────────
async def heartbeat_loop():
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                r = await client.post(f"{API_BASE}/api/child/heartbeat",
                                      json={"child_id": CHILD_ID, "is_online": True})
                data = r.json()
                if data.get("device_locked"):
                    show_warning_popup("Device Locked by Parent")
            except Exception:
                pass
            await asyncio.sleep(30)


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
        show_warning_popup(result.get("threat_type", "Unsafe Content"))


# ── App Monitor ───────────────────────────────────────────────────────────────
async def app_monitor_loop():
    config = {}
    while True:
        try:
            # Poll config (blocked apps list)
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{API_BASE}/api/child/config/{CHILD_ID}")
                config = r.json()
        except Exception:
            pass

        blocked_apps = config.get("blocked_apps", [])

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

        await asyncio.sleep(15)


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
