import os

from dotenv import load_dotenv

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SMTP SETTINGS
#
# Supports your existing:
# SMTP_HOST
# SMTP_PORT
# SMTP_USERNAME
# SMTP_PASSWORD
# SMTP_FROM
#
# Also supports MAIL_* as fallback.
# ============================================================

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        os.getenv(
            "MAIL_PORT",
            "587"
        )
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    os.getenv(
        "MAIL_USERNAME"
    )
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    os.getenv(
        "MAIL_PASSWORD"
    )
)

SMTP_FROM = os.getenv(
    "SMTP_FROM",
    os.getenv(
        "MAIL_FROM",
        SMTP_USERNAME
    )
)


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

conf = ConnectionConfig(

    MAIL_USERNAME=SMTP_USERNAME,

    MAIL_PASSWORD=SMTP_PASSWORD,

    MAIL_FROM=SMTP_FROM,

    MAIL_PORT=SMTP_PORT,

    MAIL_SERVER=SMTP_HOST,

    MAIL_STARTTLS=True,

    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,

    VALIDATE_CERTS=True,
)


# ============================================================
# FAST MAIL INSTANCE
# ============================================================

fast_mail = FastMail(
    conf
)


# ============================================================
# PASSWORD RESET EMAIL
# ============================================================

async def send_password_reset_email(
    *args,
    **kwargs,
):
    """
    Send password reset email.

    This function intentionally accepts both
    positional and keyword arguments so it remains
    compatible with the existing auth.py.
    """

    # --------------------------------------------------------
    # Try to find email
    # --------------------------------------------------------

    email = (
        kwargs.get("email")
        or kwargs.get("receiver_email")
        or kwargs.get("user_email")
        or kwargs.get("to_email")
    )

    # --------------------------------------------------------
    # Try to find reset link
    # --------------------------------------------------------

    reset_link = (
        kwargs.get("reset_link")
        or kwargs.get("reset_url")
        or kwargs.get("link")
    )

    # --------------------------------------------------------
    # Try to find token
    # --------------------------------------------------------

    token = (
        kwargs.get("token")
        or kwargs.get("reset_token")
    )

    # --------------------------------------------------------
    # Handle positional arguments
    # --------------------------------------------------------

    if args:

        if email is None:
            email = args[0]

        if len(args) >= 2:

            if reset_link is None:
                reset_link = args[1]

        if len(args) >= 3:

            if token is None:
                token = args[2]

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if not email:

        raise ValueError(
            "Password reset email recipient is missing."
        )

    # --------------------------------------------------------
    # If auth.py provides only token,
    # create a frontend reset URL.
    # --------------------------------------------------------

    if not reset_link and token:

        frontend_url = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173"
        )

        reset_link = (
            f"{frontend_url}"
            f"/reset-password?token={token}"
        )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not reset_link:

        reset_link = (
        "Please use the password reset link "
        "provided by ReFindX."
    )

    # --------------------------------------------------------
    # Email
    # --------------------------------------------------------

    message = MessageSchema(

        subject=(
            "ReFindX - Password Reset"
        ),

        recipients=[
            email
        ],

        body=f"""
Hello,

We received a request to reset your
ReFindX account password.

Use the following link to reset your password:

{reset_link}

If you did not request a password reset,
you can safely ignore this email.

For security reasons, do not share your
password reset link with anyone.

Regards,

ReFindX
Lost • Found • Reconnected
""",

        subtype="plain",
    )

    await fast_mail.send_message(
        message
    )


# ============================================================
# CONTACT ITEM OWNER
# ============================================================

async def send_contact_email(
    receiver_email: str,
    sender_name: str,
    sender_email: str,
    item_title: str,
    message_text: str,
):
    """
    Send an email to the owner of a
    lost/found item.

    Example:

    Found person
        ↓
    ReFindX
        ↓
    Lost item owner
    """

    # --------------------------------------------------------
    # Validate receiver
    # --------------------------------------------------------

    if not receiver_email:

        raise ValueError(
            "Receiver email is missing."
        )

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not message_text:

        raise ValueError(
            "Contact message cannot be empty."
        )

    # --------------------------------------------------------
    # Create email
    # --------------------------------------------------------

    message = MessageSchema(

        subject=(
            f"ReFindX - Someone contacted you "
            f"about '{item_title}'"
        ),

        recipients=[
            receiver_email
        ],

        body=f"""
Hello,

Someone has contacted you through ReFindX
regarding your item.

--------------------------------
ITEM
--------------------------------

{item_title}


--------------------------------
MESSAGE
--------------------------------

{message_text}


--------------------------------
SENDER
--------------------------------

Name:
{sender_name}

Email:
{sender_email}


--------------------------------

You can contact the sender directly using
the email address above.

Please do not share sensitive personal
information through ReFindX.

Regards,

ReFindX
Lost • Found • Reconnected
""",

        subtype="plain",
    )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    await fast_mail.send_message(
        message
    )

    # ============================================================
# EMAIL OTP VERIFICATION
# ============================================================

async def send_email_otp(
    receiver_email: str,
    otp_code: str,
):
    """
    Send email verification OTP to a ReFindX user.
    """

    # --------------------------------------------------------
    # Validate recipient
    # --------------------------------------------------------

    if not receiver_email:

        raise ValueError(
            "OTP recipient email is missing."
        )


    # --------------------------------------------------------
    # Validate OTP
    # --------------------------------------------------------

    if not otp_code:

        raise ValueError(
            "OTP code is missing."
        )


    # --------------------------------------------------------
    # Create email
    # --------------------------------------------------------

    message = MessageSchema(

        subject=(
            "ReFindX - Email Verification OTP"
        ),

        recipients=[
            receiver_email
        ],

        body=f"""
Hello,

Welcome to ReFindX - Lost • Found • Reconnected.

Your email verification OTP is:

--------------------------------
        {otp_code}
--------------------------------

This OTP is valid for 5 minutes.

Enter this OTP on the ReFindX website
to verify your email address.

If you did not create a ReFindX account,
please ignore this email.

For your security, do not share this OTP
with anyone.

Regards,

ReFindX
Lost • Found • Reconnected
""",

        subtype="plain",
    )


    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    await fast_mail.send_message(
        message
    )