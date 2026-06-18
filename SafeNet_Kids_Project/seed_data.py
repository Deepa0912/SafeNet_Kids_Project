"""seed_data.py — Populates demo data for the SafeNet Kids dashboard."""
import os
import datetime
import random

LOG_FILE = "data/safenet_audit.log"

ACTIVITIES = [
    ("Info", "SafeNet Monitoring System initialized."),
    ("Info", "Process blocker service started."),
    ("Info", "NLP threat database version 2.1 loaded."),
    ("Info", "Keylogger active — Monitoring window: Chrome"),
    ("Threat: Keyboard", "Potentially harmful phrase detected: 'how to bypass parental controls'"),
    ("Info", "Blocked process attempt: 'roblox.exe'"),
    ("Threat: Computer Vision", "Inappropriate visual content detected on Screen 1."),
    ("Info", "Keylogger active — Monitoring window: Discord"),
    ("Threat: NLP", "Bullying behavior detected in typed message: 'you are so stupid'"),
    ("Info", "Screen capture analyzed: No threats found."),
    ("Threat: Keyboard", "Sensitive data entry attempt: 'credit card'"),
    ("Info", "Application 'Zoom' started."),
    ("Info", "VPN connection detected and logged."),
]

def seed():
    os.makedirs("data", exist_ok=True)
    
    timestamp = datetime.datetime.now()
    
    with open(LOG_FILE, "a") as f:
        for i in range(20):
            # Backdate entries slightly
            t = timestamp - datetime.timedelta(minutes=random.randint(1, 120))
            ts_str = t.strftime("%Y-%m-%d %H:%M:%S")
            category, msg = random.choice(ACTIVITIES)
            f.write(f"[{ts_str}] {category}: {msg}\n")
            
    print(f"Success: Seeded 20 demo entries into {LOG_FILE}")

if __name__ == "__main__":
    seed()
