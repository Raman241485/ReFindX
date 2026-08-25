import os
import uuid
from datetime import date
from typing import Optional

import cloudinary
import cloudinary.uploader

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

from app.utils.cloudinary_config import cloudinary


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/items",
    tags=["Items"],
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


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

    # ========================================================
    # CLEAN INPUT
    # ========================================================

    type = type.strip().lower()
    title = title.strip()
    category = category.strip()
    description = description.strip()
    location = location.strip()


    # ========================================================
    # VALIDATE TYPE
    # ========================================================

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


    # ========================================================
    # VALIDATE REQUIRED FIELDS
    # ========================================================

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


    # ========================================================
    # VALIDATE IMAGE TYPE
    # ========================================================

    if image.content_type not in ALLOWED_IMAGE_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed"
            ),
        )


    # ========================================================
    # READ IMAGE
    # ========================================================

    image_data = await image.read()


    # ========================================================
    # VALIDATE IMAGE SIZE
    # ========================================================

    if len(image_data) > MAX_IMAGE_SIZE:

        raise HTTPException(
            status_code=400,
            detail=(
                "Image size must be less than 5 MB"
            ),
        )


    if len(image_data) == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )


    # ========================================================
    # VALIDATE EXTENSION
    # ========================================================

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


    # ========================================================
    # CLOUDINARY PUBLIC ID
    # ========================================================

    public_id = (
        f"refindx/items/"
        f"{uuid.uuid4().hex}"
    )


    # ========================================================
    # UPLOAD IMAGE TO CLOUDINARY
    # ========================================================

    image_url = None

    try:

        upload_result = (
            cloudinary.uploader.upload(
                image_data,

                public_id=public_id,

                resource_type="image",

                overwrite=False,
            )
        )


        image_url = upload_result.get(
            "secure_url"
        )


        if not image_url:

            raise Exception(
                "Cloudinary did not return "
                "a secure image URL."
            )


    except Exception as error:

        print(
            "CLOUDINARY UPLOAD ERROR:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not upload image. "
                "Please try again."
            ),
        )


    # ========================================================
    # CREATE DATABASE ITEM
    # ========================================================

    try:

        new_item = Item(

            user_id=current_user.id,

            type=type,

            title=title,

            category=category,

            description=description,

            image_url=image_url,

            location=location,

            date_lost_found=date_lost_found,

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


        # ----------------------------------------------------
        # Try to remove Cloudinary image if DB creation fails
        # ----------------------------------------------------

        try:

            cloudinary.uploader.destroy(
                public_id,
                resource_type="image",
            )

        except Exception as cleanup_error:

            print(
                "CLOUDINARY CLEANUP ERROR:",
                cleanup_error,
            )


        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not create item: {error}"
            ),
        )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "message":
            "Item submitted successfully",

        "item": {

            "id":
                new_item.id,

            "user_id":
                new_item.user_id,

            "type":
                new_item.type,

            "title":
                new_item.title,

            "category":
                new_item.category,

            "description":
                new_item.description,

            "image_url":
                new_item.image_url,

            "location":
                new_item.location,

            "date_lost_found":
                new_item.date_lost_found,

            "status":
                new_item.status,

            "admin_verified":
                new_item.admin_verified,
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

    query = (
        db.query(Item)
        .filter(
            Item.admin_verified == True,
            Item.status != "returned",
        )
    )


    # ========================================================
    # SEARCH
    # ========================================================

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


    # ========================================================
    # CATEGORY
    # ========================================================

    if category:

        category = category.strip()


        if category:

            query = query.filter(
                Item.category.ilike(
                    category
                )
            )


    # ========================================================
    # TYPE
    # ========================================================

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


    # ========================================================
    # LOCATION
    # ========================================================

    if location:

        location = location.strip()


        if location:

            query = query.filter(
                Item.location.ilike(
                    f"%{location}%"
                )
            )


    # ========================================================
    # LATEST FIRST
    # ========================================================

    items = (
        query
        .order_by(
            Item.created_at.desc()
        )
        .all()
    )


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

    item = (
        db.query(Item)
        .filter(
            Item.id == item_id,

            Item.admin_verified == True,

            Item.status != "returned",
        )
        .first()
    )


    if not item:

        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )


    return item


# ============================================================
# ADMIN DELETE ITEM
# ============================================================

@router.delete("/{item_id}")
def delete_item(

    item_id: int,

    current_admin: User = Depends(
        get_current_admin
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
    # DELETE CLOUDINARY IMAGE
    # ========================================================

    if item.image_url:

        try:

            image_url = item.image_url

            # Example:
            # https://res.cloudinary.com/
            # cloud/image/upload/v123/
            # refindx/items/abc.jpg

            if (
                "res.cloudinary.com"
                in image_url
                and "/upload/" in image_url
            ):

                cloudinary_path = (
                    image_url.split(
                        "/upload/",
                        1,
                    )[1]
                )


                # Remove version segment:
                # v123456789/
                parts = (
                    cloudinary_path
                    .split("/")
                )


                if (
                    parts
                    and parts[0].startswith("v")
                    and parts[0][1:].isdigit()
                ):

                    parts = parts[1:]


                public_id_with_extension = (
                    "/".join(parts)
                )


                public_id_to_delete = (
                    os.path.splitext(
                        public_id_with_extension
                    )[0]
                )


                cloudinary.uploader.destroy(

                    public_id_to_delete,

                    resource_type="image",
                )


        except Exception as error:

            print(
                "CLOUDINARY DELETE ERROR:",
                error,
            )


    # ========================================================
    # DELETE DATABASE ITEM
    # ========================================================

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


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "message":
            "Item deleted successfully",

        "item_id":
            item_id,

        "deleted_by": {

            "admin_id":
                current_admin.id,

            "admin_name":
                current_admin.name,
        },
    }