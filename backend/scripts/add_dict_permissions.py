"""
添加字典管理权限的脚本
用于在已有系统中添加字典管理相关权限
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


async def add_dict_permissions():
    """添加字典管理权限"""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        tenant_id = "0"
        
        # 检查字典权限组是否存在
        stmt = select(Permission).where(
            Permission.code == "dict:module",
            Permission.is_deleted == False
        )
        result = await db.execute(stmt)
        dict_group = result.scalar_one_or_none()
        
        if not dict_group:
            # 创建字典权限组
            dict_group = Permission(
                name="字典管理",
                code="dict:module",
                type=1,  # 分组
                sort=5,
                status=1,
                tenant_id=tenant_id,
            )
            db.add(dict_group)
            await db.flush()
            await db.refresh(dict_group)
            print(f"✅ 创建字典权限组: {dict_group.name} ({dict_group.code})")
        else:
            print(f"⚠️  字典权限组已存在: {dict_group.name} ({dict_group.code})")
        
        # 定义字典权限
        dict_permissions = [
            {"name": "字典列表", "code": "dict:list", "type": 2, "sort": 1},
            {"name": "字典查询", "code": "dict:query", "type": 2, "sort": 2},
            {"name": "字典创建", "code": "dict:create", "type": 2, "sort": 3},
            {"name": "字典更新", "code": "dict:update", "type": 2, "sort": 4},
            {"name": "字典删除", "code": "dict:delete", "type": 2, "sort": 5},
        ]
        
        permission_map = {}
        for perm_data in dict_permissions:
            # 检查权限是否已存在
            stmt = select(Permission).where(
                Permission.code == perm_data["code"],
                Permission.is_deleted == False
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                perm = Permission(
                    name=perm_data["name"],
                    code=perm_data["code"],
                    type=perm_data["type"],
                    sort=perm_data["sort"],
                    status=1,
                    tenant_id=tenant_id,
                )
                db.add(perm)
                await db.flush()
                await db.refresh(perm)
                permission_map[perm.code] = perm.id
                print(f"✅ 创建权限: {perm.name} ({perm.code})")
            else:
                permission_map[existing.code] = existing.id
                print(f"⚠️  权限已存在: {existing.name} ({existing.code})")
        
        # 查找超级管理员角色
        stmt = select(Role).where(Role.code == "SUPER_ADMIN", Role.is_deleted == False)
        result = await db.execute(stmt)
        super_admin_role = result.scalar_one_or_none()
        
        if super_admin_role:
            # 给超级管理员角色分配所有字典权限
            for perm_code, perm_id in permission_map.items():
                # 检查是否已分配
                stmt = select(RolePermission).where(
                    RolePermission.role_id == super_admin_role.id,
                    RolePermission.permission_id == perm_id
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if not existing:
                    role_perm = RolePermission(
                        role_id=super_admin_role.id,
                        permission_id=perm_id,
                        tenant_id=tenant_id,
                    )
                    db.add(role_perm)
                    print(f"✅ 给超级管理员角色分配权限: {perm_code}")
                else:
                    print(f"⚠️  超级管理员角色已有权限: {perm_code}")
        else:
            print("⚠️  未找到超级管理员角色")
        
        await db.commit()
        print(f"\n🎉 成功添加字典管理权限！")


if __name__ == "__main__":
    print("🌱 添加字典管理权限...")
    asyncio.run(add_dict_permissions())

