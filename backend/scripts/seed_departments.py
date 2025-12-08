"""
Seed data script for initial departments.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.department import Department


async def seed_departments():
    """Seed initial department data."""
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    from app.core.config import settings
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    
    async with AsyncSessionLocal() as db:
        # Check if departments already exist
        stmt = select(Department).limit(1)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print("⚠️  Departments already exist, skipping seed")
            return
        
        # Default tenant_id (adjust as needed)
        tenant_id = 0
        
        # Define department structure
        departments = [
            {
                "name": "总经办",
                "code": "CEO_OFFICE",
                "sort": 1,
                "tenant_id": tenant_id,
                "children": []
            },
            {
                "name": "技术部",
                "code": "TECH",
                "sort": 2,
                "tenant_id": tenant_id,
                "children": [
                    {
                        "name": "研发组",
                        "code": "TECH_DEV",
                        "sort": 1,
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "测试组",
                        "code": "TECH_QA",
                        "sort": 2,
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "运维组",
                        "code": "TECH_OPS",
                        "sort": 3,
                        "tenant_id": tenant_id,
                    },
                ]
            },
            {
                "name": "市场部",
                "code": "MARKETING",
                "sort": 3,
                "tenant_id": tenant_id,
                "children": [
                    {
                        "name": "销售组",
                        "code": "MARKETING_SALES",
                        "sort": 1,
                        "tenant_id": tenant_id,
                    },
                    {
                        "name": "推广组",
                        "code": "MARKETING_PROMO",
                        "sort": 2,
                        "tenant_id": tenant_id,
                    },
                ]
            },
            {
                "name": "人事部",
                "code": "HR",
                "sort": 4,
                "tenant_id": tenant_id,
                "children": []
            },
            {
                "name": "财务部",
                "code": "FINANCE",
                "sort": 5,
                "tenant_id": tenant_id,
                "children": []
            },
        ]
        
        # Insert departments
        async def insert_department(dept_data, parent_id=None):
            """Recursively insert department and children."""
            children = dept_data.pop("children", [])
            dept_data["parent_id"] = parent_id
            
            dept = Department(**dept_data)
            db.add(dept)
            await db.flush()
            await db.refresh(dept)
            
            print(f"✅ Created department: {dept.name} (ID: {dept.id})")
            
            # Insert children
            for child_data in children:
                await insert_department(child_data, dept.id)
        
        for dept_data in departments:
            await insert_department(dept_data)
        
        await db.commit()
        print(f"\n🎉 Successfully seeded {len(departments)} top-level departments!")


if __name__ == "__main__":
    print("🌱 Seeding department data...")
    asyncio.run(seed_departments())
