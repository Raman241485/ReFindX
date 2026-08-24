from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os

from app.database import SessionLocal
from app.models.user import User
from app.websocket_manager import manager


router = APIRouter(
    tags=["Realtime"],
)


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "refindx_super_secret_key_2026_change_this",
)

ALGORITHM = "HS256"


def get_user_from_token(token: str):
    """
    Validate JWT token and return user ID.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("user_id")

        if user_id is None:
            return None

        return int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):
        return None


@router.websocket("/ws/notifications")
async def notification_websocket(
    websocket: WebSocket,
):
    db: Session = SessionLocal()

    user_id = None

    try:
        await websocket.accept()

        auth_data = await websocket.receive_json()

        token = auth_data.get("token")

        if not token:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication token required",
            })

            await websocket.close(code=1008)
            return

        user_id = get_user_from_token(token)

        if user_id is None:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid authentication token",
            })

            await websocket.close(code=1008)
            return

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            await websocket.send_json({
                "type": "error",
                "message": "User not found",
            })

            await websocket.close(code=1008)
            return

        # Use manager method
        manager.active_connections[user_id] = websocket

        await websocket.send_json({
            "type": "connection",
            "message": "Real-time notifications connected",
            "user_id": user_id,
        })

        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong"
                })

    except WebSocketDisconnect:

        if user_id is not None:
            manager.disconnect(user_id)

    except Exception as error:

        print(
            f"WebSocket error for user {user_id}: {error}"
        )

        if user_id is not None:
            manager.disconnect(user_id)

    finally:

        db.close()

        if user_id is not None:
            manager.disconnect(user_id)