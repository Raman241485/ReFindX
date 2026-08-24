from datetime import datetime, timedelta, timezone
import secrets

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.user import (
    UserSignup,
    UserLogin,
    TokenResponse,
    UserResponse,
    SignupResponse,
    VerifyEmailRequest,
    ResendOTPRequest,
    MessageResponse,
)

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.utils.dependencies import (
    get_current_user,
)

from app.services.email_service import (
    send_password_reset_email,
    send_email_otp,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ============================================================
# PASSWORD RESET TEMPORARY STORAGE
# ============================================================

password_reset_tokens = {}


# ============================================================
# OTP CONFIGURATION
# ============================================================

OTP_EXPIRY_MINUTES = 5


# ============================================================
# HELPER - GENERATE OTP
# ============================================================

def generate_otp():

    return str(
        secrets.randbelow(900000) + 100000
    )


# ============================================================
# SIGNUP
# ============================================================

@router.post(
    "/signup",
    response_model=SignupResponse,
)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db),
):

    email = user_data.email.strip().lower()


    # --------------------------------------------------------
    # CHECK EXISTING USER
    # --------------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if existing_user:

        # ----------------------------------------------------
        # If account exists but email is NOT verified,
        # allow OTP to be sent again.
        # ----------------------------------------------------

        if not existing_user.email_verified:

            otp_code = generate_otp()

            otp_expires_at = (
                datetime.now(timezone.utc)
                + timedelta(
                    minutes=OTP_EXPIRY_MINUTES
                )
            )

            existing_user.otp_code = otp_code

            existing_user.otp_expires_at = (
                otp_expires_at
            )

            db.commit()


            try:

                await send_email_otp(
                    receiver_email=existing_user.email,
                    otp_code=otp_code,
                )

            except Exception as error:

                print(
                    "SIGNUP OTP EMAIL ERROR:",
                    str(error),
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Could not send verification "
                        "email. Please try again later."
                    ),
                )


            return {
                "message": (
                    "Your account is not verified. "
                    "A new OTP has been sent."
                ),
                "email": existing_user.email,
                "requires_verification": True,
            }


        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )


    # --------------------------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------------------------

    if len(
        user_data.password.encode("utf-8")
    ) > 72:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be 72 bytes or less."
            ),
        )


    # --------------------------------------------------------
    # GENERATE OTP
    # --------------------------------------------------------

    otp_code = generate_otp()

    otp_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )
    )


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    new_user = User(

        name=user_data.name.strip(),

        email=email,

        password_hash=hash_password(
            user_data.password
        ),

        role="user",

        email_verified=False,

        otp_code=otp_code,

        otp_expires_at=otp_expires_at,

    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)


    # --------------------------------------------------------
    # SEND OTP EMAIL
    # --------------------------------------------------------

    try:

        await send_email_otp(
            receiver_email=new_user.email,
            otp_code=otp_code,
        )

    except Exception as error:

        print(
            "SIGNUP OTP EMAIL ERROR:",
            str(error),
        )

        # Remove newly created user if email fails
        db.delete(new_user)

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not send verification email. "
                "Please try again later."
            ),
        )


    # --------------------------------------------------------
    # SIGNUP SUCCESS
    # --------------------------------------------------------

    return {

        "message": (
            "Account created successfully. "
            "Please check your email for the "
            "6-digit verification OTP."
        ),

        "email": new_user.email,

        "requires_verification": True,

    }


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

@router.post(
    "/verify-email",
    response_model=TokenResponse,
)
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):

    email = data.email.strip().lower()

    otp = data.otp.strip()


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )


    # --------------------------------------------------------
    # ALREADY VERIFIED
    # --------------------------------------------------------

    if user.email_verified:

        raise HTTPException(
            status_code=400,
            detail="Email is already verified.",
        )


    # --------------------------------------------------------
    # CHECK OTP EXISTS
    # --------------------------------------------------------

    if not user.otp_code:

        raise HTTPException(
            status_code=400,
            detail=(
                "No verification OTP found. "
                "Please request a new OTP."
            ),
        )


    # --------------------------------------------------------
    # CHECK OTP EXPIRY
    # --------------------------------------------------------

    if not user.otp_expires_at:

        raise HTTPException(
            status_code=400,
            detail=(
                "OTP has expired. "
                "Please request a new OTP."
            ),
        )


    now = datetime.now(timezone.utc)


    # Handle timezone-safe comparison
    expires_at = user.otp_expires_at

    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )


    if now > expires_at:

        user.otp_code = None

        user.otp_expires_at = None

        db.commit()

        raise HTTPException(
            status_code=400,
            detail=(
                "OTP has expired. "
                "Please request a new OTP."
            ),
        )


    # --------------------------------------------------------
    # CHECK OTP
    # --------------------------------------------------------

    if otp != user.otp_code:

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP.",
        )


    # --------------------------------------------------------
    # VERIFY EMAIL
    # --------------------------------------------------------

    user.email_verified = True

    user.otp_code = None

    user.otp_expires_at = None


    db.commit()

    db.refresh(user)


    # --------------------------------------------------------
    # CREATE JWT
    # --------------------------------------------------------

    token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
        }
    )


    return {

        "access_token": token,

        "token_type": "bearer",

        "user": user,

    }


# ============================================================
# RESEND OTP
# ============================================================

@router.post(
    "/resend-otp",
    response_model=MessageResponse,
)
async def resend_otp(
    data: ResendOTPRequest,
    db: Session = Depends(get_db),
):

    email = data.email.strip().lower()


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    # --------------------------------------------------------
    # DON'T REVEAL ACCOUNT INFORMATION
    # --------------------------------------------------------

    if not user:

        return {
            "message": (
                "If an account exists with this email, "
                "a verification OTP has been sent."
            )
        }


    # --------------------------------------------------------
    # ALREADY VERIFIED
    # --------------------------------------------------------

    if user.email_verified:

        return {
            "message": (
                "This email is already verified."
            )
        }


    # --------------------------------------------------------
    # GENERATE NEW OTP
    # --------------------------------------------------------

    otp_code = generate_otp()

    otp_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )
    )


    user.otp_code = otp_code

    user.otp_expires_at = otp_expires_at


    db.commit()


    # --------------------------------------------------------
    # SEND OTP
    # --------------------------------------------------------

    try:

        await send_email_otp(
            receiver_email=user.email,
            otp_code=otp_code,
        )

    except Exception as error:

        print(
            "RESEND OTP EMAIL ERROR:",
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not send OTP email. "
                "Please try again later."
            ),
        )


    return {

        "message": (
            "A new verification OTP has been "
            "sent to your email."
        )

    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):

    email = user_data.email.strip().lower()


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


    if not verify_password(
        user_data.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


    # --------------------------------------------------------
    # EMAIL VERIFICATION CHECK
    # --------------------------------------------------------

    if not user.email_verified:

        raise HTTPException(
            status_code=403,
            detail=(
                "Email is not verified. "
                "Please verify your email using OTP."
            ),
        )


    # --------------------------------------------------------
    # CREATE TOKEN
    # --------------------------------------------------------

    token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
        }
    )


    return {

        "access_token": token,

        "token_type": "bearer",

        "user": user,

    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return current_user


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post(
    "/forgot-password"
)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db),
):

    email = email.strip().lower()


    user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


    # --------------------------------------------------------
    # Don't reveal whether email exists
    # --------------------------------------------------------

    if not user:

        return {

            "message": (
                "If an account exists with this email, "
                "a password reset link has been sent."
            )

        }


    # --------------------------------------------------------
    # Generate reset token
    # --------------------------------------------------------

    reset_token = secrets.token_urlsafe(32)


    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=15)
    )


    password_reset_tokens[
        reset_token
    ] = {

        "user_id": user.id,

        "expires_at": expires_at,

    }


    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    try:

        await send_password_reset_email(

            recipient_email=user.email,

            reset_token=reset_token,

        )

    except Exception as error:

        password_reset_tokens.pop(
            reset_token,
            None,
        )

        print(
            "PASSWORD RESET EMAIL ERROR:",
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not send password reset email. "
                "Please try again later."
            ),
        )


    return {

        "message": (
            "Password reset link has been sent "
            "to your registered email address."
        )

    }


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post(
    "/reset-password"
)
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
):

    token = token.strip()


    # --------------------------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------------------------

    if len(new_password) < 8:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be at least "
                "8 characters long"
            ),
        )


    if len(
        new_password.encode("utf-8")
    ) > 72:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be 72 bytes or less"
            ),
        )


    # --------------------------------------------------------
    # FIND TOKEN
    # --------------------------------------------------------

    reset_data = (
        password_reset_tokens.get(token)
    )


    if not reset_data:

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )


    # --------------------------------------------------------
    # CHECK EXPIRY
    # --------------------------------------------------------

    expires_at = reset_data[
        "expires_at"
    ]


    if (
        datetime.now(timezone.utc)
        > expires_at
    ):

        password_reset_tokens.pop(
            token,
            None,
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == reset_data["user_id"]
        )
        .first()
    )


    if not user:

        password_reset_tokens.pop(
            token,
            None,
        )

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    # --------------------------------------------------------
    # UPDATE PASSWORD
    # --------------------------------------------------------

    user.password_hash = hash_password(
        new_password
    )


    db.commit()

    db.refresh(user)


    # --------------------------------------------------------
    # TOKEN CAN ONLY BE USED ONCE
    # --------------------------------------------------------

    password_reset_tokens.pop(
        token,
        None,
    )


    return {

        "message": (
            "Password reset successfully. "
            "You can now login with your new password."
        )

    }