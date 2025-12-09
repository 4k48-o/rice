"""
添加字典管理菜单项的脚本
用于在已有系统中添加字典管理菜单
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.menu import Menu


async def add_dict_menu():
    """添加字典管理菜单项到系统管理目录下"""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        # 查找系统管理目录
        stmt = select(Menu).where(
            Menu.path == "/system",
            Menu.type == 1,  # Directory
            Menu.is_deleted == False
        )
        result = await db.execute(stmt)
        system_menu = result.scalar_one_or_none()
        
        if not system_menu:
            print("❌ 未找到系统管理目录，请先确保系统管理菜单存在")
            return
        
        # 检查字典管理菜单是否已存在
        stmt = select(Menu).where(
            Menu.path == "/system/dict",
            Menu.is_deleted == False
        )
        result = await db.execute(stmt)
        existing_menu = result.scalar_one_or_none()
        
        if existing_menu:
            print("⚠️  字典管理菜单已存在，跳过添加")
            return
        
        # 查找系统管理下最大的sort值
        stmt = select(Menu).where(
            Menu.parent_id == system_menu.id,
            Menu.is_deleted == False
        )
        result = await db.execute(stmt)
        children = result.scalars().all()
        max_sort = max([m.sort for m in children], default=0) if children else 0
        
        # 创建字典管理菜单
        dict_menu = Menu(
            name="dict",
            title="字典管理",
            path="/system/dict",
            component="system/dict/index",
            icon="file-text",
            sort=max_sort + 1,
            type=2,  # Menu
            permission_code="dict:list",
            parent_id=system_menu.id,
            tenant_id=system_menu.tenant_id,
            status=1,
            visible=1,
            is_cache=0,
            is_external=0,
        )
        
        db.add(dict_menu)
        await db.commit()
        await db.refresh(dict_menu)
        
        print(f"✅ 成功添加字典管理菜单: {dict_menu.title} (ID: {dict_menu.id})")
        print(f"   路径: {dict_menu.path}")
        print(f"   权限码: {dict_menu.permission_code}")


if __name__ == "__main__":
    print("🌱 添加字典管理菜单...")
    asyncio.run(add_dict_menu())

