from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


def create_admin():
    db = SessionLocal()

    try:
        name = input("Admin name: ").strip()
        email = input("Admin email: ").strip().lower()
        password = getpass("Admin password: ")

        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("User with this email already exists.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin created successfully!")
        print("ID:", admin.id)
        print("Email:", admin.email)
        print("Role:", admin.role)

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()