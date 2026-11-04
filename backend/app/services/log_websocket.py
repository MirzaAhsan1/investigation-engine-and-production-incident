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
        print(f"[LOG WS MANAGER] Client connected. Total active connections: {len(self.connections)}")
        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
            print(f"[LOG WS MANAGER] Client disconnected. Total active connections: {len(self.connections)}")

    async def broadcast(self, log_data: dict):
        disconnected = []
        print(f"[LOG WS MANAGER] Broadcasting log to {len(self.connections)} active connection(s)...")
        for websocket in list(self.connections):
            try:
                await websocket.send_json(log_data)
            except Exception as exc:
                print(f"[LOG WS MANAGER] Failed to send payload to websocket: {exc}")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

    def broadcast_sync(self, log_data_list: list[dict]):
        """
        Thread-safe sync bridge to broadcast log payloads to WebSocket clients
        from synchronous API request handlers across threads.
        """
        print(f"[LOG WS MANAGER] broadcast_sync called with {len(log_data_list)} log item(s). Active connections: {len(self.connections)}")
        if not self.connections or not log_data_list:
            return

        async def _do_broadcast():
            for data in log_data_list:
                await self.broadcast(data)

        if self.main_loop and self.main_loop.is_running() and not self.main_loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(_do_broadcast(), self.main_loop)
                return
            except Exception as e:
                print(f"[WebSocket Broadcast Warning] Threadsafe dispatch failed: {e}")

        try:
            running_loop = asyncio.get_running_loop()
            if running_loop.is_running():
                running_loop.create_task(_do_broadcast())
        except RuntimeError:
            try:
                asyncio.run(_do_broadcast())
            except Exception as e:
                print(f"[WebSocket Broadcast Warning] Asyncio run failed: {e}")



log_ws_manager = LogWebSocketManager()