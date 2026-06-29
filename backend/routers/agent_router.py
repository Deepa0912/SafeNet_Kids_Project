"""
backend/routers/agent_router.py — Serves agent files for download
"""
import os, io, zipfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Resolve the agent/ folder relative to this file (backend/routers/ → ../../agent/)
_HERE = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "agent"))

# Files allowed for individual download
ALLOWED_FILES = {
    "monitor.py",
    "requirements.txt",
    "start_child_agent.bat",
    "start_silent.vbs",
    "install_autostart.vbs",
    "stop_monitoring.vbs",
}


@router.get("/download")
def download_agent_zip():
    """Stream the entire agent folder as a ZIP file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ALLOWED_FILES:
            fpath = os.path.join(AGENT_DIR, fname)
            if os.path.isfile(fpath):
                zf.write(fpath, arcname=f"safenet_agent/{fname}")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=safenet_agent.zip"},
    )


@router.get("/file/{filename}")
def download_agent_file(filename: str):
    """Download a single agent file by name."""
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=404, detail="File not found.")
    fpath = os.path.join(AGENT_DIR, filename)
    if not os.path.isfile(fpath):
        raise HTTPException(status_code=404, detail="File not found on server.")
    return FileResponse(
        fpath,
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
