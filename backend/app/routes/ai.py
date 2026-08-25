import os
import tempfile
from urllib.request import urlopen
from urllib.parse import urlparse

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
    compare_images,
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
# DOWNLOAD CLOUDINARY IMAGE TEMPORARILY
# ============================================================

def download_image(
    image_url: str,
):
    """
    Download an image from Cloudinary or another
    HTTP/HTTPS image URL into a temporary file.

    Returns:
        temporary file path
    """

    if not image_url:
        return None

    parsed = urlparse(image_url)

    if parsed.scheme not in [
        "http",
        "https",
    ]:

        raise ValueError(
            "Invalid image URL."
        )

    # --------------------------------------------------------
    # Determine extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        parsed.path
    )[1].lower()

    if extension not in [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]:

        extension = ".jpg"

    # --------------------------------------------------------
    # Create temporary file
    # --------------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension,
    )

    temp_path = temp_file.name

    temp_file.close()

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:

        with urlopen(
            image_url,
            timeout=30,
        ) as response:

            image_data = response.read()

        with open(
            temp_path,
            "wb",
        ) as file:

            file.write(
                image_data
            )

        return temp_path

    except Exception:

        if os.path.exists(
            temp_path
        ):

            os.remove(
                temp_path
            )

        raise


# ============================================================
# GET IMAGE FOR AI
# ============================================================

def get_ai_image_path(
    image_url: str,
):
    """
    Supports:

    1. Cloudinary HTTPS URL
    2. Existing local /uploads/... URL

    Cloudinary images are downloaded temporarily.
    """

    if not image_url:
        return None

    # --------------------------------------------------------
    # Cloudinary / HTTPS image
    # --------------------------------------------------------

    if image_url.startswith(
        "http://"
    ) or image_url.startswith(
        "https://"
    ):

        return download_image(
            image_url
        )

    # --------------------------------------------------------
    # Legacy local image support
    # --------------------------------------------------------

    if image_url.startswith(
        "/uploads/"
    ):

        filename = os.path.basename(
            image_url
        )

        backend_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(
                        __file__
                    )
                )
            )
        )

        local_path = os.path.join(
            backend_dir,
            "uploads",
            filename,
        )

        if os.path.exists(
            local_path
        ):

            return local_path

    return None


# ============================================================
# DELETE TEMPORARY FILE
# ============================================================

def cleanup_temp_file(
    file_path: str,
):
    """
    Delete temporary Cloudinary download.
    Never raises an exception.
    """

    if not file_path:
        return

    try:

        if os.path.exists(
            file_path
        ):

            os.remove(
                file_path
            )

    except Exception as error:

        print(
            "Temporary image cleanup error:",
            error,
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
    Run AI image matching for an item.

    Supports Cloudinary images.

    Allowed:
        - Item owner
        - Admin

    Matching:
        - Opposite item type
        - Admin verified
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


    # ========================================================
    # GET CURRENT IMAGE
    # ========================================================

    current_image_path = None

    temporary_files = []


    try:

        try:

            current_image_path = (
                get_ai_image_path(
                    item.image_url
                )
            )

        except Exception as error:

            print(
                "Current image download error:",
                error,
            )

            raise HTTPException(
                status_code=404,
                detail=(
                    "Could not download "
                    "current item image."
                ),
            )


        if not current_image_path:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Current item image not found."
                ),
            )


        # ----------------------------------------------------
        # Track temporary Cloudinary file
        # ----------------------------------------------------

        if (
            item.image_url.startswith(
                "http://"
            )
            or item.image_url.startswith(
                "https://"
            )
        ):

            temporary_files.append(
                current_image_path
            )


        # ====================================================
        # OPPOSITE ITEM TYPE
        # ====================================================

        opposite_type = (
            "found"
            if item.type == "lost"
            else "lost"
        )


        # ====================================================
        # FIND VERIFIED CANDIDATES
        # ====================================================

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


        # ====================================================
        # COMPARE AGAINST CANDIDATES
        # ====================================================

        matches = []


        for candidate in candidates:

            # ------------------------------------------------
            # Candidate image check
            # ------------------------------------------------

            if not candidate.image_url:

                continue


            candidate_path = None


            try:

                candidate_path = (
                    get_ai_image_path(
                        candidate.image_url
                    )
                )

            except Exception as error:

                print(
                    "Candidate image download error "
                    f"for item {candidate.id}:",
                    error,
                )

                continue


            if not candidate_path:

                continue


            # ------------------------------------------------
            # Track temporary candidate image
            # ------------------------------------------------

            if (
                candidate.image_url.startswith(
                    "http://"
                )
                or candidate.image_url.startswith(
                    "https://"
                )
            ):

                temporary_files.append(
                    candidate_path
                )


            # ------------------------------------------------
            # Gemini comparison
            # ------------------------------------------------

            try:

                result = compare_images(

                    current_image_path,

                    candidate_path,
                )


                similarity = float(
                    result.get(
                        "similarity_score",
                        0,
                    )
                )


                match_reason = result.get(
                    "reason",
                    "Gemini detected visual similarity.",
                )


            except Exception as error:

                print(
                    "AI matching error for "
                    f"item {candidate.id}: "
                    f"{error}"
                )

                continue


            # ------------------------------------------------
            # Threshold
            # ------------------------------------------------

            if (
                similarity >=
                MATCH_THRESHOLD
            ):

                matches.append(
                    (
                        candidate,
                        similarity,
                        match_reason,
                    )
                )


        # ====================================================
        # SORT BEST MATCH FIRST
        # ====================================================

        matches.sort(
            key=lambda x: x[1],
            reverse=True,
        )


        matches = matches[
            :MAX_MATCHES
        ]


        # ====================================================
        # SAVE MATCHES + NOTIFICATIONS
        # ====================================================

        response_matches = []


        for (
            candidate,
            similarity,
            match_reason,
        ) in matches:

            # ------------------------------------------------
            # CHECK EXISTING MATCH
            # ------------------------------------------------

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


            # ------------------------------------------------
            # CREATE NEW MATCH
            # ------------------------------------------------

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

                    match_reason=
                        match_reason,
                )


                db.add(
                    new_match
                )


                # ============================================
                # NOTIFY CURRENT ITEM OWNER
                # ============================================

                db.add(
                    Notification(

                        user_id=
                            item.user_id,

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


                # ============================================
                # NOTIFY MATCHED ITEM OWNER
                # ============================================

                if (
                    candidate.user_id
                    != item.user_id
                ):

                    db.add(
                        Notification(

                            user_id=
                                candidate.user_id,

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


            # ------------------------------------------------
            # RESPONSE DATA
            # ------------------------------------------------

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

                    "match_reason":
                        match_reason,
                }
            )


        # ====================================================
        # SAVE DATABASE CHANGES
        # ====================================================

        db.commit()


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

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


    finally:

        # ====================================================
        # CLEAN TEMPORARY CLOUDINARY FILES
        # ====================================================

        for temp_file in temporary_files:

            cleanup_temp_file(
                temp_file
            )