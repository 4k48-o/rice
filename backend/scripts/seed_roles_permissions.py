"""
Seed data script for roles and permissions.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.associations import RolePermission


async def seed_roles_permissions():
    """Seed initial roles and permissions."""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        # Check if permissions already exist
        stmt = select(Permission).limit(1)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print("⚠️  Permissions already exist, skipping seed")
            return
        
        # Default tenant_id (adjust as needed)
        tenant_id = 0
        
        # Define permissions by module
        permissions_data = [
            # User module
            {"name": "用户查询", "code": "user:list", "type": 2, "sort": 1},
            {"name": "用户详情", "code": "user:query", "type": 2, "sort": 2},
            {"name": "用户创建", "code": "user:create", "type": 2, "sort": 3},
            {"name": "用户更新", "code": "user:update", "type": 2, "sort": 4},
            {"name": "用户删除", "code": "user:delete", "type": 2, "sort": 5},
            
            # Role module
            {"name": "角色查询", "code": "role:list", "type": 2, "sort": 11},
            {"name": "角色详情", "code": "role:query", "type": 2, "sort": 12},
            {"name": "角色创建", "code": "role:create", "type": 2, "sort": 13},
            {"name": "角色更新", "code": "role:update", "type": 2, "sort": 14},
            {"name": "角色删除", "code": "role:delete", "type": 2, "sort": 15},
            
            # Department module
            {"name": "部门查询", "code": "dept:list", "type": 2, "sort": 21},
            {"name": "部门详情", "code": "dept:query", "type": 2, "sort": 22},
            {"name": "部门创建", "code": "dept:create", "type": 2, "sort": 23},
            {"name": "部门更新", "code": "dept:update", "type": 2, "sort": 24},
            {"name": "部门删除", "code": "dept:delete", "type": 2, "sort": 25},
            
            # Menu module
            {"name": "菜单查询", "code": "menu:list", "type": 2, "sort": 31},
            {"name": "菜单详情", "code": "menu:query", "type": 2, "sort": 32},
            {"name": "菜单创建", "code": "menu:create", "type": 2, "sort": 33},
            {"name": "菜单更新", "code": "menu:update", "type": 2, "sort": 34},
            {"name": "菜单删除", "code": "menu:delete", "type": 2, "sort": 35},
        ]
        
        # Create permissions
        permission_map = {}
        for perm_data in permissions_data:
            perm = Permission(**perm_data)
            db.add(perm)
            await db.flush()
            await db.refresh(perm)
            permission_map[perm.code] = perm.id
            print(f"✅ Created permission: {perm.name} ({perm.code})")

        
        # Define roles
        roles_data = [
            {
                "name": "超级管理员",
                "code": "SUPER_ADMIN",
                "sort": 1,
                "data_scope": 1,  # All data
                "permissions": list(permission_map.keys())  # All permissions
            },
            {
                "name": "管理员",
                "code": "ADMIN",
                "sort": 2,
                "data_scope": 2,  # Department and sub-departments
                "permissions": [
                    "user:list", "user:query", "user:create", "user:update",
                    "role:list", "role:query",
                    "dept:list", "dept:query", "dept:create", "dept:update",
                    "menu:list", "menu:query"
                ]
            },
            {
                "name": "普通用户",
                "code": "USER",
                "sort": 3,
                "data_scope": 4,  # Self only
                "permissions": [
                    "user:list", "user:query",
                    "dept:list", "dept:query",
                    "menu:list"
                ]
            },
        ]
        
        # Create roles and assign permissions
        for role_data in roles_data:
            perm_codes = role_data.pop("permissions")
            role = Role(**role_data, tenant_id=tenant_id)
            db.add(role)
            await db.flush()
            await db.refresh(role)
            
            # Assign permissions
            for perm_code in perm_codes:
                if perm_code in permission_map:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permission_map[perm_code]
                    )
                    db.add(role_perm)
            
            print(f"✅ Created role: {role.name} ({len(perm_codes)} permissions)")
        
        await db.commit()
        print(f"\n🎉 Successfully seeded {len(permissions_data)} permissions and {len(roles_data)} roles!")


if __name__ == "__main__":
    print("🌱 Seeding roles and permissions...")
    asyncio.run(seed_roles_permissions())
