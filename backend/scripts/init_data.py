"""
Initialize database with default data.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from app.services.user_service import user_service
from app.models.tenant import Tenant
from app.utils.snowflake import generate_id

async def init_data():
    """Initialize default data."""
    async with AsyncSessionLocal() as session:
        print("Creating default tenant...")
        # Check if tenant exists
        # For simplicity, we just try to create if not exists or ignore unique constraint error logic properly
        # But here we just assume clean db or careful insertion
        
        # ID 会自动通过 BaseModel 的雪花算法生成，无需手动设置
        tenant = Tenant(
            name="Default Tenant",
            code="default",
            status=1
        )
        session.add(tenant)
        await session.flush()  # 刷新以获取自动生成的 ID
        tenant_id = tenant.id
        
        print("Creating super admin user...")
        # Create admin
        # Password: admin123
        user_id = generate_id()
        await user_service.create_user(
            session,
            username="admin",
            password="admin123",
            email="admin@example.com",
            tenant_id=tenant_id,
            is_admin=True
        )
        
        try:
            await session.commit()
            print("✅ Default data initialized successfully!")
            print("User: admin / admin123")
        except Exception as e:
            print(f"❌ Failed to initialize data: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(init_data())
