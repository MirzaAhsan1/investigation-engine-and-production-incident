from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.log_websocket import log_ws_manager


router = APIRouter()


@router.websocket("/ws/logs")
async def logs_websocket(websocket: WebSocket):

    await log_ws_manager.connect(websocket)

    try:

        while True:

            # Keep connection alive.
            # Frontend se message receive karne ki zarurat nahi.
            await websocket.receive_text()

    except WebSocketDisconnect:

        log_ws_manager.disconnect(websocket)

    except Exception:

        log_ws_manager.disconnect(websocket)