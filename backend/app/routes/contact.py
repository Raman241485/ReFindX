from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from pydantic import (
    BaseModel,
    EmailStr,
)

from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.utils.dependencies import get_current_user

from app.services.email_service import (
    send_contact_email,
)


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

@router.post(
    "/item/{item_id}"
)
async def contact_item_owner(

    item_id: int,

    data: ContactOwnerRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    # ========================================================
    # FIND ITEM
    # ========================================================

    item = (
        db.query(Item)
        .filter(
            Item.id == item_id
        )
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

    if (
        item.user_id
        == current_user.id
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "You cannot contact yourself "
                "about your own item."
            ),
        )


    # ========================================================
    # FIND ITEM OWNER
    # ========================================================

    owner = (
        db.query(User)
        .filter(
            User.id ==
            item.user_id
        )
        .first()
    )

    if not owner:

        raise HTTPException(
            status_code=404,
            detail="Item owner not found",
        )


    # ========================================================
    # CHECK OWNER EMAIL
    # ========================================================

    if not owner.email:

        raise HTTPException(
            status_code=400,
            detail=(
                "Item owner does not have "
                "a registered email address."
            ),
        )


    # ========================================================
    # VALIDATE MESSAGE
    # ========================================================

    message_text = (
        data.message.strip()
    )

    if not message_text:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )


    if len(message_text) > 2000:

        raise HTTPException(
            status_code=400,
            detail=(
                "Message cannot exceed "
                "2000 characters."
            ),
        )


    # ========================================================
    # SEND EMAIL
    # ========================================================

    try:

        await send_contact_email(

            receiver_email=
                owner.email,

            sender_name=
                current_user.name,

            sender_email=
                current_user.email,

            item_title=
                item.title,

            message_text=
                message_text,
        )

    except Exception as error:

        print(
            "EMAIL ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not send email. "
                "Please try again later."
            ),
        )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "message":
            "Email sent successfully",

        "item_id":
            item.id,

        "owner_id":
            owner.id,
    }