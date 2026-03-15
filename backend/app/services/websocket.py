import json
import logging
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections per project room.
    Uses Redis pub/sub to broadcast events across multiple server instances.
    """

    def __init__(self):
        # project_id -> list of active WebSocket connections
        self._rooms: dict[str, list[WebSocket]] = {}
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def connect(self, websocket: WebSocket, project_id: UUID) -> None:
        room = str(project_id)
        self._rooms.setdefault(room, []).append(websocket)
        logger.debug("WS connected to room %s (total: %d)", room, len(self._rooms[room]))

    async def disconnect(self, websocket: WebSocket, project_id: UUID) -> None:
        room = str(project_id)
        if room in self._rooms:
            self._rooms[room] = [ws for ws in self._rooms[room] if ws is not websocket]
            if not self._rooms[room]:
                del self._rooms[room]

    async def broadcast(self, project_id: UUID, event: str, data: dict) -> None:
        """Publish an event to a project room via Redis so all instances receive it."""
        redis = await self._get_redis()
        message = json.dumps({"event": event, "data": data})
        await redis.publish(f"project:{project_id}", message)

    async def _send_to_room(self, room: str, message: str) -> None:
        """Deliver a message to all local WebSocket connections in a room."""
        dead: list[WebSocket] = []
        for ws in self._rooms.get(room, []):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._rooms[room] = [c for c in self._rooms[room] if c is not ws]

    async def listen(self) -> None:
        """Subscribe to all project channels and relay messages to local sockets."""
        redis = await self._get_redis()
        pubsub = redis.pubsub()
        await pubsub.psubscribe("project:*")
        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue
            channel: str = message["channel"]
            room = channel.split(":", 1)[1]
            await self._send_to_room(room, message["data"])


manager = ConnectionManager()
