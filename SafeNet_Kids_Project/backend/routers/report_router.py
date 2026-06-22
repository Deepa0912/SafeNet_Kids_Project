"""
backend/routers/report_router.py — PDF Report Generation Service
"""
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from ..database import get_db, Child, ThreatLog, ActivityLog, RiskScore
from ..auth import get_current_parent, Parent

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/{child_id}")
def generate_report(
    child_id: int,
    period: str = "weekly",   # daily | weekly | monthly
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == child_id, Child.parent_id == parent.id).first()
    if not child:
        from fastapi import HTTPException
        raise HTTPException(404, "Child not found.")

    # Date range
    now = datetime.utcnow()
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
    since = now - timedelta(days=days)

    threats  = db.query(ThreatLog).filter(ThreatLog.child_id == child_id, ThreatLog.timestamp >= since).all()
    activity = db.query(ActivityLog).filter(ActivityLog.child_id == child_id, ActivityLog.timestamp >= since).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    risk     = db.query(RiskScore).filter(RiskScore.child_id == child_id).order_by(RiskScore.timestamp.desc()).first()

    # Build PDF
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle("Title", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor("#00d4ff"), spaceAfter=4)
    sub_style   = ParagraphStyle("Sub",   parent=styles["Normal"],   alignment=TA_CENTER, fontSize=10, textColor=colors.grey, spaceAfter=12)
    h2_style    = ParagraphStyle("H2",    parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#1a1a2e"), spaceBefore=12, spaceAfter=6)

    # Header
    story.append(Paragraph("🛡️ SafeNet Kids — Safety Report", title_style))
    story.append(Paragraph(f"Child: {child.name} | Period: {period.capitalize()} | Generated: {now.strftime('%Y-%m-%d %H:%M')} UTC", sub_style))
    story.append(Spacer(1, 0.3*cm))

    # Summary
    cat_counts = {}
    for t in threats:
        cat_counts[t.threat_type] = cat_counts.get(t.threat_type, 0) + 1

    summary_data = [
        ["Metric", "Value"],
        ["Total Threats Detected", str(len(threats))],
        ["Current Risk Score",    str(round(risk.score if risk else 0))],
        ["Period",                f"Last {days} day(s)"],
    ]
    for cat, cnt in cat_counts.items():
        summary_data.append([f"  {cat}", str(cnt)])

    story.append(Paragraph("Summary", h2_style))
    t_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d1117")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("PADDING",    (0, 0), (-1, -1), 6),
    ])
    tbl = Table(summary_data, colWidths=[10*cm, 5*cm])
    tbl.setStyle(t_style)
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))

    # Threat details
    if threats:
        story.append(Paragraph("Threat Incidents", h2_style))
        threat_data = [["#", "Type", "Source", "Confidence", "Timestamp"]]
        for i, t in enumerate(threats[:30], 1):
            threat_data.append([
                str(i), t.threat_type, t.source,
                f"{int(t.confidence*100)}%",
                t.timestamp.strftime("%m-%d %H:%M")
            ])
        tbl2 = Table(threat_data, colWidths=[1*cm, 5*cm, 3*cm, 2.5*cm, 3.5*cm])
        tbl2.setStyle(t_style)
        story.append(tbl2)

    doc.build(story)
    buf.seek(0)
    filename = f"safenet_{child.name.lower()}_{period}_{now.strftime('%Y%m%d')}.pdf"
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})
