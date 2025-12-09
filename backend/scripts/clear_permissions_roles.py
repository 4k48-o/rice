"""
Clear all permissions and roles from database.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from app.core.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.associations import RolePermission, UserRole


async def clear_permissions_roles():
    """Clear all permissions and roles."""
    async with AsyncSessionLocal() as db:
        # Delete in correct order (foreign key constraints)
        await db.execute(delete(UserRole))
        await db.execute(delete(RolePermission))
        await db.execute(delete(Role))
        await db.execute(delete(Permission))
        await db.commit()
        print("✅ Cleared all permissions and roles")


if __name__ == "__main__":
    print("🗑️  Clearing permissions and roles...")
    asyncio.run(clear_permissions_roles())

