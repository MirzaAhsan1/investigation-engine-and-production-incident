import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.log_websocket import log_ws_manager


router = APIRouter()


@router.websocket("/ws/logs")
async def logs_websocket(websocket: WebSocket):

    await log_ws_manager.connect(websocket)

    try:
        # Send initial handshake message so frontend gets instant confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established. Listening for fleet logs."
        })

        while True:
            try:
                # Listen for client frames with a 25-second keep-alive timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Send periodic ping frame to keep connection alive across proxies/firewalls
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:

        log_ws_manager.disconnect(websocket)

    except Exception:

        log_ws_manager.disconnect(websocket)