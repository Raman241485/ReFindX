from sqlalchemy import text

from app.database import engine


def add_otp_columns():

    with engine.begin() as connection:

        # ----------------------------------------------------
        # EMAIL VERIFIED
        # ----------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS
                email_verified BOOLEAN
                NOT NULL DEFAULT FALSE;
                """
            )
        )

        # ----------------------------------------------------
        # OTP CODE
        # ----------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS
                otp_code VARCHAR(6);
                """
            )
        )

        # ----------------------------------------------------
        # OTP EXPIRY
        # ----------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS
                otp_expires_at TIMESTAMP WITH TIME ZONE;
                """
            )
        )

    print()
    print("========================================")
    print("OTP DATABASE MIGRATION SUCCESSFUL")
    print("========================================")
    print("Added:")
    print("1. email_verified")
    print("2. otp_code")
    print("3. otp_expires_at")
    print("========================================")


if __name__ == "__main__":

    add_otp_columns()