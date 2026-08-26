from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.push_subscription import PushSubscription
from app.models.user import User
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/push",
    tags=["Push Notifications"],
)


# ============================================================
# PUSH SUBSCRIPTION SCHEMA
# ============================================================

class PushSubscriptionData(BaseModel):

    endpoint: str
    p256dh: str
    auth: str


# ============================================================
# SAVE / UPDATE PUSH SUBSCRIPTION
# ============================================================

@router.post("/subscribe")
def subscribe_push(
    data: PushSubscriptionData,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    existing = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.endpoint == data.endpoint
        )
        .first()
    )


    # --------------------------------------------------------
    # EXISTING SUBSCRIPTION
    # --------------------------------------------------------

    if existing:

        existing.user_id = current_user.id
        existing.p256dh = data.p256dh
        existing.auth = data.auth

        db.commit()
        db.refresh(existing)

        return {
            "message": "Push subscription updated",
            "subscription_id": existing.id,
        }


    # --------------------------------------------------------
    # NEW SUBSCRIPTION
    # --------------------------------------------------------

    subscription = PushSubscription(
        user_id=current_user.id,
        endpoint=data.endpoint,
        p256dh=data.p256dh,
        auth=data.auth,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)


    return {
        "message": "Push subscription saved",
        "subscription_id": subscription.id,
    }


# ============================================================
# REMOVE PUSH SUBSCRIPTION
# ============================================================

@router.delete("/unsubscribe")
def unsubscribe_push(
    data: PushSubscriptionData,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    subscription = (
        db.query(PushSubscription)
        .filter(
            PushSubscription.endpoint == data.endpoint,
            PushSubscription.user_id == current_user.id,
        )
        .first()
    )


    if not subscription:

        raise HTTPException(
            status_code=404,
            detail="Push subscription not found",
        )


    db.delete(subscription)
    db.commit()


    return {
        "message": "Push subscription removed",
    }