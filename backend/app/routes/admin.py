import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User
from app.models.item import Item
from app.models.claim import Claim
from app.models.notification import Notification
from app.models.ai_match import AIMatch

from app.utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


# ============================================================
# ADMIN PROFILE
# ============================================================

@router.get("/me")
def admin_me(
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return {
        "message": "Admin authenticated successfully",

        "admin": {
            "id": current_admin.id,
            "name": current_admin.name,
            "email": current_admin.email,
            "role": current_admin.role,
        },
    }


# ============================================================
# ADMIN DASHBOARD STATISTICS
# ============================================================

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    """
    Return real-time statistics for
    the admin dashboard.
    """

    # --------------------------------------------------------
    # TOTAL USERS
    # --------------------------------------------------------

    total_users = (
        db.query(User)
        .count()
    )


    # --------------------------------------------------------
    # TOTAL ITEMS
    # --------------------------------------------------------

    total_items = (
        db.query(Item)
        .count()
    )


    # --------------------------------------------------------
    # PENDING ITEMS
    # --------------------------------------------------------

    pending_items = (
        db.query(Item)
        .filter(
            Item.admin_verified == False,
            Item.status == "active",
        )
        .count()
    )


    # --------------------------------------------------------
    # TOTAL CLAIMS
    # --------------------------------------------------------

    total_claims = (
        db.query(Claim)
        .count()
    )


    # --------------------------------------------------------
    # PENDING CLAIMS
    # --------------------------------------------------------

    pending_claims = (
        db.query(Claim)
        .filter(
            Claim.status == "pending"
        )
        .count()
    )


    # --------------------------------------------------------
    # TOTAL AI MATCHES
    # --------------------------------------------------------

    ai_matches = (
        db.query(AIMatch)
        .count()
    )


    # --------------------------------------------------------
    # SUCCESSFUL RETURNS
    # --------------------------------------------------------
    # In the current ReFindX flow, an approved claim
    # changes the item status to "claimed".
    #
    # Therefore claimed items are counted as
    # successful returns.

    successful_returns = (
        db.query(Item)
        .filter(
            Item.status == "claimed"
        )
        .count()
    )


    # --------------------------------------------------------
    # LOST ITEMS
    # --------------------------------------------------------

    lost_items = (
        db.query(Item)
        .filter(
            Item.type == "lost"
        )
        .count()
    )


    # --------------------------------------------------------
    # FOUND ITEMS
    # --------------------------------------------------------

    found_items = (
        db.query(Item)
        .filter(
            Item.type == "found"
        )
        .count()
    )


    # --------------------------------------------------------
    # VERIFIED ITEMS
    # --------------------------------------------------------

    verified_items = (
        db.query(Item)
        .filter(
            Item.admin_verified == True
        )
        .count()
    )


    # --------------------------------------------------------
    # REJECTED ITEMS
    # --------------------------------------------------------

    rejected_items = (
        db.query(Item)
        .filter(
            Item.status == "rejected"
        )
        .count()
    )


    # --------------------------------------------------------
    # APPROVED CLAIMS
    # --------------------------------------------------------

    approved_claims = (
        db.query(Claim)
        .filter(
            Claim.status == "approved"
        )
        .count()
    )


    # --------------------------------------------------------
    # REJECTED CLAIMS
    # --------------------------------------------------------

    rejected_claims = (
        db.query(Claim)
        .filter(
            Claim.status == "rejected"
        )
        .count()
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "total_users":
            total_users,

        "total_items":
            total_items,

        "pending_items":
            pending_items,

        "total_claims":
            total_claims,

        "pending_claims":
            pending_claims,

        "ai_matches":
            ai_matches,

        "successful_returns":
            successful_returns,

        # Additional useful statistics

        "lost_items":
            lost_items,

        "found_items":
            found_items,

        "verified_items":
            verified_items,

        "rejected_items":
            rejected_items,

        "approved_claims":
            approved_claims,

        "rejected_claims":
            rejected_claims,
    }


# ============================================================
# PENDING ITEMS
# ============================================================

@router.get("/items/pending")
def get_pending_items(
    db: Session = Depends(get_db),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    items = (
        db.query(Item)
        .filter(
            Item.admin_verified == False,
            Item.status == "active",
        )
        .order_by(
            Item.created_at.desc()
        )
        .all()
    )

    return items


# ============================================================
# VERIFY ITEM
# ============================================================

@router.patch(
    "/items/{item_id}/verify"
)
def verify_item(
    item_id: int,

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
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


    if item.status == "rejected":

        raise HTTPException(
            status_code=400,
            detail=(
                "Rejected item cannot be verified"
            ),
        )


    item.admin_verified = True

    item.status = "active"


    db.commit()

    db.refresh(item)


    return {
        "message":
            "Item verified successfully",

        "item_id":
            item.id,

        "admin_verified":
            item.admin_verified,

        "status":
            item.status,
    }


# ============================================================
# REJECT ITEM
# ============================================================

@router.patch(
    "/items/{item_id}/reject"
)
def reject_item(
    item_id: int,

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
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


    item.admin_verified = False

    item.status = "rejected"


    db.commit()

    db.refresh(item)


    return {
        "message":
            "Item rejected successfully",

        "item_id":
            item.id,

        "admin_verified":
            False,

        "status":
            "rejected",
    }


# ============================================================
# DELETE ITEM - ADMIN ONLY
# ============================================================

@router.delete(
    "/items/{item_id}"
)
def delete_item(
    item_id: int,

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    """
    Permanently delete an item.

    Only authenticated admin can access
    this endpoint.

    Also removes related claims,
    AI matches and uploaded image.
    """

    # --------------------------------------------------------
    # FIND ITEM
    # --------------------------------------------------------

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


    image_url = item.image_url


    # --------------------------------------------------------
    # DELETE CLAIMS
    # --------------------------------------------------------

    db.query(
        Claim
    ).filter(
        Claim.item_id == item.id
    ).delete(
        synchronize_session=False
    )


    # --------------------------------------------------------
    # DELETE AI MATCHES
    # --------------------------------------------------------

    db.query(
        AIMatch
    ).filter(
        AIMatch.item_id == item.id
    ).delete(
        synchronize_session=False
    )


    db.query(
        AIMatch
    ).filter(
        AIMatch.matched_item_id == item.id
    ).delete(
        synchronize_session=False
    )

# --------------------------------------------------------
# DELETE NOTIFICATIONS RELATED TO ITEM
# --------------------------------------------------------

    db.query(
    Notification
        ).filter(
    Notification.item_id == item.id
    ).delete(
    synchronize_session=False
    )
    # --------------------------------------------------------
    # DELETE ITEM
    # --------------------------------------------------------

    try:

        db.delete(item)

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not delete item: {error}"
            ),
        )


    # --------------------------------------------------------
    # DELETE IMAGE
    # --------------------------------------------------------

    if image_url:

        try:

            relative_path = (
                image_url
                .lstrip("/\\")
            )

            image_path = os.path.join(
                relative_path
            )


            if os.path.exists(
                image_path
            ):

                os.remove(
                    image_path
                )

        except Exception as error:

            print(
                "Warning: could not delete image: "
                f"{error}"
            )


    return {
        "message":
            "Item deleted successfully",

        "item_id":
            item_id,
    }


# ============================================================
# PENDING CLAIMS
# ============================================================

@router.get(
    "/claims/pending"
)
def get_pending_claims(
    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    claims = (
        db.query(Claim)
        .filter(
            Claim.status == "pending"
        )
        .order_by(
            Claim.created_at.desc()
        )
        .all()
    )

    return claims


# ============================================================
# APPROVE CLAIM
# ============================================================

@router.patch(
    "/claims/{claim_id}/approve"
)
def approve_claim(
    claim_id: int,

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    claim = (
        db.query(Claim)
        .filter(
            Claim.id == claim_id
        )
        .first()
    )


    if not claim:

        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )


    if claim.status != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                "This claim has already been processed"
            ),
        )


    item = (
        db.query(Item)
        .filter(
            Item.id == claim.item_id
        )
        .first()
    )


    if not item:

        raise HTTPException(
            status_code=404,
            detail=(
                "Item associated with claim "
                "not found"
            ),
        )


    # --------------------------------------------------------
    # APPROVE CLAIM
    # --------------------------------------------------------

    claim.status = "approved"

    item.status = "claimed"


    # --------------------------------------------------------
    # REJECT OTHER CLAIMS
    # --------------------------------------------------------

    other_claims = (
        db.query(Claim)
        .filter(
            Claim.item_id == claim.item_id,

            Claim.id != claim.id,

            Claim.status == "pending",
        )
        .all()
    )


    for other_claim in other_claims:

        other_claim.status = "rejected"


        db.add(
            Notification(
                user_id=
                    other_claim.claimant_id,

                item_id=
                    item.id,

                message=(
                    f"Your claim for "
                    f"'{item.title}' was rejected "
                    "because another claim was "
                    "approved."
                ),

                is_read=False,
            )
        )


    # --------------------------------------------------------
    # NOTIFY APPROVED CLAIMANT
    # --------------------------------------------------------

    db.add(
        Notification(
            user_id=
                claim.claimant_id,

            item_id=
                item.id,

            message=(
                f"Your claim for "
                f"'{item.title}' has been "
                "approved by ReFindX admin."
            ),

            is_read=False,
        )
    )


    # --------------------------------------------------------
    # NOTIFY ITEM OWNER
    # --------------------------------------------------------

    db.add(
        Notification(
            user_id=
                item.user_id,

            item_id=
                item.id,

            message=(
                f"A claim for your item "
                f"'{item.title}' has been "
                "approved."
            ),

            is_read=False,
        )
    )


    db.commit()


    return {
        "message":
            "Claim approved successfully",

        "claim_id":
            claim.id,

        "claim_status":
            claim.status,

        "item_id":
            item.id,

        "item_status":
            item.status,
    }


# ============================================================
# REJECT CLAIM
# ============================================================

@router.patch(
    "/claims/{claim_id}/reject"
)
def reject_claim(
    claim_id: int,

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    claim = (
        db.query(Claim)
        .filter(
            Claim.id == claim_id
        )
        .first()
    )


    if not claim:

        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )


    if claim.status != "pending":

        raise HTTPException(
            status_code=400,
            detail=(
                "This claim has already been processed"
            ),
        )


    item = (
        db.query(Item)
        .filter(
            Item.id == claim.item_id
        )
        .first()
    )


    if not item:

        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )


    claim.status = "rejected"


    db.add(
        Notification(
            user_id=
                claim.claimant_id,

            item_id=
                item.id,

            message=(
                f"Your claim for "
                f"'{item.title}' has been "
                "rejected by ReFindX admin."
            ),

            is_read=False,
        )
    )


    db.commit()


    return {
        "message":
            "Claim rejected successfully",

        "claim_id":
            claim.id,

        "claim_status":
            claim.status,
    }