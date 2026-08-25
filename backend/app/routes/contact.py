from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/contact",
    tags=["Contact"],
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class ContactOwnerRequest(BaseModel):
    message: str


# ============================================================
# CONTACT ITEM OWNER
# ============================================================

@router.post("/item/{item_id}")
async def contact_item_owner(
    item_id: int,
    data: ContactOwnerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # ========================================================
    # FIND ITEM
    # ========================================================

    item = (
        db.query(Item)
        .filter(Item.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    # ========================================================
    # PREVENT SELF CONTACT
    # ========================================================

    if item.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot contact yourself about your own item.",
        )

    # ========================================================
    # FIND ITEM OWNER / FINDER
    # ========================================================

    owner = (
        db.query(User)
        .filter(User.id == item.user_id)
        .first()
    )

    if not owner:
        raise HTTPException(
            status_code=404,
            detail="Item owner not found",
        )

    # ========================================================
    # VALIDATE MESSAGE
    # ========================================================

    message_text = data.message.strip()

    if not message_text:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if len(message_text) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Message cannot exceed 2000 characters.",
        )

    # ========================================================
    # CREATE NOTIFICATION
    # ========================================================

    notification_message = (
        f"{current_user.name} wants to contact you about "
        f"the item '{item.title}'.\n\n"
        f"Message:\n{message_text}"
    )

    notification = Notification(
        user_id=owner.id,
        item_id=item.id,
        message=notification_message,
        is_read=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": "Message sent successfully.",
        "item_id": item.id,
        "owner_id": owner.id,
        "notification_id": notification.id,
    }