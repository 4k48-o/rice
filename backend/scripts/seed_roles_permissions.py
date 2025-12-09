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
from app.models.associations import RolePermission, UserRole
from app.models.user import User


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
        tenant_id = "0"
        
        # Define permission groups (type=1, 目录/分组)
        groups_data = [
            {"name": "用户管理", "code": "user:module", "type": 1, "sort": 1},
            {"name": "角色管理", "code": "role:module", "type": 1, "sort": 2},
            {"name": "部门管理", "code": "dept:module", "type": 1, "sort": 3},
            {"name": "菜单管理", "code": "menu:module", "type": 1, "sort": 4},
        ]
        
        # Create permission groups first
        group_map = {}  # code -> id
        for group_data in groups_data:
            group = Permission(**group_data, tenant_id=tenant_id)
            db.add(group)
            await db.flush()  # 刷新以获取自动生成的 ID
            await db.refresh(group)
            group_map[group.code] = group.id
            print(f"✅ Created permission group: {group.name} ({group.code})")
        
        # Define permissions by module (type=2, 菜单/权限)
        # parent_group 字段用于指定所属分组
        permissions_data = [
            # User module
            {"name": "用户查询", "code": "user:list", "type": 2, "sort": 1, "parent_group": "user:module"},
            {"name": "用户详情", "code": "user:query", "type": 2, "sort": 2, "parent_group": "user:module"},
            {"name": "用户创建", "code": "user:create", "type": 2, "sort": 3, "parent_group": "user:module"},
            {"name": "用户更新", "code": "user:update", "type": 2, "sort": 4, "parent_group": "user:module"},
            {"name": "用户删除", "code": "user:delete", "type": 2, "sort": 5, "parent_group": "user:module"},
            
            # Role module
            {"name": "角色查询", "code": "role:list", "type": 2, "sort": 1, "parent_group": "role:module"},
            {"name": "角色详情", "code": "role:query", "type": 2, "sort": 2, "parent_group": "role:module"},
            {"name": "角色创建", "code": "role:create", "type": 2, "sort": 3, "parent_group": "role:module"},
            {"name": "角色更新", "code": "role:update", "type": 2, "sort": 4, "parent_group": "role:module"},
            {"name": "角色删除", "code": "role:delete", "type": 2, "sort": 5, "parent_group": "role:module"},
            
            # Department module
            {"name": "部门查询", "code": "dept:list", "type": 2, "sort": 1, "parent_group": "dept:module"},
            {"name": "部门详情", "code": "dept:query", "type": 2, "sort": 2, "parent_group": "dept:module"},
            {"name": "部门创建", "code": "dept:create", "type": 2, "sort": 3, "parent_group": "dept:module"},
            {"name": "部门更新", "code": "dept:update", "type": 2, "sort": 4, "parent_group": "dept:module"},
            {"name": "部门删除", "code": "dept:delete", "type": 2, "sort": 5, "parent_group": "dept:module"},
            
            # Menu module
            {"name": "菜单查询", "code": "menu:list", "type": 2, "sort": 1, "parent_group": "menu:module"},
            {"name": "菜单详情", "code": "menu:query", "type": 2, "sort": 2, "parent_group": "menu:module"},
            {"name": "菜单创建", "code": "menu:create", "type": 2, "sort": 3, "parent_group": "menu:module"},
            {"name": "菜单更新", "code": "menu:update", "type": 2, "sort": 4, "parent_group": "menu:module"},
            {"name": "菜单删除", "code": "menu:delete", "type": 2, "sort": 5, "parent_group": "menu:module"},
        ]
        
        # Create permissions with parent_id set to group ID
        permission_map = {}
        for perm_data in permissions_data:
            # Extract parent_group and remove it from perm_data
            parent_group = perm_data.pop("parent_group")
            parent_id = group_map.get(parent_group, "0")  # Default to "0" if group not found
            
            # ID 会自动通过 BaseModel 的雪花算法生成，无需手动设置
            perm = Permission(**perm_data, parent_id=parent_id, tenant_id=tenant_id)
            db.add(perm)
            await db.flush()  # 刷新以获取自动生成的 ID
            await db.refresh(perm)
            permission_map[perm.code] = perm.id
            print(f"✅ Created permission: {perm.name} ({perm.code}) under group {parent_group}")

        
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
        
        # 给超级管理员用户分配"超级管理员"角色
        # 查找超级管理员用户
        stmt = select(User).where(User.username == "admin", User.user_type == 0)
        result = await db.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        # 查找"超级管理员"角色
        stmt = select(Role).where(Role.code == "SUPER_ADMIN")
        result = await db.execute(stmt)
        super_admin_role = result.scalar_one_or_none()
        
        if admin_user and super_admin_role:
            # 检查是否已经分配
            stmt = select(UserRole).where(
                UserRole.user_id == admin_user.id,
                UserRole.role_id == super_admin_role.id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=super_admin_role.id,
                    tenant_id="0"
                )
                db.add(user_role)
                print(f"✅ Assigned SUPER_ADMIN role to admin user")
            else:
                print("⚠️  Admin user already has SUPER_ADMIN role")
        elif not admin_user:
            print("⚠️  Admin user not found, skipping role assignment")
        elif not super_admin_role:
            print("⚠️  SUPER_ADMIN role not found, skipping role assignment")
        
        await db.commit()
        print(f"\n🎉 Successfully seeded:")
        print(f"   - {len(groups_data)} permission groups")
        print(f"   - {len(permissions_data)} permissions")
        print(f"   - {len(roles_data)} roles")


if __name__ == "__main__":
    print("🌱 Seeding roles and permissions...")
    asyncio.run(seed_roles_permissions())
