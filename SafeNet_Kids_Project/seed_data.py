"""seed_data.py — Populates professional demo data for the SafeNet Kids dashboard."""
import os
from datetime import datetime, timedelta
import random

LOG_FILE = "data/safenet_audit.log"

# Production-style threat template
THREAT_TEMPLATE = "[{ts}] Threat: {category} | Trigger: '{trigger}' | Source: '{source}'"

THREAT_SAMPLES = [
    ("Restricted Activity (Adult)", "porn", "Keyboard: Typed in Chrome browser"),
    ("Restricted Activity (Adult)", "xvideos", "Screen OCR: Detected in window title"),
    ("Restricted Activity (Violence)", "how to make a bomb", "Keyboard: Search query detected"),
    ("Restricted Activity (Violence)", "fighting clips", "AI Detection: Violence detected in screenshot"),
    ("Restricted Activity (Drugs)", "buy cannabis", "Keyboard: Message sent in Discord"),
    ("Self-Harm Detection", "i hate my life", "NLP: Sensitive sentiment detected"),
    ("Blocked Website", "roblox.com", "Browser Monitor: Attempted visit"),
    ("Restricted App", "minecraft.exe", "Process Blocker: Blocked during study hours"),
    ("Cyberbullying", "you are a loser", "NLP: Harassment detected in chat window")
]

def seed(count=30):
    os.makedirs("data", exist_ok=True)
    
    # Start the log with initialization events
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Info: SafeNet Kids Initialized Successfully.\n")
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Info: All AI Sensors (NLP, CV, OCR) are active.\n")

        # Generate backdated threats
        for i in range(count):
            # Distribute over the last 12 hours
            t = datetime.now() - timedelta(minutes=random.randint(1, 720))
            ts = t.strftime("%Y-%m-%d %H:%M:%S")
            
            category, trigger, source = random.choice(THREAT_SAMPLES)
            log_line = THREAT_TEMPLATE.format(ts=ts, category=category, trigger=trigger, source=source)
            f.write(log_line + "\n")
            
    print(f"SUCCESS: Seeded {count} professional threat entries into {LOG_FILE}")
    print("You can now view these threats in the Dashboard and generate PDF Reports.")

if __name__ == "__main__":
    seed()
