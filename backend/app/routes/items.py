import os
import uuid
from datetime import date
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.utils.dependencies import (
    get_current_user,
    get_current_admin,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/items",
    tags=["Items"],
)


# ============================================================
# IMAGE UPLOAD SETTINGS
# ============================================================

UPLOAD_DIR = "uploads"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


# ============================================================
# CREATE LOST / FOUND ITEM
# ============================================================

@router.post("/create")
async def create_item(
    type: str = Form(...),
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    date_lost_found: date = Form(...),
    image: UploadFile = File(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    # --------------------------------------------------------
    # Clean input
    # --------------------------------------------------------

    type = type.strip().lower()
    title = title.strip()
    category = category.strip()
    description = description.strip()
    location = location.strip()

    # --------------------------------------------------------
    # Validate type
    # --------------------------------------------------------

    if type not in [
        "lost",
        "found",
    ]:

        raise HTTPException(
            status_code=400,
            detail="Type must be either 'lost' or 'found'",
        )

    # --------------------------------------------------------
    # Validate fields
    # --------------------------------------------------------

    if not title:

        raise HTTPException(
            status_code=400,
            detail="Title is required",
        )

    if not category:

        raise HTTPException(
            status_code=400,
            detail="Category is required",
        )

    if not description:

        raise HTTPException(
            status_code=400,
            detail="Description is required",
        )

    if not location:

        raise HTTPException(
            status_code=400,
            detail="Location is required",
        )

    # --------------------------------------------------------
    # Validate image type
    # --------------------------------------------------------

    if image.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed"
            ),
        )

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image_data = await image.read()

    # --------------------------------------------------------
    # Validate image size
    # --------------------------------------------------------

    if len(image_data) > MAX_IMAGE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB",
        )

    if len(image_data) == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    original_filename = (
        image.filename or ""
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Invalid image extension",
        )

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    filename = (
        f"{uuid.uuid4()}"
        f"{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb",
        ) as file:

            file.write(
                image_data
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save image: {error}"
            ),
        )

    # --------------------------------------------------------
    # Create database item
    # --------------------------------------------------------

    try:

        new_item = Item(
            user_id=current_user.id,

            type=type,

            title=title,

            category=category,

            description=description,

            image_url=(
                f"/uploads/{filename}"
            ),

            location=location,

            date_lost_found=(
                date_lost_found
            ),

            status="active",

            admin_verified=False,
        )

        db.add(
            new_item
        )

        db.commit()

        db.refresh(
            new_item
        )

    except Exception as error:

        db.rollback()

        if os.path.exists(
            file_path
        ):

            os.remove(
                file_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not create item: {error}"
            ),
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Item submitted successfully"
        ),

        "item": {
            "id": new_item.id,
            "user_id": new_item.user_id,
            "type": new_item.type,
            "title": new_item.title,
            "category": new_item.category,
            "description": new_item.description,
            "image_url": new_item.image_url,
            "location": new_item.location,
            "date_lost_found": (
                new_item.date_lost_found
            ),
            "status": new_item.status,
            "admin_verified": (
                new_item.admin_verified
            ),
        },
    }


# ============================================================
# PUBLIC ITEMS FEED
# ============================================================

@router.get("/")
def get_items(
    search: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    location: Optional[str] = None,

    db: Session = Depends(
        get_db
    ),
):

    query = db.query(
        Item
    ).filter(
        Item.admin_verified == True,
        Item.status != "returned",
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:

        search = search.strip()

        if search:

            search_term = (
                f"%{search}%"
            )

            query = query.filter(
                or_(
                    Item.title.ilike(
                        search_term
                    ),

                    Item.description.ilike(
                        search_term
                    ),

                    Item.category.ilike(
                        search_term
                    ),

                    Item.location.ilike(
                        search_term
                    ),
                )
            )

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if category:

        category = category.strip()

        if category:

            query = query.filter(
                Item.category.ilike(
                    category
                )
            )

    # --------------------------------------------------------
    # Type
    # --------------------------------------------------------

    if type:

        type = type.strip().lower()

        if type not in [
            "lost",
            "found",
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Type must be either "
                    "'lost' or 'found'"
                ),
            )

        query = query.filter(
            Item.type == type
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    if location:

        location = location.strip()

        if location:

            query = query.filter(
                Item.location.ilike(
                    f"%{location}%"
                )
            )

    # --------------------------------------------------------
    # Latest first
    # --------------------------------------------------------

    items = query.order_by(
        Item.created_at.desc()
    ).all()

    return items


# ============================================================
# GET SINGLE PUBLIC ITEM
# ============================================================

@router.get("/{item_id}")
def get_item(
    item_id: int,

    db: Session = Depends(
        get_db
    ),
):

    item = db.query(
        Item
    ).filter(
        Item.id == item_id,
        Item.admin_verified == True,
        Item.status != "returned",
    ).first()

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return item


# ============================================================
# ADMIN DELETE ITEM
# ============================================================

@router.delete(
    "/{item_id}"
)
def delete_item(
    item_id: int,

    current_admin: User = Depends(
        get_current_admin
    ),

    db: Session = Depends(
        get_db
    ),
):

    # --------------------------------------------------------
    # Find item
    # --------------------------------------------------------

    item = db.query(
        Item
    ).filter(
        Item.id == item_id
    ).first()

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    # --------------------------------------------------------
    # Save image path before deleting DB record
    # --------------------------------------------------------

    image_path = None

    if item.image_url:

        clean_path = (
            item.image_url
            .lstrip("/")
        )

        image_path = clean_path

    # --------------------------------------------------------
    # Delete item
    # --------------------------------------------------------

    try:

        db.delete(
            item
        )

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
    # Delete uploaded image
    # --------------------------------------------------------

    if image_path:

        try:

            if os.path.exists(
                image_path
            ):

                os.remove(
                    image_path
                )

        except Exception as error:

            # Item already deleted from DB.
            # Image cleanup failure should not
            # make the delete request fail.
            print(
                "Could not delete item image:",
                error,
            )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Item deleted successfully"
        ),

        "item_id": item_id,

        "deleted_by": {
            "admin_id": current_admin.id,
            "admin_name": current_admin.name,
        },
    }