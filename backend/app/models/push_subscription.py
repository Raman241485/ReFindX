from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from app.database import Base


class PushSubscription(Base):

    __tablename__ = "push_subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    endpoint = Column(
        String(1000),
        nullable=False,
        unique=True,
    )

    p256dh = Column(
        String(500),
        nullable=False,
    )

    auth = Column(
        String(500),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )