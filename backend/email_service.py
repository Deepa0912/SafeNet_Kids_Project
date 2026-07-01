"""
backend/email_service.py — Send email alerts to parents via SMTP
Reads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM_NAME,
and FRONTEND_URL from environment at call time (supports Railway env vars).
Fails silently if credentials are not configured.
"""
import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def _get_smtp_config() -> dict:
    """Read SMTP settings fresh from env each call — required for Railway/Render."""
    return {
        "host":      os.getenv("SMTP_HOST", ""),
        "port":      int(os.getenv("SMTP_PORT", "587")),
        "user":      os.getenv("SMTP_USER", ""),
        "password":  os.getenv("SMTP_PASS", ""),
        "from_name": os.getenv("SMTP_FROM_NAME", "SafeNet Kids"),
        "app_url":   os.getenv("FRONTEND_URL", "http://localhost:8000"),
    }


def _smtp_ready(cfg: dict) -> bool:
    return bool(cfg["host"] and cfg["user"] and cfg["password"])


def send_threat_alert(to_email: str, child_name: str, threat_type: str,
                      confidence: float, source_text: str) -> bool:
    """
    Send a threat alert email to the parent.
    Returns True on success, False on failure / not configured.
    """
    cfg = _get_smtp_config()
    if not _smtp_ready(cfg) or not to_email:
        print(f"[Email] SMTP not configured — skipping alert to {to_email}")
        return False
    try:
        subject = f"⚠️ SafeNet Kids Alert — {threat_type} detected on {child_name}'s device"
        dashboard_url = cfg["app_url"]
        html = f"""
        <div style="font-family:Inter,sans-serif;background:#0a0d14;color:#e8f4f8;padding:32px;border-radius:12px;max-width:560px;margin:0 auto">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px">
            <span style="font-size:28px">🛡️</span>
            <div>
              <div style="font-size:20px;font-weight:900;color:#fff">{cfg["from_name"]}</div>
              <div style="font-size:13px;color:#00d4ff">Threat Alert</div>
            </div>
          </div>
          <div style="background:#141d2e;border:1px solid #1f3050;border-radius:12px;padding:20px;margin-bottom:16px">
            <p style="margin:0 0 8px;font-size:13px;color:#94a3b8">CHILD</p>
            <p style="margin:0;font-size:16px;font-weight:700;color:#fff">{child_name}</p>
          </div>
          <div style="background:#ff525220;border:1px solid #ff525240;border-radius:12px;padding:20px;margin-bottom:16px">
            <p style="margin:0 0 8px;font-size:13px;color:#94a3b8">THREAT DETECTED</p>
            <p style="margin:0;font-size:18px;font-weight:900;color:#ff5252">{threat_type}</p>
            <p style="margin:8px 0 0;font-size:13px;color:#94a3b8">Confidence: {round(confidence * 100)}%</p>
          </div>
          <div style="background:#1e2d45;border:1px solid #1f3050;border-radius:12px;padding:16px;margin-bottom:24px">
            <p style="margin:0 0 8px;font-size:13px;color:#94a3b8">DETECTED TEXT (EXCERPT)</p>
            <p style="margin:0;font-size:13px;color:#cbd5e1;font-style:italic">"{source_text[:200]}..."</p>
          </div>
          <div style="text-align:center;margin-bottom:24px">
            <a href="{dashboard_url}" style="display:inline-block;background:linear-gradient(135deg,#00d4ff,#7b2ff7);color:#fff;text-decoration:none;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:700;letter-spacing:0.5px">
              View Dashboard →
            </a>
          </div>
          <p style="font-size:12px;color:#475569;text-align:center;margin:0">
            {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} · SafeNet Kids
          </p>
        </div>
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{cfg['from_name']} <{cfg['user']}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"]) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(cfg["user"], cfg["password"])
            s.sendmail(cfg["user"], to_email, msg.as_string())
        print(f"[Email] Alert sent to {to_email} — {threat_type}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send alert: {e}")
        return False
