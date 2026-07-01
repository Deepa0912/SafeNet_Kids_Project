"""
agent/monitor.py — SafeNet Kids Child Monitoring Agent
Runs on the child's device. Monitors keyboard, browser, apps, and screen.
"""
import asyncio, time, os, base64, platform, sys, secrets, subprocess
import httpx
import psutil
from datetime import datetime
from dotenv import load_dotenv

try:
    import pyautogui
    PYAUTOGUI = True
except Exception:
    PYAUTOGUI = False

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

# ── Unsafe keyword categories to detect in browser title/URL ─────────────────
# Each category maps to a list of trigger words.
# All checks are case-insensitive substring matches against the window title.
UNSAFE_KEYWORDS: dict[str, list[str]] = {

    "Adult Content": [
        "xxx", "porn", "pornhub", "xvideos", "xhamster", "xnxx", "redtube",
        "youporn", "tube8", "spankbang", "eporner", "tnaflix", "4tube",
        "livejasmin", "chaturbate", "bongacams", "myfreecams", "stripchat",
        "onlyfans", "fansly", "manyvids", "brazzers", "bangbros", "naughtyamerica",
        "sex", "nude", "naked", "hentai", "erotic", "camgirl", "fetish",
        "sexvid", "adult content", "18+", "nsfw", "hot girls", "free porn",
    ],

    "Violence / Gore": [
        "gore", "bestgore", "liveleak", "graphic violence", "death video",
        "murder video", "beheading", "execution video", "torture video",
        "shock site", "cartel video", "brutal fight", "mass shooting video",
        "war crimes video", "live murder", "dead body",
    ],

    "Drug Related": [
        "buy drugs", "buy weed", "buy cocaine", "buy heroin", "buy meth",
        "buy mdma", "buy lsd", "dark web drugs", "drug dealer", "how to get high",
        "how to make drugs", "drug overdose how", "buy ketamine", "buy fentanyl",
        "silk road", "drug market", "weed shop", "cannabis delivery",
        "psychedelics buy", "shrooms buy", "buy pills online",
        "get high at home", "snort drugs", "inject drugs",
        "drug effects", "recreational drugs", "get drugs delivered",
    ],

    "Self Harm": [
        # Direct phrases
        "i will die", "i want to die", "i wanna die", "kill myself",
        "want to kill myself", "i want to kill myself", "end my life",
        "end it all", "no reason to live", "don't want to live",
        "not worth living", "life is not worth", "tired of living",
        "can't go on", "can't take it anymore", "better off dead",
        "wish i was dead", "wish i were dead", "ready to die",
        "planning to die", "going to kill myself", "will kill myself",
        # Methods
        "how to self harm", "how to cut yourself", "how to kill yourself",
        "suicide methods", "painless suicide", "ways to die", "suicide tutorial",
        "how to commit suicide", "self harm tips", "cutting tips",
        "how to overdose", "lethal dose", "hanging yourself",
        "how to hang yourself", "wrist cutting",
        # Communities / forums
        "suicide forum", "pro suicide", "pro ana", "pro mia",
        "encourage suicide", "suicide note", "suicide pact",
        "r/suicide", "suicide watch", "teen suicide",
    ],

    "Gambling": [
        "online casino", "bet online", "sports betting", "poker online",
        "roulette online", "blackjack online", "slot machine online",
        "gambling site", "bet365", "draftkings", "fanduel casino",
        "online gambling", "real money casino", "win money gambling",
        "crash gambling", "stake casino", "rollbit", "betway",
        "1xbet", "888casino", "spin casino", "jackpot city",
        "bet for money", "free slots real money", "casino bonus",
        "poker real money", "teen patti cash", "rummy cash",
        "ludo earn money", "fantasy cricket money", "dream11",
    ],

    "Weapons": [
        "buy gun online", "illegal weapons", "buy knife online", "ghost gun",
        "convert gun automatic", "buy silencer", "how to make bomb",
        "pipe bomb instructions", "how to make explosives", "buy explosive",
        "illegal firearms", "untraceable gun",
    ],

    "Hate Speech": [
        "white supremacy", "neo nazi", "racial slur", "kill all ", "hate jews",
        "white power", "kkk site", "ethnic cleansing", "islamic terrorism",
        "terrorism recruitment", "join isis", "jihadist",
    ],

    "Cyberbullying / Predators": [
        "omegle", "chatroulette", "tinychat", "random video chat",
        "meet strangers online", "anonymous chat kids", "kik strangers",
        "snapchat strangers", "discord 18+", "teen dating", "meet teens online",
        "you should die", "kill yourself", "kys", "nobody likes you",
        "go kill yourself", "you are worthless", "nobody cares about you",
        "you should end it", "commit suicide", "rope yourself",
        "bully tips", "how to bully", "cyberbully",
    ],

    "Dark Web": [
        ".onion", "tor browser", "dark web", "darknet", "hidden wiki",
        "how to access dark web", "buy on darknet", "illegal dark web",
    ],
}

# Flat lookup: keyword -> category (built at startup for fast O(n) scan)
_KW_CATEGORY: dict[str, str] = {
    kw: cat
    for cat, keywords in UNSAFE_KEYWORDS.items()
    for kw in keywords
}


def close_active_tab():
    """
    Close the current browser TAB using Ctrl+W.
    Tries 3 methods in order so it always works regardless of what's installed.
    Method 1: focus window → pyautogui Ctrl+W
    Method 2: pynput keyboard Ctrl+W
    Method 3: close entire browser window (last resort)
    """
    import time as _time

    # ── Method 1: pyautogui (most reliable when window is focused) ────────────
    if PYAUTOGUI and PYGETWINDOW:
        try:
            win = gw.getActiveWindow()
            if win:
                win.activate()          # bring window to front
                _time.sleep(0.15)       # wait for focus
            import pyautogui
            pyautogui.hotkey('ctrl', 'w')
            print("[SafeNet Agent] 🛡️ Tab closed via pyautogui Ctrl+W")
            return
        except Exception as e:
            print(f"[SafeNet Agent] pyautogui Ctrl+W failed: {e}")

    # ── Method 2: pynput keyboard (works even if pyautogui unavailable) ───────
    if PYNPUT:
        try:
            from pynput.keyboard import Key, Controller
            _kb = Controller()
            _time.sleep(0.1)
            with _kb.pressed(Key.ctrl):
                _kb.press('w')
                _kb.release('w')
            print("[SafeNet Agent] 🛡️ Tab closed via pynput Ctrl+W")
            return
        except Exception as e:
            print(f"[SafeNet Agent] pynput Ctrl+W failed: {e}")

    # ── Method 3: close entire browser window (last resort) ───────────────────
    print("[SafeNet Agent] ⚠️  Falling back to window close")
    close_active_window()


def close_active_window():
    """Identifies the active browser window and closes it (last resort)."""
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


# Track which adapters we disabled so resume re-enables only those
_paused_adapter_names: list = []


def _is_admin() -> bool:
    """Check if the process has administrator privileges."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def pause_internet():
    """Disable all connected network adapters using PowerShell."""
    global _paused_adapter_names
    print("[SafeNet Agent] 📵 Pausing internet...")
    if platform.system() != "Windows":
        print("[SafeNet Agent] Internet pause only supported on Windows.")
        return
    if not _is_admin():
        print("[SafeNet Agent] ⚠️  WARNING: Not running as Administrator — Pause Internet may fail.")
    try:
        # Get names of all currently UP adapters, then disable them
        ps = (
            "$up = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }; "
            "$up | Disable-NetAdapter -Confirm:$false; "
            "$up.Name -join '|'"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, timeout=15
        )
        names_str = result.stdout.strip().split("\n")[-1]  # last line has the names
        _paused_adapter_names = [n.strip() for n in names_str.split("|") if n.strip()]
        if _paused_adapter_names:
            print(f"[SafeNet Agent]   Disabled: {_paused_adapter_names}")
        else:
            print(f"[SafeNet Agent]   No adapters found or disabled. stderr: {result.stderr.strip()}")
    except Exception as e:
        print(f"[SafeNet Agent] Pause internet error: {e}")


def resume_internet():
    """Re-enable the exact adapters that were paused."""
    global _paused_adapter_names
    print("[SafeNet Agent] 🌐 Resuming internet...")
    if platform.system() != "Windows":
        return
    try:
        targets = _paused_adapter_names if _paused_adapter_names else []
        if targets:
            names_ps = ",".join(f"'{n}'" for n in targets)
            ps = f"Enable-NetAdapter -Name @({names_ps}) -Confirm:$false"
        else:
            # Fallback: enable any disabled adapter we might have missed
            ps = "Get-NetAdapter | Where-Object { $_.Status -ne 'Up' } | Enable-NetAdapter -Confirm:$false"
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, timeout=15
        )
        print(f"[SafeNet Agent]   Re-enabled: {targets or 'all disabled adapters'}")
        _paused_adapter_names = []
    except Exception as e:
        print(f"[SafeNet Agent] Resume internet error: {e}")


def enforce_blocked_urls(blocked_urls: list):
    """Close TAB if its title contains a blocked domain."""
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
                close_active_tab()
                show_warning_popup(f"Blocked Website: {domain}")
                break
    except Exception as e:
        print(f"[SafeNet Agent] URL enforce error: {e}")


async def url_search_monitor_loop():
    """
    Continuously reads the active browser window title every 2 seconds.
    Detects unsafe keywords in the title (which includes search terms and URLs)
    and closes the tab immediately, logs the threat, and alerts the parent.
    """
    _alerted_titles: set = set()   # avoid spamming the same page repeatedly

    BROWSER_NAMES = ["chrome", "edge", "firefox", "opera", "brave", "safari", "msedge"]

    while True:
        try:
            if PYGETWINDOW:
                win = gw.getActiveWindow()
                if win:
                    title = win.title
                    title_lower = title.lower()
                    is_browser = any(b in title_lower for b in BROWSER_NAMES)

                    if is_browser:
                        # Scan all unsafe keyword categories
                        for kw, category in _KW_CATEGORY.items():
                            if kw in title_lower and title not in _alerted_titles:
                                _alerted_titles.add(title)
                                print(f"[SafeNet Agent] 🚨 [{category}] keyword '{kw}' in: {title}")

                                # 1. Close the tab immediately
                                close_active_tab()

                                # 2. Show warning popup to child
                                show_warning_popup(category)

                                # 3. Take screenshot as evidence
                                await send_screenshot(f"{category}: {kw}")

                                # 4. Log threat to backend
                                await send_activity(
                                    "url_blocked",
                                    f"[{category}] keyword '{kw}' detected in: '{title}'"
                                )

                                break  # one action per cycle

        except Exception as e:
            print(f"[SafeNet Agent] URL/search monitor error: {e}")

        await asyncio.sleep(2)   # check every 2 seconds



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

# ── Shared Gemini safety prompt (used by screenshot analyser + browser AI monitor)
_GEMINI_SAFETY_PROMPT = """You are SafeNet Kids, a child safety AI monitoring a child's screen.
Analyze this screenshot and determine if it contains ANY content harmful or inappropriate for a child under 18.

Check ALL of these categories:
- Adult Content: nudity, pornography, sexual content, explicit images or text
- Violence / Gore: graphic violence, blood, death, torture, brutal fights
- Self Harm: suicide content, self-injury tutorials, eating disorder forums
- Drug Related: drug purchases, how-to drug use, drug promotion
- Gambling: casino sites, sports betting, real-money games
- Cyberbullying: hate messages, threats, harassment, humiliation
- Predators: stranger chat sites, adult dating, suspicious messaging
- Weapons: bomb-making, illegal weapon purchase, explosives
- Hate Speech: racism, extremism, terrorist recruitment
- Dark Web: darknet markets, Tor usage, illegal content

If content is SAFE (education, entertainment, news, normal social media) respond with Safe.

Respond ONLY in this exact format:
CATEGORY: <category or Safe>
CONFIDENCE: <0.0 to 1.0>
IS_THREAT: <true or false>
REASON: <one short sentence of what you saw>"""


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
                response = _gemini_agent_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        _GEMINI_SAFETY_PROMPT,
                        genai_types.Part.from_bytes(data=buf2.getvalue(), mime_type="image/png"),
                    ],
                )
                raw    = response.text.strip()
                cat_m  = re.search(r"CATEGORY:\s*(.+)",         raw)
                conf_m = re.search(r"CONFIDENCE:\s*([\d.]+)",   raw)
                thr_m  = re.search(r"IS_THREAT:\s*(true|false)", raw, re.IGNORECASE)
                rsn_m  = re.search(r"REASON:\s*(.+)",            raw)
                if cat_m and thr_m:
                    category   = cat_m.group(1).strip()
                    confidence = float(conf_m.group(1)) if conf_m else 0.0
                    is_threat  = thr_m.group(1).lower() == "true"
                    detail     = rsn_m.group(1).strip() if rsn_m else category
                    if is_threat and category != "Safe" and confidence >= 0.65:
                        reason = f"Gemini: {category}"
                        await send_activity(
                            "screenshot_vision",
                            f"[Gemini Vision] {category} ({round(confidence*100)}%) — {detail}"
                        )
                        close_active_tab()
                        show_warning_popup(f"{category}\n\n{detail}")
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
                close_active_tab()   # 🛡️ Close tab only
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
        # Take immediate screenshot before closing tab as evidence
        await send_screenshot(f"Keylog Threat: {result.get('threat_type')}")
        close_active_tab()   # 🛡️ Close tab only, not whole browser
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


# ── Screen Monitor (periodic background screenshots) ─────────────────────────
async def screen_monitor_loop():
    while True:
        await send_screenshot("periodic")
        await asyncio.sleep(SCREEN_INTERVAL)


# ── AI Browser Monitor (Gemini Vision on every active browser tab) ────────────
async def browser_ai_monitor_loop():
    """
    Every 10 s: if a browser is active, capture a screenshot and send it to
    Gemini Vision with the full child-safety prompt.
    Catches visual content, images, and videos that keyword lists miss entirely.
    Requires GEMINI_API_KEY to be configured.
    """
    if not _gemini_agent_client:
        print("[SafeNet AI] GEMINI_API_KEY not set — AI browser monitor disabled.")
        return
    if not PILLOW:
        print("[SafeNet AI] Pillow not installed — AI browser monitor disabled.")
        return

    print("[SafeNet AI] 🧠 AI Browser Monitor active (Gemini Vision, every 10 s)")

    BROWSER_NAMES = ["chrome", "edge", "firefox", "opera", "brave", "safari", "msedge"]
    _analyzed: set = set()   # page titles already acted on (prevent duplicate alerts)
    _cooldown  = 0           # skip N cycles after a block to avoid rapid-fire

    while True:
        try:
            if _cooldown > 0:
                _cooldown -= 1
                await asyncio.sleep(10)
                continue

            if not PYGETWINDOW:
                await asyncio.sleep(10)
                continue

            win = gw.getActiveWindow()
            if not win:
                await asyncio.sleep(10)
                continue

            title     = win.title
            title_low = title.lower()
            if not any(b in title_low for b in BROWSER_NAMES):
                await asyncio.sleep(10)
                continue

            # ── Capture screenshot ──────────────────────────────────────────
            import io, re
            from PIL import ImageGrab
            from google.genai import types as genai_types

            img = ImageGrab.grab()
            img.thumbnail((1280, 720))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            # ── Ask Gemini ──────────────────────────────────────────────────
            response = _gemini_agent_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    _GEMINI_SAFETY_PROMPT,
                    genai_types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                ],
            )
            raw    = response.text.strip()
            cat_m  = re.search(r"CATEGORY:\s*(.+)",         raw)
            conf_m = re.search(r"CONFIDENCE:\s*([\d.]+)",   raw)
            thr_m  = re.search(r"IS_THREAT:\s*(true|false)", raw, re.IGNORECASE)
            rsn_m  = re.search(r"REASON:\s*(.+)",            raw)

            if not (cat_m and thr_m):
                await asyncio.sleep(10)
                continue

            category   = cat_m.group(1).strip()
            confidence = float(conf_m.group(1)) if conf_m else 0.0
            is_threat  = thr_m.group(1).lower() == "true"
            reason     = rsn_m.group(1).strip() if rsn_m else ""

            print(f"[SafeNet AI] 🧠 {category} | {round(confidence*100)}% | threat={is_threat} | {reason}")

            if is_threat and category != "Safe" and confidence >= 0.65 and title not in _analyzed:
                _analyzed.add(title)
                print(f"[SafeNet AI] 🚨 BLOCKING [{category}] {round(confidence*100)}% — {reason}")

                # 1. Close the browser tab immediately
                close_active_tab()

                # 2. Warn the child with category + AI reason
                show_warning_popup(f"{category}\n\n{reason}")

                # 3. Upload screenshot as evidence to parent dashboard
                img_b64 = base64.b64encode(img_bytes).decode()
                async with httpx.AsyncClient(timeout=30) as hc:
                    await hc.post(
                        f"{API_BASE}/api/child/screenshot",
                        json={"child_id": CHILD_ID,
                              "image_b64": img_b64,
                              "reason": f"AI Detected: {category}"}
                    )

                # 4. Log threat to parent dashboard
                await send_activity(
                    "ai_browser_threat",
                    f"[{category}] {round(confidence*100)}% confidence — {reason} — Page: {title}"
                )

                _cooldown = 3   # wait 30 s before re-analyzing (3 × 10 s cycles)

        except Exception as e:
            print(f"[SafeNet AI] Browser AI monitor error: {e}")

        await asyncio.sleep(10)   # check every 10 seconds


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
        url_search_monitor_loop(),    # 🔍 Keyword detection (title/URL, every 2 s)
        browser_ai_monitor_loop(),    # 🧠 Gemini Vision AI  (every 10 s, browser only)
    )


if __name__ == "__main__":
    asyncio.run(main())
