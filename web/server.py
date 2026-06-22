"""
web/server.py — SafeNet Kids Flask Web Server
Exposes the backend via a REST API and serves the static dashboard HTML.
Run standalone: python web/server.py
Or launched from main.py with --web flag.
"""
import sys
import os
import json
import re
import logging
from datetime import datetime, timedelta
from functools import wraps

# Allow imports from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

# ── SafeNet Core Imports ──────────────────────────────────────────────────────
from core.auth_manager import AuthManager
from core.process_manager import ProcessManager
from core.monitor import SafeNetMonitor

# ── App Setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
    static_url_path="/static",
)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# ── Backend Singletons ────────────────────────────────────────────────────────
os.chdir(BASE_DIR)  # Ensure relative paths (data/, assets/) resolve correctly

for folder in ["data", "assets"]:
    os.makedirs(folder, exist_ok=True)

if not os.path.exists("data/safenet_audit.log"):
    open("data/safenet_audit.log", "w").close()

auth_manager    = AuthManager()
process_manager = ProcessManager()
monitor         = SafeNetMonitor(
    "data/threat_database.json",
    "data/safenet_audit.log",
    process_manager,
)

# ── Auth Decorator ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    success, msg = auth_manager.login(username, password)
    if not success:
        return jsonify({"error": msg}), 401

    session["username"] = username
    display = auth_manager.get_display_name(username)
    return jsonify({"status": "ok", "username": username, "display_name": display})


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def api_logout():
    session.clear()
    return jsonify({"status": "ok"})


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username       = data.get("username", "")
    password       = data.get("password", "")
    parent_password = data.get("parent_password", "")
    success, msg   = auth_manager.register(username, password, parent_password)
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"status": "ok"})


@app.route("/api/auth/reset_password", methods=["POST"])
def api_reset_password():
    """Reset login password using the parent/admin password as verification."""
    data = request.get_json(silent=True) or {}
    username        = data.get("username", "").strip()
    parent_password = data.get("parent_password", "")
    new_password    = data.get("new_password", "")

    if not username or not parent_password or not new_password:
        return jsonify({"error": "Username, parent password, and new password are required."}), 400
    if len(new_password) < 4:
        return jsonify({"error": "New password must be at least 4 characters."}), 400

    if not auth_manager.username_exists(username):
        return jsonify({"error": "Username not found."}), 404

    if not auth_manager.verify_parent_password(username, parent_password):
        return jsonify({"error": "Incorrect parent/admin password."}), 401

    # Reset the password using internal helpers
    import hashlib, secrets
    auth_manager._load()
    key  = username.lower()
    salt = secrets.token_hex(16)
    auth_manager._users[key]["salt"] = salt
    auth_manager._users[key]["hashed_password"] = hashlib.sha256(
        (salt + new_password).encode()
    ).hexdigest()
    auth_manager._save()

    return jsonify({"status": "ok", "message": "Password reset successfully. You can now sign in."})



@app.route("/api/auth/me")
def api_me():
    if "username" in session:
        return jsonify({
            "logged_in": True,
            "username": session["username"],
            "display_name": auth_manager.get_display_name(session["username"]),
        })
    return jsonify({"logged_in": False})


@app.route("/api/auth/verify_parent", methods=["POST"])
@login_required
def api_verify_parent():
    """Verify the parent/admin password for the currently logged-in user.
    Used to gate all write actions in the web dashboard."""
    data            = request.get_json(silent=True) or {}
    parent_password = data.get("parent_password", "")
    username        = session["username"]

    if not parent_password:
        return jsonify({"error": "Parent password required."}), 400

    if not auth_manager.verify_parent_password(username, parent_password):
        return jsonify({"error": "Incorrect parent/admin password."}), 401

    return jsonify({"status": "ok", "verified": True})


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_log_lines(n=200):
    """Return the last `n` log lines as a list of dicts."""
    log_path = "data/safenet_audit.log"
    results = []
    if not os.path.exists(log_path):
        return results
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-n:]
        pattern = re.compile(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - (\w+) - (.*)"
        )
        for line in lines:
            m = pattern.match(line.strip())
            if m:
                results.append({
                    "timestamp": m.group(1),
                    "level":     m.group(2),
                    "message":   m.group(3),
                })
    except Exception:
        pass
    return results


@app.route("/api/stats")
@login_required
def api_stats():
    risk_score  = monitor.risk_engine.calculate_score()
    risk_label  = monitor.risk_engine.get_category(risk_score)
    log_lines   = _parse_log_lines(500)

    # Count by category in last 7 days
    week_ago    = datetime.now() - timedelta(days=7)
    cat_counts  = {}
    total_threats = 0
    for entry in log_lines:
        try:
            ts = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if ts < week_ago:
            continue
        msg = entry["message"]
        if "Threat:" in msg or "AI Detected" in msg or "Panic Lock" in msg:
            total_threats += 1
            # Extract category
            for cat in ["Self-Harm", "Adult Content", "Violence", "Cyberbullying",
                        "Drugs", "Gambling", "Illegal", "Screen Threat", "Restricted"]:
                if cat.lower() in msg.lower():
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
                    break

    return jsonify({
        "risk_score":    risk_score,
        "risk_label":    risk_label,
        "total_threats": total_threats,
        "monitor_running": monitor.is_running,
        "category_counts": cat_counts,
        "blocked_sites_count": len(monitor.blocked_sites),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVITY LOGS
# ═════════════════════════════════════════════════════════════════════════════

@app.route("/api/logs")
@login_required
def api_logs():
    limit = int(request.args.get("limit", 100))
    entries = _parse_log_lines(limit)
    entries.reverse()  # newest first
    return jsonify(entries)


# ═══════════════════════════════════════════════════════════════════════════════
# THREAT DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/database")
@login_required
def api_database():
    db_path = "data/threat_database.json"
    if not os.path.exists(db_path):
        return jsonify({"categories": {}, "blocked_sites": [], "blocked_apps": []})
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/api/database/blocked_sites", methods=["POST"])
@login_required
def api_add_blocked_site():
    data = request.get_json(silent=True) or {}
    site = data.get("site", "").strip()
    if not site:
        return jsonify({"error": "Site required"}), 400
    db_path = "data/threat_database.json"
    db = {}
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db = json.load(f)
    db.setdefault("blocked_sites", [])
    if site not in db["blocked_sites"]:
        db["blocked_sites"].append(site)
        with open(db_path, "w") as f:
            json.dump(db, f, indent=2)
        monitor.reload_database()
    return jsonify({"status": "ok", "blocked_sites": db["blocked_sites"]})


@app.route("/api/database/blocked_sites/<site>", methods=["DELETE"])
@login_required
def api_remove_blocked_site(site):
    db_path = "data/threat_database.json"
    if not os.path.exists(db_path):
        return jsonify({"error": "No database"}), 404
    with open(db_path, "r") as f:
        db = json.load(f)
    db["blocked_sites"] = [s for s in db.get("blocked_sites", []) if s != site]
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)
    monitor.reload_database()
    return jsonify({"status": "ok", "blocked_sites": db["blocked_sites"]})


# ═══════════════════════════════════════════════════════════════════════════════
# MONITOR CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/monitor/start", methods=["POST"])
@login_required
def api_monitor_start():
    if not monitor.is_running:
        monitor.start()
    return jsonify({"status": "running"})


@app.route("/api/monitor/stop", methods=["POST"])
@login_required
def api_monitor_stop():
    if monitor.is_running:
        monitor.stop()
    return jsonify({"status": "stopped"})


# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKED APPS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/blocked_apps", methods=["GET"])
@login_required
def api_get_blocked_apps():
    return jsonify({"blocked_apps": process_manager.blocked_processes})


@app.route("/api/blocked_apps", methods=["POST"])
@login_required
def api_add_blocked_app():
    data = request.get_json(silent=True) or {}
    app_name = data.get("app", "").strip().lower()
    if not app_name:
        return jsonify({"error": "App name required"}), 400
    if app_name not in process_manager.blocked_processes:
        process_manager.blocked_processes.append(app_name)
        _save_blocked_apps()
    return jsonify({"status": "ok", "blocked_apps": process_manager.blocked_processes})


@app.route("/api/blocked_apps/<app_name>", methods=["DELETE"])
@login_required
def api_remove_blocked_app(app_name):
    app_name = app_name.lower()
    process_manager.blocked_processes = [
        a for a in process_manager.blocked_processes if a != app_name
    ]
    _save_blocked_apps()
    return jsonify({"status": "ok", "blocked_apps": process_manager.blocked_processes})


def _save_blocked_apps():
    db_path = "data/threat_database.json"
    db = {}
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db = json.load(f)
    db["blocked_apps"] = process_manager.blocked_processes
    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)
    monitor.reload_database()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import webbrowser, threading
    port = 5000
    print(f"\n[SafeNet Kids] Web Dashboard starting on port {port}")
    print(f"   Open in browser: http://localhost:{port}")
    print("   Press Ctrl+C to stop.\n")
    # Auto-open browser after 1 second
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=False)
