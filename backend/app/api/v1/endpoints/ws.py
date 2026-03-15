from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError

from app.core.security import decode_token
from app.services.websocket import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: UUID):
    # On accepte la connexion en premier avant tout
    await websocket.accept()

    try:
        token_message = await websocket.receive_json()
        token = token_message.get("token", "")

        decode_token(token)

    except (JWTError, ValueError, Exception):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, project_id)
    await websocket.send_json({"event": "connected", "data": {"project_id": str(project_id)}})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, project_id)