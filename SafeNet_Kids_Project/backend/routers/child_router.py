"""
backend/routers/child_router.py — Child device endpoints (used by monitoring agent)
"""
import os, base64, secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from ..database import get_db, Child, ActivityLog, ThreatLog, Screenshot, Notification, RiskScore, BlockedWebsite, BlockedApplication
from ..ai_service import analyze_text
from ..sockets import notify_parent

router = APIRouter(prefix="/api/child", tags=["child"])


class LinkRequest(BaseModel):
    link_code: str
    device_id: str


@router.post("/link")
def link_device(body: LinkRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.link_code == body.link_code.upper()).first()
    if not child:
        raise HTTPException(404, "Invalid link code.")
    child.device_id = body.device_id
    child.is_online = True
    db.commit()
    return {"status": "linked", "child_id": child.id, "child_name": child.name,
            "parent_id": child.parent_id}


class HeartbeatRequest(BaseModel):
    child_id:  int
    is_online: bool = True


@router.post("/heartbeat")
def heartbeat(body: HeartbeatRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == body.child_id).first()
    if child:
        child.is_online = body.is_online
        db.commit()
    return {"device_locked": child.device_locked if child else False,
            "internet_paused": child.internet_paused if child else False}


class ActivityRequest(BaseModel):
    child_id:  int
    log_type:  str   # website / app / keyboard / search
    value:     str


@router.post("/activity")
async def log_activity(body: ActivityRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == body.child_id).first()
    if not child:
        raise HTTPException(404, "Child not found.")

    # Persist activity
    log = ActivityLog(child_id=body.child_id, log_type=body.log_type, value=body.value)
    db.add(log)
    db.commit()

    # AI Threat Analysis
    result = analyze_text(body.value)
    response = {"is_threat": result.is_threat, "threat_type": result.threat_type,
                "confidence": result.confidence, "child_id": body.child_id}

    if result.is_threat:
        threat = ThreatLog(
            child_id=body.child_id, threat_type=result.threat_type,
            confidence=result.confidence, source_text=body.value[:500],
            source=body.log_type, action_taken="blocked"
        )
        db.add(threat)

        # Notification
        notif = Notification(
            parent_id=child.parent_id, child_id=body.child_id,
            message=f"Threat detected on {child.name}'s device: {result.threat_type} ({int(result.confidence*100)}% confidence)",
            category=result.threat_type,
        )
        db.add(notif)

        # Update risk score
        _update_risk(body.child_id, result.confidence, db)
        db.commit()

        # Real-time notify parent
        await notify_parent(child.parent_id, "threat_alert", {
            "child_id": body.child_id, "child_name": child.name,
            "threat_type": result.threat_type,
            "confidence": round(result.confidence * 100),
            "source": body.log_type, "text": body.value[:200],
            "ts": datetime.utcnow().isoformat(),
        })

    return response


class ScreenshotRequest(BaseModel):
    child_id: int
    image_b64: str
    reason:    Optional[str] = "monitoring"


@router.post("/screenshot")
async def upload_screenshot(body: ScreenshotRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == body.child_id).first()
    if not child:
        raise HTTPException(404)

    filename = f"{body.child_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    path     = os.path.join("data", "screenshots", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(base64.b64decode(body.image_b64))

    ss = Screenshot(child_id=body.child_id, filename=filename, reason=body.reason)
    db.add(ss)
    db.commit()

    await notify_parent(child.parent_id, "new_screenshot", {
        "child_id": body.child_id, "child_name": child.name,
        "filename": filename, "reason": body.reason,
    })
    return {"status": "ok", "filename": filename}


@router.get("/config/{child_id}")
def get_config(child_id: int, db: Session = Depends(get_db)):
    """Agent polls this to get blocked URLs and app list."""
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(404)
    sites = db.query(BlockedWebsite).filter(
        (BlockedWebsite.child_id == child_id) | (BlockedWebsite.child_id.is_(None)),
        BlockedWebsite.parent_id == child.parent_id,
    ).all()
    apps = db.query(BlockedApplication).filter(
        (BlockedApplication.child_id == child_id) | (BlockedApplication.child_id.is_(None)),
        BlockedApplication.parent_id == child.parent_id,
    ).all()
    return {
        "device_locked":    child.device_locked,
        "internet_paused":  child.internet_paused,
        "blocked_urls":     [s.url for s in sites],
        "blocked_apps":     [a.app_name for a in apps],
    }


def _update_risk(child_id: int, threat_confidence: float, db: Session):
    last = db.query(RiskScore).filter(RiskScore.child_id == child_id).order_by(RiskScore.timestamp.desc()).first()
    current = last.score if last else 0
    new_score = min(100, current + threat_confidence * 25)
    db.add(RiskScore(child_id=child_id, score=new_score))
