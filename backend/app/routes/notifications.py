from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


# ============================================================
# GET MY NOTIFICATIONS
# ============================================================

@router.get("/")
def get_notifications(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return notifications


# ============================================================
# UNREAD NOTIFICATIONS COUNT
# ============================================================

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .count()
    )

    return {
        "unread_count": count
    }


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
        "is_read": notification.is_read,
        "item_id": notification.item_id,
    }