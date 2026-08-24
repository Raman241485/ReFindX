from datetime import datetime

from pydantic import BaseModel


class ClaimResponse(BaseModel):
    id: int
    item_id: int
    claimant_id: int
    proof: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True