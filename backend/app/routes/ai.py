import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.models.ai_match import AIMatch

from app.utils.dependencies import get_current_user

from app.services.ai_match import (
    get_image_embedding,
    calculate_similarity,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Matching"],
)


# ============================================================
# AI SETTINGS
# ============================================================

MATCH_THRESHOLD = 0.80

MAX_MATCHES = 5


# ============================================================
# IMAGE UPLOAD PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads",
)


# ============================================================
# GET IMAGE PATH
# ============================================================

def get_image_path(
    image_url: str,
):
    """
    Convert:

        /uploads/file.jpg

    into:

        backend/uploads/file.jpg
    """

    if not image_url:
        return None

    filename = os.path.basename(
        image_url
    )

    return os.path.join(
        UPLOAD_DIR,
        filename,
    )


# ============================================================
# AI IMAGE MATCHING
# ============================================================

@router.post(
    "/match/{item_id}"
)
def match_item(
    item_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    """
    Run CLIP image matching for an item.

    Allowed:
        - Item owner
        - Admin

    Matching is performed against:
        - Opposite item type
        - Admin verified items
        - Active items
    """

    # ========================================================
    # FIND CURRENT ITEM
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
    # AUTHORIZATION
    # ========================================================

    is_admin = (
        current_user.role == "admin"
    )


    is_owner = (
        item.user_id ==
        current_user.id
    )


    if not is_admin and not is_owner:

        raise HTTPException(
            status_code=403,
            detail=(
                "You can only run AI matching "
                "on your own item or as an admin."
            ),
        )


    # ========================================================
    # IMAGE CHECK
    # ========================================================

    if not item.image_url:

        raise HTTPException(
            status_code=400,
            detail=(
                "This item does not have an image"
            ),
        )


    current_image_path = (
        get_image_path(
            item.image_url
        )
    )


    if (
        not current_image_path
        or not os.path.exists(
            current_image_path
        )
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Current item image not found"
            ),
        )


    # ========================================================
    # OPPOSITE ITEM TYPE
    # ========================================================

    opposite_type = (
        "found"
        if item.type == "lost"
        else "lost"
    )


    # ========================================================
    # FIND VERIFIED CANDIDATES
    # ========================================================

    candidates = (
        db.query(Item)
        .filter(
            Item.type ==
            opposite_type,

            Item.admin_verified ==
            True,

            Item.status ==
            "active",

            Item.id !=
            item.id,
        )
        .all()
    )


    if not candidates:

        return {
            "message": (
                "No verified opposite-type "
                "items available for matching."
            ),

            "item_id":
                item.id,

            "matches_found":
                0,

            "threshold":
                MATCH_THRESHOLD,

            "matches":
                [],
        }


    # ========================================================
    # CURRENT IMAGE EMBEDDING
    # ========================================================

    try:

        current_embedding = (
            get_image_embedding(
                current_image_path
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not process current image: "
                f"{error}"
            ),
        )


    # ========================================================
    # COMPARE AGAINST CANDIDATES
    # ========================================================

    matches = []


    for candidate in candidates:

        if not candidate.image_url:
            continue


        candidate_path = (
            get_image_path(
                candidate.image_url
            )
        )


        if (
            not candidate_path
            or not os.path.exists(
                candidate_path
            )
        ):
            continue


        try:

            candidate_embedding = (
                get_image_embedding(
                    candidate_path
                )
            )


            similarity = (
                calculate_similarity(
                    current_embedding,
                    candidate_embedding,
                )
            )


        except Exception as error:

            print(
                "AI matching error for "
                f"item {candidate.id}: "
                f"{error}"
            )

            continue


        # ====================================================
        # MATCH THRESHOLD
        # ====================================================

        if (
            similarity >=
            MATCH_THRESHOLD
        ):

            matches.append(
                (
                    candidate,
                    similarity,
                )
            )


    # ========================================================
    # SORT BEST MATCH FIRST
    # ========================================================

    matches.sort(
        key=lambda x: x[1],
        reverse=True,
    )


    matches = matches[
        :MAX_MATCHES
    ]


    # ========================================================
    # SAVE MATCHES + NOTIFICATIONS
    # ========================================================

    response_matches = []


    for candidate, similarity in matches:

        # ----------------------------------------------------
        # CHECK EXISTING MATCH
        # ----------------------------------------------------

        existing_match = (
            db.query(AIMatch)
            .filter(
                AIMatch.item_id ==
                item.id,

                AIMatch.matched_item_id ==
                candidate.id,
            )
            .first()
        )


        # ----------------------------------------------------
        # CREATE NEW MATCH
        # ----------------------------------------------------

        if not existing_match:

            new_match = AIMatch(
                item_id=
                    item.id,

                matched_item_id=
                    candidate.id,

                similarity_score=
                    similarity,

                status=
                    "notified",

                match_reason=(
                    "CLIP detected a potential "
                    "image similarity."
                ),
            )


            db.add(
                new_match
            )


            # =================================================
            # NOTIFY CURRENT ITEM OWNER
            # =================================================

            db.add(
                Notification(
                    user_id=
                        item.user_id,

                    # IMPORTANT:
                    # Open the matched candidate item
                    item_id=
                        candidate.id,

                    message=(
                        "🤖 AI found a "
                        "possible match for "
                        f"your {item.type} item "
                        f"'{item.title}'. "
                        f"Similarity: "
                        f"{similarity * 100:.1f}%."
                    ),

                    is_read=False,
                )
            )


            # =================================================
            # NOTIFY MATCHED ITEM OWNER
            # =================================================

            if (
                candidate.user_id
                != item.user_id
            ):

                db.add(
                    Notification(
                        user_id=
                            candidate.user_id,

                        # IMPORTANT:
                        # Open the original/current item
                        item_id=
                            item.id,

                        message=(
                            "🤖 AI found a "
                            "possible match "
                            f"between your item "
                            f"'{candidate.title}' "
                            "and another "
                            "ReFindX item. "
                            f"Similarity: "
                            f"{similarity * 100:.1f}%."
                        ),

                        is_read=False,
                    )
                )


        # ----------------------------------------------------
        # RESPONSE DATA
        # ----------------------------------------------------

        response_matches.append(
            {
                "item_id":
                    item.id,

                "matched_item_id":
                    candidate.id,

                "matched_title":
                    candidate.title,

                "matched_type":
                    candidate.type,

                "similarity_score":
                    round(
                        similarity,
                        4,
                    ),

                "similarity_percentage":
                    round(
                        similarity * 100,
                        2,
                    ),
            }
        )


    # ========================================================
    # SAVE DATABASE CHANGES
    # ========================================================

    db.commit()


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "message":
            "AI matching completed",

        "item_id":
            item.id,

        "matches_found":
            len(
                response_matches
            ),

        "threshold":
            MATCH_THRESHOLD,

        "matches":
            response_matches,
    }