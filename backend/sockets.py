"""
backend/sockets.py — Socket.IO Server for real-time alerts
"""
import socketio
from typing import Dict, Set

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

# Map parent_id -> set of connected sids
_parent_rooms: Dict[int, Set[str]] = {}


@sio.event
async def connect(sid, environ, auth):
    print(f"[Socket.IO] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    # Remove from all rooms
    for parent_id, sids in list(_parent_rooms.items()):
        sids.discard(sid)
        if not sids:
            del _parent_rooms[parent_id]
    print(f"[Socket.IO] Client disconnected: {sid}")


@sio.event
async def join_parent_room(sid, data):
    """Parent joins their dedicated room to receive child alerts."""
    parent_id = data.get("parent_id")
    if parent_id:
        _parent_rooms.setdefault(int(parent_id), set()).add(sid)
        await sio.enter_room(sid, f"parent_{parent_id}")
        await sio.emit("joined", {"room": f"parent_{parent_id}"}, to=sid)


async def notify_parent(parent_id: int, event: str, data: dict):
    """Broadcast an event to all parent's connected browsers."""
    room = f"parent_{parent_id}"
    await sio.emit(event, data, room=room)
