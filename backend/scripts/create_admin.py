"""Create a super admin user."""
import asyncio
import sys

# Add parent directory to path
sys.path.insert(0, ".")

from app.db.session import async_session
from app.repositories.user import UserRepository
from app.core.security import get_password_hash
from app.models.user import Role


async def create_admin(
    full_name: str,
    staff_id: str,
    department: str,
    section: str,
    password: str,
) -> None:
    """Create a super admin user."""
    async with async_session() as db:
        user_repo = UserRepository(db)

        # Check if user already exists
        existing = await user_repo.get_by_staff_id(staff_id)
        if existing:
            print(f"User with staff_id '{staff_id}' already exists!")
            return

        # Create user
        user = await user_repo.create({
            "full_name": full_name,
            "staff_id": staff_id,
            "department": department,
            "section": section,
            "role": Role.SUPER_ADMIN,
            "password_hash": get_password_hash(password),
            "is_active": True,
        })
        await db.commit()

        print(f"✅ Super admin user created successfully!")
        print(f"   Name: {user.full_name}")
        print(f"   Staff ID: {user.staff_id}")
        print(f"   Role: {user.role}")
        print(f"\n   You can now login with:")
        print(f"   Staff ID: {user.staff_id}")
        print(f"   Password: {password}")


if __name__ == "__main__":
    # Default values - you can change these or pass as arguments
    import argparse

    parser = argparse.ArgumentParser(description="Create a super admin user")
    parser.add_argument("--name", default="Super Admin", help="Full name")
    parser.add_argument("--staff-id", default="ADMIN001", help="Staff ID")
    parser.add_argument("--department", default="Administration", help="Department")
    parser.add_argument("--section", default="IT", help="Section")
    parser.add_argument("--password", default="admin123", help="Password")

    args = parser.parse_args()

    asyncio.run(create_admin(
        full_name=args.name,
        staff_id=args.staff_id,
        department=args.department,
        section=args.section,
        password=args.password,
    ))
