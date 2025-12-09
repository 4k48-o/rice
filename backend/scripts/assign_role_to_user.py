"""
给用户分配角色的脚本
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.associations import UserRole


async def assign_role_to_user(username: str, role_code: str):
    """给用户分配角色"""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        # 查找用户
        stmt = select(User).where(User.username == username, User.is_deleted == False)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 未找到用户: {username}")
            return
        
        # 查找角色
        stmt = select(Role).where(Role.code == role_code, Role.is_deleted == False)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            print(f"❌ 未找到角色: {role_code}")
            return
        
        # 检查是否已分配
        stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"⚠️  用户 {username} 已有角色 {role_code}")
            return
        
        # 分配角色
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            tenant_id=user.tenant_id
        )
        db.add(user_role)
        await db.commit()
        
        print(f"✅ 成功给用户 {username} 分配角色 {role_code} ({role.name})")


if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "test123"
    role_code = sys.argv[2] if len(sys.argv) > 2 else "SUPER_ADMIN"
    
    print(f"🌱 给用户 {username} 分配角色 {role_code}...")
    asyncio.run(assign_role_to_user(username, role_code))

