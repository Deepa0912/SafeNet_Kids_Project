"""
backend/email_service.py — Send email alerts to parents via SMTP
Reads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS from environment.
Fails silently if credentials are not configured.
"""
import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def _smtp_ready() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASS)


def send_threat_alert(to_email: str, child_name: str, threat_type: str,
                      confidence: float, source_text: str) -> bool:
    """
    Send a threat alert email to the parent.
    Returns True on success, False on failure / not configured.
    """
    if not _smtp_ready() or not to_email:
        print(f"[Email] SMTP not configured — skipping alert to {to_email}")
        return False
    try:
        subject = f"⚠️ SafeNet Kids Alert — {threat_type} detected on {child_name}'s device"
        html = f"""
        <div style="font-family:Inter,sans-serif;background:#0a0d14;color:#e8f4f8;padding:32px;border-radius:12px;max-width:560px;margin:0 auto">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px">
            <span style="font-size:28px">🛡️</span>
            <div>
              <div style="font-size:20px;font-weight:900;color:#fff">SafeNet Kids</div>
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
            <p style="margin:8px 0 0;font-size:13px;color:#94a3b8">Confidence: {round(confidence*100)}%</p>
          </div>
          <div style="background:#1e2d45;border:1px solid #1f3050;border-radius:12px;padding:16px;margin-bottom:24px">
            <p style="margin:0 0 8px;font-size:13px;color:#94a3b8">DETECTED TEXT (EXCERPT)</p>
            <p style="margin:0;font-size:13px;color:#cbd5e1;font-style:italic">"{source_text[:200]}..."</p>
          </div>
          <p style="font-size:12px;color:#475569;text-align:center">
            {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} · SafeNet Kids Dashboard
          </p>
        </div>
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"SafeNet Kids <{SMTP_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"[Email] Alert sent to {to_email} — {threat_type}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send alert: {e}")
        return False
