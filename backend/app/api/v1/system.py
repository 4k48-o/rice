"""
System initialization API.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.common import Response
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/init", response_model=Response)
async def init_system_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize system data (create admin user).
    
    This endpoint should be called once when the application starts.
    It checks if the admin user exists, and creates it if not.
    """
    import time
    current_time = int(time.time())
    
    # Check if admin exists
    stmt = select(User).where(User.username == "admin")
    result = await db.execute(stmt)
    existing_admin = result.scalar_one_or_none()
    
    if existing_admin:
        return Response(
            code=400,
            message="System already initialized (admin user exists)",
            timestamp=current_time
        )
    
    # Initialize Snowflake if needed (usually done in main.py, but safe to ensure)
    # We assume app startup has handles global init, so we just focus on DB data
    
    # Create admin user
    # Password should be set via environment variable ADMIN_PASSWORD
    # If not set, use a default (ONLY for development!)
    import os
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # Change in production!
    
    admin = User(
        username="admin",
        password=get_password_hash(admin_password),
        email="admin@example.com",
        real_name="Super Admin",
        user_type=0,  # Superadmin
        status=1,
        tenant_id=0  # System tenant
    )
    db.add(admin)
    
    try:
        await db.commit()
        await db.refresh(admin)
        
        return Response(
            code=200,
            message="System initialized successfully",
            data={
                "username": admin.username,
                "user_id": str(admin.id)
            },
            timestamp=current_time
        )
    except Exception as e:
        await db.rollback()
        return Response(
            code=500,
            message=f"Initialization failed: {str(e)}",
            timestamp=current_time
        )
