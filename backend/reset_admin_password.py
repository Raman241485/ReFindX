from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


def reset_admin_password():
    db = SessionLocal()

    try:
        email = input("Admin email: ").strip().lower()
        new_password = getpass("New admin password: ")

        if len(new_password) < 8:
            print("Password must be at least 8 characters.")
            return

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            print("User not found.")
            return

        if user.role != "admin":
            print("This user is not an admin.")
            return

        user.password_hash = hash_password(
            new_password
        )

        db.commit()
        db.refresh(user)

        print("\nAdmin password reset successfully!")
        print("Email:", user.email)
        print("Role:", user.role)

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    reset_admin_password()