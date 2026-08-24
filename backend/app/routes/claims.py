from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.claim import Claim
from app.models.item import Item
from app.models.user import User
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/claims",
    tags=["Claims"],
)


# ============================================================
# CREATE CLAIM
# ============================================================

@router.post("/")
def create_claim(
    item_id: int,
    proof: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Submit a claim for a verified item.
    """

    # --------------------------------------------------------
    # Find item
    # --------------------------------------------------------

    item = db.query(Item).filter(
        Item.id == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    # --------------------------------------------------------
    # Item must be admin verified
    # --------------------------------------------------------

    if not item.admin_verified:
        raise HTTPException(
            status_code=400,
            detail="This item has not been verified by admin",
        )

    # --------------------------------------------------------
    # Item must be active
    # --------------------------------------------------------

    if item.status != "active":
        raise HTTPException(
            status_code=400,
            detail="This item is no longer available for claims",
        )

    # --------------------------------------------------------
    # User cannot claim own item
    # --------------------------------------------------------

    if item.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot claim your own item",
        )

    # --------------------------------------------------------
    # Validate proof
    # --------------------------------------------------------

    proof = proof.strip()

    if not proof:
        raise HTTPException(
            status_code=400,
            detail="Proof is required",
        )

    # --------------------------------------------------------
    # Prevent duplicate pending claim
    # --------------------------------------------------------

    existing_claim = db.query(Claim).filter(
        Claim.item_id == item_id,
        Claim.claimant_id == current_user.id,
        Claim.status == "pending",
    ).first()

    if existing_claim:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending claim for this item",
        )

    # --------------------------------------------------------
    # Create claim
    # --------------------------------------------------------

    new_claim = Claim(
        item_id=item_id,
        claimant_id=current_user.id,
        proof=proof,
        status="pending",
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    return {
        "message": "Claim submitted successfully",
        "claim": {
            "id": new_claim.id,
            "item_id": new_claim.item_id,
            "claimant_id": new_claim.claimant_id,
            "proof": new_claim.proof,
            "status": new_claim.status,
            "created_at": new_claim.created_at,
        },
    }


# ============================================================
# MY CLAIMS
# ============================================================

@router.get("/my")
def get_my_claims(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Get claims submitted by current user.
    """

    claims = db.query(Claim).filter(
        Claim.claimant_id == current_user.id
    ).order_by(
        Claim.created_at.desc()
    ).all()

    return claims


# ============================================================
# GET SINGLE CLAIM
# ============================================================

@router.get("/{claim_id}")
def get_claim(
    claim_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    User can view their own claim.
    """

    claim = db.query(Claim).filter(
        Claim.id == claim_id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    if claim.claimant_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this claim",
        )

    return claim