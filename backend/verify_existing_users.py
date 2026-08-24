from sqlalchemy import text

from app.database import engine


def verify_existing_users():

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                UPDATE users
                SET email_verified = TRUE
                WHERE email_verified = FALSE;
                """
            )
        )

    print()
    print("========================================")
    print("EXISTING USERS VERIFIED")
    print("========================================")
    print("All existing accounts are now verified.")
    print("New accounts will still require OTP.")
    print("========================================")


if __name__ == "__main__":
    verify_existing_users()