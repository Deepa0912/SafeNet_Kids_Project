"""
backend/routers/parent_router.py — Parent management: children, controls, dashboard
"""
import secrets, os, json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from ..database import (get_db, Parent, Child, ActivityLog, ThreatLog,
                         Screenshot, BlockedWebsite, BlockedApplication,
                         RiskScore, Notification, BedtimeSchedule)
from ..auth import get_current_parent
from ..sockets import notify_parent

router = APIRouter(prefix="/api/parent", tags=["parent"])


# ── Children ────────────────────────────────────────────────────────────────

class AddChildRequest(BaseModel):
    name: str

@router.get("/children")
def list_children(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == parent.id).all()
    return [{"id": c.id, "name": c.name, "link_code": c.link_code,
             "is_online": c.is_online, "device_locked": c.device_locked,
             "internet_paused": c.internet_paused} for c in children]

@router.post("/children")
def add_child(body: AddChildRequest, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = Child(parent_id=parent.id, name=body.name, link_code=secrets.token_hex(6).upper())
    db.add(child); db.commit(); db.refresh(child)
    return {"id": child.id, "name": child.name, "link_code": child.link_code}


# ── Dashboard Stats ──────────────────────────────────────────────────────────

@router.get("/dashboard/{child_id}")
def dashboard(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")
    week_ago = datetime.utcnow() - timedelta(days=7)
    threats  = db.query(ThreatLog).filter(ThreatLog.child_id == child_id, ThreatLog.timestamp >= week_ago).all()
    latest   = db.query(ActivityLog).filter(ActivityLog.child_id == child_id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    risk_rows = db.query(RiskScore).filter(RiskScore.child_id == child_id).order_by(RiskScore.timestamp.desc()).limit(1).first()
    cat_counts = {}
    for t in threats:
        cat_counts[t.threat_type] = cat_counts.get(t.threat_type, 0) + 1
    return {
        "child": {"id": child.id, "name": child.name, "is_online": child.is_online,
                  "device_locked": child.device_locked, "internet_paused": child.internet_paused},
        "risk_score":    round(risk_rows.score if risk_rows else 0),
        "total_threats": len(threats),
        "category_counts": cat_counts,
        "latest_activity": [{"type": a.log_type, "value": a.value,
                              "ts": a.timestamp.isoformat()} for a in latest],
    }


# ── Threat Logs ──────────────────────────────────────────────────────────────

@router.get("/threats/{child_id}")
def threats(child_id: int, limit: int = 100, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    rows = db.query(ThreatLog).filter(ThreatLog.child_id == child_id).order_by(ThreatLog.timestamp.desc()).limit(limit).all()
    return [{"id": r.id, "type": r.threat_type, "confidence": round(r.confidence*100),
             "source": r.source, "text": r.source_text,
             "action": r.action_taken, "ts": r.timestamp.isoformat()} for r in rows]


# ── Screenshots ──────────────────────────────────────────────────────────────

@router.get("/screenshots/{child_id}")
def screenshots(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    rows = db.query(Screenshot).filter(Screenshot.child_id == child_id).order_by(Screenshot.timestamp.desc()).limit(50).all()
    return [{"id": r.id, "filename": r.filename, "reason": r.reason,
             "ts": r.timestamp.isoformat()} for r in rows]

@router.get("/screenshots/file/{filename}")
def screenshot_file(filename: str):
    path = os.path.join("data", "screenshots", filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path)


# ── Control Center ────────────────────────────────────────────────────────────

class ControlRequest(BaseModel):
    action:   str   # "lock" | "unlock" | "pause_internet" | "resume_internet"

@router.post("/control/{child_id}")
async def control(child_id: int, body: ControlRequest,
                  parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")
    if body.action   == "lock":            child.device_locked   = True
    elif body.action == "unlock":          child.device_locked   = False
    elif body.action == "pause_internet":  child.internet_paused = True
    elif body.action == "resume_internet": child.internet_paused = False
    db.commit()
    await notify_parent(parent.id, "control_applied", {"action": body.action, "child_id": child_id})
    return {"status": "ok", "action": body.action}


# ── Blocked Websites ─────────────────────────────────────────────────────────

class BlockSiteRequest(BaseModel):
    url:      str
    child_id: Optional[int] = None
    reason:   Optional[str] = None

@router.get("/blocked-sites")
def get_blocked_sites(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    rows = db.query(BlockedWebsite).filter(BlockedWebsite.parent_id == parent.id).all()
    return [{"id": r.id, "url": r.url, "reason": r.reason} for r in rows]

@router.post("/blocked-sites")
def add_blocked_site(body: BlockSiteRequest, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    row = BlockedWebsite(parent_id=parent.id, child_id=body.child_id, url=body.url.strip(), reason=body.reason)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "url": row.url, "reason": row.reason}

@router.delete("/blocked-sites/{site_id}")
def remove_blocked_site(site_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    row = db.query(BlockedWebsite).filter(BlockedWebsite.id == site_id, BlockedWebsite.parent_id == parent.id).first()
    if not row:
        raise HTTPException(404)
    db.delete(row); db.commit()
    return {"status": "ok"}


# ── Blocked Apps ─────────────────────────────────────────────────────────────

class BlockAppRequest(BaseModel):
    app_name: str
    child_id: Optional[int] = None

@router.get("/blocked-apps")
def get_blocked_apps(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    rows = db.query(BlockedApplication).filter(BlockedApplication.parent_id == parent.id).all()
    return [{"id": r.id, "app_name": r.app_name} for r in rows]

@router.post("/blocked-apps")
def add_blocked_app(body: BlockAppRequest, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    row = BlockedApplication(parent_id=parent.id, child_id=body.child_id, app_name=body.app_name.strip())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "app_name": row.app_name}

@router.delete("/blocked-apps/{app_id}")
def remove_blocked_app(app_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    row = db.query(BlockedApplication).filter(BlockedApplication.id == app_id, BlockedApplication.parent_id == parent.id).first()
    if not row:
        raise HTTPException(404)
    db.delete(row); db.commit()
    return {"status": "ok"}


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications")
def notifications(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter(Notification.parent_id == parent.id).order_by(Notification.timestamp.desc()).limit(50).all()
    return [{"id": r.id, "message": r.message, "category": r.category,
             "is_read": r.is_read, "ts": r.timestamp.isoformat()} for r in rows]

@router.patch("/notifications/{notif_id}/read")
def mark_read(notif_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    row = db.query(Notification).filter(Notification.id == notif_id, Notification.parent_id == parent.id).first()
    if row:
        row.is_read = True; db.commit()
    return {"status": "ok"}


# ── Bedtime Schedule ──────────────────────────────────────────────────────────

class BedtimeRequest(BaseModel):
    enabled:    bool
    sleep_hour: int   # 0-23
    wake_hour:  int   # 0-23

@router.get("/bedtime/{child_id}")
def get_bedtime(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")
    row = db.query(BedtimeSchedule).filter(BedtimeSchedule.child_id == child_id).first()
    if not row:
        return {"enabled": False, "sleep_hour": 22, "wake_hour": 7}
    return {"enabled": row.enabled, "sleep_hour": row.sleep_hour, "wake_hour": row.wake_hour}

@router.put("/bedtime/{child_id}")
def set_bedtime(child_id: int, body: BedtimeRequest,
               parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")
    row = db.query(BedtimeSchedule).filter(BedtimeSchedule.child_id == child_id).first()
    if not row:
        row = BedtimeSchedule(child_id=child_id)
        db.add(row)
    row.enabled    = body.enabled
    row.sleep_hour = body.sleep_hour
    row.wake_hour  = body.wake_hour
    db.commit()
    return {"status": "ok", "enabled": row.enabled, "sleep_hour": row.sleep_hour, "wake_hour": row.wake_hour}


# ── Email Alert Settings ──────────────────────────────────────────────────────

class EmailSettingsRequest(BaseModel):
    alert_email:          Optional[str] = None
    email_alerts_enabled: bool

@router.put("/email-settings")
def update_email_settings(body: EmailSettingsRequest,
                          parent: Parent = Depends(get_current_parent),
                          db: Session = Depends(get_db)):
    parent.alert_email          = body.alert_email
    parent.email_alerts_enabled = body.email_alerts_enabled
    db.commit()
    return {"status": "ok",
            "alert_email": parent.alert_email,
            "email_alerts_enabled": parent.email_alerts_enabled}


@router.get("/email-settings")
def get_email_settings(parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    return {"alert_email": parent.alert_email,
            "email_alerts_enabled": parent.email_alerts_enabled}


# ── Weekly AI Summary ────────────────────────────────────────────────────────

@router.get("/ai-summary/{child_id}")
def get_ai_summary(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Generate a Gemini-powered natural language safety summary for the past 7 days."""
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")

    now = datetime.utcnow()
    since = now - timedelta(days=7)
    threats  = db.query(ThreatLog).filter(ThreatLog.child_id == child_id, ThreatLog.timestamp >= since).all()
    activity = db.query(ActivityLog).filter(ActivityLog.child_id == child_id, ActivityLog.timestamp >= since).count()

    cat_counts = {}
    for t in threats:
        cat_counts[t.threat_type] = cat_counts.get(t.threat_type, 0) + 1

    # Build context for Gemini
    threat_summary = ", ".join(f"{k}: {v}" for k, v in cat_counts.items()) or "none"
    prompt = f"""You are SafeNet Kids, a child safety AI assistant. Write a concise, friendly weekly safety summary for a parent.

Child name: {child.name}
Period: Last 7 days
Total activity events: {activity}
Threats detected: {len(threats)}
Threat breakdown: {threat_summary}

Write 2-3 sentences. Be reassuring if no threats, or cautionary if threats exist. Start with the child's name. Keep it under 60 words."""

    summary = None

    # Try Gemini
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        if GEMINI_API_KEY:
            from google import genai as google_genai
            client = google_genai.Client(api_key=GEMINI_API_KEY)
            resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            summary = resp.text.strip()
    except Exception as e:
        pass

    # Fallback if Gemini unavailable
    if not summary:
        if len(threats) == 0:
            summary = f"{child.name} had a safe week! No threats were detected across {activity} monitored events. Keep up the great parenting!"
        else:
            top = max(cat_counts, key=cat_counts.get)
            summary = f"{child.name}'s week had {len(threats)} threat(s) detected, primarily {top}. Review the Alerts page for details and consider adjusting blocked sites."

    return {"summary": summary, "threat_count": len(threats), "activity_count": activity, "categories": cat_counts}


# ── Screen Time Daily Stats ──────────────────────────────────────────────────

@router.get("/screentime-stats/{child_id}")
def get_screentime_stats(child_id: int, parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    """Return daily activity counts for the last 7 days for the screen time chart."""
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        raise HTTPException(404, "Child not found.")

    now = datetime.utcnow()
    days = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        count = db.query(ActivityLog).filter(
            ActivityLog.child_id == child_id,
            ActivityLog.timestamp >= day_start,
            ActivityLog.timestamp < day_end,
        ).count()
        days.append({"date": day_start.strftime("%a %d"), "count": count})
    return {"days": days}


# ── Password Change ──────────────────────────────────────────────────────────

from ..auth import verify_password, hash_password

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password:     str

@router.put("/change-password")
def change_password(body: PasswordChangeRequest,
                    parent: Parent = Depends(get_current_parent),
                    db: Session = Depends(get_db)):
    if not verify_password(body.current_password, parent.hashed_pw):
        raise HTTPException(400, "Current password is incorrect.")
    if len(body.new_password) < 6:
        raise HTTPException(400, "New password must be at least 6 characters.")
    parent.hashed_pw = hash_password(body.new_password)
    db.commit()
    return {"status": "ok", "message": "Password changed successfully."}
