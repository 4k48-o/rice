import asyncio
import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal

async def check_tables():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"))
        tables = result.scalars().all()
        print("Tables in DB:")
        for t in tables:
            print(f"- {t}")

if __name__ == "__main__":
    asyncio.run(check_tables())
