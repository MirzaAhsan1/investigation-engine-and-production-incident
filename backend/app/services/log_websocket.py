import asyncio
from typing import Optional
from fastapi import WebSocket


class LogWebSocketManager:

    def __init__(self):
        self.connections: list[WebSocket] = []
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_main_loop(self, loop: asyncio.AbstractEventLoop):
        """Set reference to FastAPI main event loop."""
        self.main_loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, log_data: dict):
        disconnected = []
        for websocket in self.connections:
            try:
                await websocket.send_json(log_data)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

    def broadcast_sync(self, log_data_list: list[dict]):
        """
        Thread-safe sync bridge to broadcast log payloads to WebSocket clients
        from synchronous API request handlers across threads.
        """
        if not self.connections or not log_data_list:
            return

        async def _do_broadcast():
            for data in log_data_list:
                await self.broadcast(data)

        if self.main_loop and self.main_loop.is_running():
            asyncio.run_coroutine_threadsafe(_do_broadcast(), self.main_loop)
        else:
            try:
                running_loop = asyncio.get_running_loop()
                running_loop.create_task(_do_broadcast())
            except RuntimeError:
                asyncio.run(_do_broadcast())


log_ws_manager = LogWebSocketManager()