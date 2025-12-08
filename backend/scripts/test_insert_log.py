import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.log import LoginLog
from app.utils.snowflake import init_snowflake
from app.core.config import settings

async def test_insert():
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    async with AsyncSessionLocal() as db:
        log = LoginLog(
            username="test_script",
            status=1,
            ip="127.0.0.1",
            msg="Script Test",
            login_time=datetime.now(),
            tenant_id=0
        )
        db.add(log)
        try:
            await db.commit()
            print("Successfully inserted login log!")
        except Exception as e:
            print(f"Failed to insert: {e}")

if __name__ == "__main__":
    asyncio.run(test_insert())
