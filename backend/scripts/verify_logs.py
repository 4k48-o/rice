import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.log import LoginLog, OperationLog
from sqlalchemy import select, func

async def verify_logs():
    async with AsyncSessionLocal() as db:
        # Check login logs
        stmt = select(func.count()).select_from(LoginLog)
        login_count = (await db.execute(stmt)).scalar()
        print(f"Login Logs Count: {login_count}")
        
        if login_count > 0:
            last_login = (await db.execute(select(LoginLog).order_by(LoginLog.id.desc()).limit(1))).scalar_one()
            print(f"Last Login Log: User={last_login.username}, Status={last_login.status}, Msg={last_login.msg}")

        # Check operation logs
        stmt = select(func.count()).select_from(OperationLog)
        opt_count = (await db.execute(stmt)).scalar()
        print(f"Operation Logs Count: {opt_count}")
        
        if opt_count > 0:
            last_opt = (await db.execute(select(OperationLog).order_by(OperationLog.id.desc()).limit(1))).scalar_one()
            print(f"Last Operation Log: Method={last_opt.method}, URL={last_opt.url}, Status={last_opt.status}")

if __name__ == "__main__":
    asyncio.run(verify_logs())
