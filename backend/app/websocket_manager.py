from typing import Dict

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[
            int,
            WebSocket,
        ] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        # Close old connection if same user
        old_websocket = (
            self.active_connections.get(
                user_id
            )
        )

        if old_websocket:
            try:
                await old_websocket.close()
            except Exception:
                pass

        self.active_connections[
            user_id
        ] = websocket

    def disconnect(
        self,
        user_id: int,
    ):
        self.active_connections.pop(
            user_id,
            None,
        )

    async def send_to_user(
        self,
        user_id: int,
        message: dict,
    ):
        websocket = (
            self.active_connections.get(
                user_id
            )
        )

        if not websocket:
            return

        try:
            await websocket.send_json(
                message
            )

        except Exception:
            self.disconnect(
                user_id
            )


manager = ConnectionManager()