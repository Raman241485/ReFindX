import os

import resend

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# RESEND CONFIGURATION
# ============================================================

RESEND_API_KEY = os.getenv(
    "RESEND_API_KEY"
)

RESEND_FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "onboarding@resend.dev",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://refindx-frontend.onrender.com",
)


# ============================================================
# INITIALIZE RESEND
# ============================================================

def get_resend():

    if not RESEND_API_KEY:

        raise RuntimeError(
            "RESEND_API_KEY environment variable "
            "is not configured."
        )

    resend.api_key = RESEND_API_KEY

    return resend


# ============================================================
# SEND CONTACT EMAIL
# ============================================================

async def send_contact_email(
    receiver_email: str,
    sender_name: str,
    sender_email: str,
    item_title: str,
    message_text: str,
):
    """
    Send a contact message from a person who lost an item
    to the person who found/owns the item.
    """

    client = get_resend()


    # ========================================================
    # EMAIL HTML
    # ========================================================

    html_content = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>
            ReFindX - Someone wants to contact you
        </title>

    </head>


    <body
        style="
            margin:0;
            padding:0;
            background:#f4f4f5;
            font-family:Arial,sans-serif;
        "
    >

        <div
            style="
                max-width:600px;
                margin:40px auto;
                background:#ffffff;
                padding:30px;
                border-radius:12px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);
            "
        >

            <h1
                style="
                    color:#7c3aed;
                    margin-bottom:10px;
                "
            >
                ReFindX
            </h1>


            <h2>
                Someone wants to contact you
            </h2>


            <p>
                <strong>{sender_name}</strong>
                wants to contact you regarding:
            </p>


            <div
                style="
                    background:#f3e8ff;
                    padding:15px;
                    border-radius:8px;
                    margin:20px 0;
                "
            >

                <strong>
                    {item_title}
                </strong>

            </div>


            <h3>
                Message
            </h3>


            <div
                style="
                    background:#f8fafc;
                    border:1px solid #e5e7eb;
                    padding:18px;
                    border-radius:8px;
                    white-space:pre-wrap;
                "
            >

                {message_text}

            </div>


            <div
                style="
                    margin-top:25px;
                    padding:15px;
                    background:#f9fafb;
                    border-radius:8px;
                "
            >

                <p style="margin:5px 0;">

                    <strong>
                        Sender:
                    </strong>

                    {sender_name}

                </p>


                <p style="margin:5px 0;">

                    <strong>
                        Email:
                    </strong>

                    {sender_email}

                </p>

            </div>


            <p
                style="
                    margin-top:25px;
                    color:#555;
                "
            >

                If you lost this item, you can reply to
                the sender's email address above to
                continue the conversation.

            </p>


            <hr
                style="
                    border:none;
                    border-top:1px solid #e5e7eb;
                    margin:25px 0;
                "
            >


            <p
                style="
                    color:#999;
                    font-size:12px;
                "
            >

                ReFindX - AI Powered Lost & Found

            </p>

        </div>

    </body>

    </html>
    """


    # ========================================================
    # SEND EMAIL
    # ========================================================

    params = {

        "from":
            RESEND_FROM_EMAIL,

        "to": [
            receiver_email
        ],

        "reply_to":
            sender_email,

        "subject":
            f"ReFindX - Contact regarding '{item_title}'",

        "html":
            html_content,
    }


    try:

        response = await client.Emails.send_async(
            params
        )


        print(
            "CONTACT EMAIL SENT:",
            response
        )


        return response


    except Exception as error:

        print(
            "RESEND CONTACT EMAIL ERROR:",
            str(error)
        )


        raise RuntimeError(
            f"Failed to send contact email: {error}"
        ) from error


# ============================================================
# SEND OTP EMAIL
# ============================================================

async def send_email_otp(
    receiver_email: str,
    otp_code: str,
):
    """
    Send email verification OTP using Resend.
    """

    client = get_resend()


    params = {

        "from":
            RESEND_FROM_EMAIL,

        "to": [
            receiver_email
        ],

        "subject":
            "ReFindX - Email Verification OTP",

        "html": f"""
        <!DOCTYPE html>

        <html>

        <body
            style="
                margin:0;
                padding:0;
                background:#f4f4f5;
                font-family:Arial,sans-serif;
            "
        >

            <div
                style="
                    max-width:500px;
                    margin:40px auto;
                    background:#ffffff;
                    padding:30px;
                    border-radius:12px;
                "
            >

                <h1
                    style="
                        color:#7c3aed;
                    "
                >
                    ReFindX
                </h1>


                <h2>
                    Verify your email
                </h2>


                <p>
                    Welcome to ReFindX!
                </p>


                <p>
                    Use the following OTP to verify
                    your email address:
                </p>


                <div
                    style="
                        margin:25px 0;
                        padding:20px;
                        text-align:center;
                        background:#f3e8ff;
                        border-radius:10px;
                    "
                >

                    <span
                        style="
                            font-size:32px;
                            font-weight:bold;
                            letter-spacing:8px;
                            color:#7c3aed;
                        "
                    >
                        {otp_code}
                    </span>

                </div>


                <p>
                    This OTP is valid for
                    <strong>5 minutes</strong>.
                </p>


                <hr>


                <p
                    style="
                        color:#999999;
                        font-size:12px;
                    "
                >
                    ReFindX - AI Powered Lost & Found
                </p>

            </div>

        </body>

        </html>
        """,
    }


    try:

        response = await client.Emails.send_async(
            params
        )


        print(
            "OTP EMAIL SENT:",
            response
        )


        return response


    except Exception as error:

        print(
            "RESEND OTP EMAIL ERROR:",
            str(error)
        )


        raise RuntimeError(
            f"Failed to send OTP email: {error}"
        ) from error


# ============================================================
# SEND PASSWORD RESET EMAIL
# ============================================================

async def send_password_reset_email(
    recipient_email: str,
    reset_token: str,
):
    """
    Send password reset email using Resend.
    """

    client = get_resend()


    reset_url = (
        f"{FRONTEND_URL}/reset-password"
        f"?token={reset_token}"
    )


    params = {

        "from":
            RESEND_FROM_EMAIL,

        "to": [
            recipient_email
        ],

        "subject":
            "ReFindX - Reset Your Password",

        "html": f"""
        <!DOCTYPE html>

        <html>

        <body
            style="
                margin:0;
                padding:0;
                background:#f4f4f5;
                font-family:Arial,sans-serif;
            "
        >

            <div
                style="
                    max-width:500px;
                    margin:40px auto;
                    background:#ffffff;
                    padding:30px;
                    border-radius:12px;
                "
            >

                <h1
                    style="
                        color:#7c3aed;
                    "
                >
                    ReFindX
                </h1>


                <h2>
                    Reset your password
                </h2>


                <p>
                    We received a request to reset
                    your ReFindX password.
                </p>


                <p>
                    Click the button below to create
                    a new password.
                </p>


                <div
                    style="
                        text-align:center;
                        margin:30px 0;
                    "
                >

                    <a
                        href="{reset_url}"
                        style="
                            display:inline-block;
                            padding:14px 24px;
                            background:#7c3aed;
                            color:#ffffff;
                            text-decoration:none;
                            border-radius:8px;
                            font-weight:bold;
                        "
                    >
                        Reset Password
                    </a>

                </div>


                <p
                    style="
                        color:#666666;
                        font-size:13px;
                    "
                >

                    This password reset link is valid
                    for 15 minutes.

                </p>


                <hr>


                <p
                    style="
                        color:#999999;
                        font-size:12px;
                    "
                >
                    ReFindX - AI Powered Lost & Found
                </p>

            </div>

        </body>

        </html>
        """,
    }


    try:

        response = await client.Emails.send_async(
            params
        )


        print(
            "PASSWORD RESET EMAIL SENT:",
            response
        )


        return response


    except Exception as error:

        print(
            "RESEND PASSWORD RESET EMAIL ERROR:",
            str(error)
        )


        raise RuntimeError(
            f"Failed to send password reset email: {error}"
        ) from error