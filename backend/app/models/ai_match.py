from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    String,
    Text,
)

from sqlalchemy.sql import func

from app.database import Base


class AIMatch(Base):
    __tablename__ = "ai_matches"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Newly uploaded/current item
    item_id = Column(
        Integer,
        ForeignKey("items.id"),
        nullable=False,
    )

    # Existing item that AI matched against
    matched_item_id = Column(
        Integer,
        ForeignKey("items.id"),
        nullable=False,
    )

    # CLIP similarity score
    similarity_score = Column(
        Float,
        nullable=False,
    )

    # pending / notified / dismissed
    status = Column(
        String(30),
        default="notified",
        nullable=False,
    )

    # Optional explanation
    match_reason = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )