"""
Seed data script for initial menus.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.menu import Menu



async def seed_menus():
    """Seed initial menu data."""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:


        # Check if menus already exist
        stmt = select(Menu).limit(1)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print("⚠️  Menus already exist, skipping seed")
            return
        
        # Default tenant_id (adjust as needed)
        tenant_id = 0
        
        # Define menu structure
        menus = [
            # System Management (Directory)
            {
                "name": "system",
                "title": "系统管理",
                "path": "/system",
                "component": "Layout",
                "icon": "setting",
                "sort": 1,
                "type": 1,  # Directory
                "tenant_id": tenant_id,
                "children": [
                    {
                        "name": "user",
                        "title": "用户管理",
                        "path": "/system/user",
                        "component": "system/user/index",
                        "icon": "user",
                        "sort": 1,
                        "type": 2,  # Menu
                        "permission_code": "user:list",
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "role",
                        "title": "角色管理",
                        "path": "/system/role",
                        "component": "system/role/index",
                        "icon": "team",
                        "sort": 2,
                        "type": 2,
                        "permission_code": "role:list",
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "menu",
                        "title": "菜单管理",
                        "path": "/system/menu",
                        "component": "system/menu/index",
                        "icon": "menu",
                        "sort": 3,
                        "type": 2,
                        "permission_code": "menu:list",
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "dept",
                        "title": "部门管理",
                        "path": "/system/dept",
                        "component": "system/dept/index",
                        "icon": "apartment",
                        "sort": 4,
                        "type": 2,
                        "permission_code": "dept:list",
                        "tenant_id": tenant_id,
                    },
                ]
            },
            # Monitoring (Directory)
            {
                "name": "monitor",
                "title": "系统监控",
                "path": "/monitor",
                "component": "Layout",
                "icon": "monitor",
                "sort": 2,
                "type": 1,
                "tenant_id": tenant_id,
                "children": [
                    {
                        "name": "online",
                        "title": "在线用户",
                        "path": "/monitor/online",
                        "component": "monitor/online/index",
                        "icon": "user-switch",
                        "sort": 1,
                        "type": 2,
                        "permission_code": "monitor:online",
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "loginlog",
                        "title": "登录日志",
                        "path": "/monitor/loginlog",
                        "component": "monitor/loginlog/index",
                        "icon": "file-text",
                        "sort": 2,
                        "type": 2,
                        "permission_code": "monitor:loginlog",
                        "tenant_id": tenant_id,
                    },
                ]
            },
        ]
        
        # Insert menus
        parent_map = {}
        
        async def insert_menu(menu_data, parent_id=None):
            """Recursively insert menu and children."""
            children = menu_data.pop("children", [])
            menu_data["parent_id"] = parent_id
            
            menu = Menu(**menu_data)
            db.add(menu)
            await db.flush()
            await db.refresh(menu)
            
            print(f"✅ Created menu: {menu.title} (ID: {menu.id})")
            
            # Insert children
            for child_data in children:
                await insert_menu(child_data, menu.id)
        
        for menu_data in menus:
            await insert_menu(menu_data)
        
        await db.commit()
        print(f"\n🎉 Successfully seeded {len(menus)} top-level menus!")


if __name__ == "__main__":
    print("🌱 Seeding menu data...")
    asyncio.run(seed_menus())
