from datetime import date

from pydantic import BaseModel, Field


class ItemResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    category: str
    description: str
    image_url: str | None
    location: str
    date_lost_found: date
    status: str
    admin_verified: bool

    class Config:
        from_attributes = True