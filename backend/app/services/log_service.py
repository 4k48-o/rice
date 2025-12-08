"""
Log service.
"""
from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import Request

from app.core.database import AsyncSessionLocal
from app.models.log import LoginLog, OperationLog
from app.utils.ip import IPUtils


class LogService:
    """Log service."""
    
    @staticmethod
    async def create_login_log(
        username: str,
        status: int,
        ip: str,
        user_id: Optional[int] = None,
        msg: Optional[str] = None,
        user_agent: str = None,
        tenant_id: int = 0
    ) -> None:
        """
        Create login log asynchronously.
        
        Should be called in background task.
        """
        location = IPUtils.get_location(ip)
        # Parse UA simply
        os = "Unknown"
        browser = "Unknown"
        if user_agent:
            # Simple heuristic
            if "Windows" in user_agent:
                os = "Windows"
            elif "Mac" in user_agent:
                os = "Mac OS"
            elif "Linux" in user_agent:
                os = "Linux"
            elif "Android" in user_agent:
                os = "Android"
            elif "iPhone" in user_agent or "iPad" in user_agent:
                os = "iOS"
                
            if "Chrome" in user_agent:
                browser = "Chrome"
            elif "Firefox" in user_agent:
                browser = "Firefox"
            elif "Safari" in user_agent:
                browser = "Safari"
            elif "Edge" in user_agent:
                browser = "Edge"
            
        
        async with AsyncSessionLocal() as db:
            try:
                log = LoginLog(
                    username=username,
                    user_id=user_id,
                    status=status,
                    ip=ip,
                    location=location,
                    msg=msg,
                    browser=browser,
                    os=os,
                    tenant_id=tenant_id
                )
                db.add(log)
                await db.commit()
            except Exception as e:
                # Log system error, don't crash
                print(f"Error writing login log: {e}")
                await db.rollback()
                
    @staticmethod
    async def create_operation_log(
        username: str,
        method: str,
        url: str,
        ip: str,
        user_agent: str,
        status: int,
        duration: int,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        summary: Optional[str] = None,
        params: Optional[dict] = None,
        result: Optional[dict] = None,
        error_msg: Optional[str] = None,
        tenant_id: int = 0
    ) -> None:
        """
        Create operation log asynchronously.
        """
        location = IPUtils.get_location(ip)
        
        async with AsyncSessionLocal() as db:
            try:
                log = OperationLog(
                    username=username,
                    user_id=user_id,
                    module=module,
                    summary=summary,
                    method=method,
                    url=url,
                    ip=ip,
                    location=location,
                    user_agent=user_agent,
                    params=params,
                    result=result,
                    status=status,
                    error_msg=error_msg,
                    duration=duration,
                    tenant_id=tenant_id
                )
                db.add(log)
                await db.commit()
            except Exception as e:
                print(f"Error writing operation log: {e}")

    @staticmethod
    async def get_login_logs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        status: Optional[int] = None,
        ip: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tenant_id: Optional[int] = None
    ) -> Tuple[List[LoginLog], int]:
        """
        Get login logs with filters.
        
        Args:
            db: Database session
            page: Page number
            page_size: Page size
            username: Filter by username
            status: Filter by status (1=success, 0=failed)
            ip: Filter by IP
            start_time: Start time filter
            end_time: End time filter
            tenant_id: Tenant ID filter
            
        Returns:
            Tuple of (logs list, total count)
        """
        stmt = select(LoginLog).where(LoginLog.is_deleted == False)
        
        # Apply filters
        if tenant_id is not None:
            stmt = stmt.where(LoginLog.tenant_id == tenant_id)
        
        if username:
            stmt = stmt.where(LoginLog.username.ilike(f"%{username}%"))
        
        if status is not None:
            stmt = stmt.where(LoginLog.status == status)
        
        if ip:
            stmt = stmt.where(LoginLog.ip.ilike(f"%{ip}%"))
        
        if start_time:
            stmt = stmt.where(LoginLog.login_time >= start_time)
        
        if end_time:
            stmt = stmt.where(LoginLog.login_time <= end_time)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        stmt = stmt.order_by(LoginLog.login_time.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        return list(logs), total

    @staticmethod
    async def get_operation_logs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        module: Optional[str] = None,
        status: Optional[int] = None,
        method: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tenant_id: Optional[int] = None
    ) -> Tuple[List[OperationLog], int]:
        """
        Get operation logs with filters.
        
        Args:
            db: Database session
            page: Page number
            page_size: Page size
            username: Filter by username
            module: Filter by module
            status: Filter by status (1=success, 0=failed)
            method: Filter by HTTP method
            start_time: Start time filter
            end_time: End time filter
            tenant_id: Tenant ID filter
            
        Returns:
            Tuple of (logs list, total count)
        """
        stmt = select(OperationLog).where(OperationLog.is_deleted == False)
        
        # Apply filters
        if tenant_id is not None:
            stmt = stmt.where(OperationLog.tenant_id == tenant_id)
        
        if username:
            stmt = stmt.where(OperationLog.username.ilike(f"%{username}%"))
        
        if module:
            stmt = stmt.where(OperationLog.module.ilike(f"%{module}%"))
        
        if status is not None:
            stmt = stmt.where(OperationLog.status == status)
        
        if method:
            stmt = stmt.where(OperationLog.method == method)
        
        if start_time:
            stmt = stmt.where(OperationLog.created_at >= start_time)
        
        if end_time:
            stmt = stmt.where(OperationLog.created_at <= end_time)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        stmt = stmt.order_by(OperationLog.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        return list(logs), total

    @staticmethod
    async def get_online_users(
        db: AsyncSession,
        tenant_id: Optional[int] = None
    ) -> List[dict]:
        """
        Get online users from Redis.
        
        Args:
            db: Database session
            tenant_id: Tenant ID filter
            
        Returns:
            List of online user info
        """
        from app.core.redis import RedisClient
        from app.models.user import User
        from sqlalchemy import select
        
        redis = RedisClient.get_client()
        online_users = []
        
        # Get all session keys from Redis
        pattern = "user_session:*"
        keys = []
        async for key in redis.scan_iter(match=pattern):
            keys.append(key)
        
        # Extract user IDs and get user info
        user_ids = []
        for key in keys:
            try:
                user_id = int(key.decode().split(":")[1])
                user_ids.append(user_id)
            except (ValueError, IndexError):
                continue
        
        if not user_ids:
            return []
        
        # Get user info from database
        stmt = select(User).where(
            User.id.in_(user_ids),
            User.is_deleted == False
        )
        if tenant_id is not None:
            stmt = stmt.where(User.tenant_id == tenant_id)
        
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        # Build online user list
        for user in users:
            session_key = f"user_session:{user.id}"
            token = await redis.get(session_key)
            ttl = await redis.ttl(session_key)
            
            # Get login log for this user
            login_log_stmt = select(LoginLog).where(
                LoginLog.user_id == user.id,
                LoginLog.status == 1
            ).order_by(LoginLog.login_time.desc()).limit(1)
            
            login_result = await db.execute(login_log_stmt)
            login_log = login_result.scalar_one_or_none()
            
            online_users.append({
                "user_id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "ip": login_log.ip if login_log else None,
                "location": login_log.location if login_log else None,
                "login_time": login_log.login_time if login_log else None,
                "last_active_time": datetime.now(),  # TODO: Track last active time
            })
        
        return online_users
