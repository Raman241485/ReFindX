from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey
)
from sqlalchemy.sql import func

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        String(10),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    image_url = Column(
        String(500),
        nullable=True
    )

    location = Column(
        String(255),
        nullable=False
    )

    date_lost_found = Column(
        Date,
        nullable=False
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )

    admin_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    ai_embedding = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )