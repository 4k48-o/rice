"""
Seed initial users.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.utils.snowflake import init_snowflake
from app.core.config import settings


async def seed_users():
    """Seed initial users."""
    # Initialize Snowflake
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("⚠️  Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            email="admin@example.com",
            real_name="系统管理员",
            user_type=0,  # Superadmin
            status=1,
            tenant_id=0
        )
        db.add(admin)
        
        # Create test user
        test_user = User(
            username="testuser",
            password=get_password_hash("Test@123456"),
            email="test@example.com",
            real_name="测试用户",
            user_type=2,  # Regular user
            status=1,
            tenant_id=0
        )
        db.add(test_user)
        
        await db.commit()
        await db.refresh(admin)
        await db.refresh(test_user)
        
        print(f"✅ Created user: {admin.username} (ID: {admin.id})")
        print(f"✅ Created user: {test_user.username} (ID: {test_user.id})")
        print("\n🎉 Successfully seeded 2 users!")
        print("\nLogin credentials:")
        print("  Admin: admin / admin123")
        print("  Test User: testuser / Test@123456")


if __name__ == "__main__":
    asyncio.run(seed_users())
