from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)

from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__ = "users"


    # ========================================================
    # BASIC USER INFORMATION
    # ========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="user",
        nullable=False
    )

    profile_image = Column(
        String(500),
        nullable=True
    )


    # ========================================================
    # EMAIL OTP VERIFICATION
    # ========================================================

    email_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    otp_code = Column(
        String(6),
        nullable=True
    )

    otp_expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


    # ========================================================
    # CREATED AT
    # ========================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )