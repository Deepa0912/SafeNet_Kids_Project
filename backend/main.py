"""
backend/main.py — FastAPI Entry Point
"""
import os
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .database import init_db
from .sockets import sio
from .routers.auth_router   import router as auth_router
from .routers.parent_router import router as parent_router
from .routers.child_router  import router as child_router
from .routers.report_router import router as report_router

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="SafeNet Kids API", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(parent_router)
app.include_router(child_router)
app.include_router(report_router)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

# ── Production Static File Serving ────────────────────────────────────────────
# The React build (npm run build) outputs to frontend-parent/dist
# which is then copied to ./static by the Dockerfile / build script.
# FastAPI serves it so the whole app runs on ONE PORT.

_BASE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.normpath(os.path.join(_BASE, "..", "static"))
INDEX_HTML  = os.path.join(STATIC_DIR, "index.html")


def _index_response() -> FileResponse:
    return FileResponse(INDEX_HTML, media_type="text/html")


if os.path.isfile(INDEX_HTML):
    # Mount /assets so CSS/JS loads with proper cache headers
    _assets = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(_assets):
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    # Mount /icons for any SVG/icon assets
    _icons = os.path.join(STATIC_DIR, "icons.svg")

    @app.get("/")
    async def index_root():
        return _index_response()

    @app.get("/child")
    async def index_child():
        return _index_response()

    @app.get("/child/{rest:path}")
    async def index_child_sub(rest: str):
        return _index_response()

    # Generic SPA fallback for any other unrecognised route
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Don't interfere with /api/* — those are handled by routers above
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return _index_response()
else:
    # Dev mode – no static folder built yet
    @app.get("/")
    def root_dev():
        return {
            "service": "SafeNet Kids API v2",
            "status": "running",
            "note": "Frontend not built. Open http://localhost:3000 for the React dev server.",
        }

# ── Socket.IO ASGI Mount ──────────────────────────────────────────────────────
sio_app = socketio.ASGIApp(sio, app)
