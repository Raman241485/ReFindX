from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from app.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    item_id = Column(
        Integer,
        ForeignKey("items.id"),
        nullable=False,
    )

    claimant_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    proof = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )