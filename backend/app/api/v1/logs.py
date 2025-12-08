"""
Log query API endpoints.
"""
from typing import Optional
from datetime import datetime
import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api import deps
from app.models.user import User
from app.schemas.log import LoginLogResponse, OperationLogResponse, OnlineUserResponse
from app.schemas.common import Response, PageResponse
from app.services.log_service import LogService
from app.core.i18n import i18n

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/login", response_model=Response)
async def get_login_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    status: Optional[int] = Query(None, description="状态:1成功,0失败"),
    ip: Optional[str] = Query(None, description="IP地址"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(deps.require_permissions("log:login:list")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get login logs.
    
    Requires permission: log:login:list
    """
    logs, total = await LogService.get_login_logs(
        db,
        page=page,
        page_size=page_size,
        username=username,
        status=status,
        ip=ip,
        start_time=start_time,
        end_time=end_time,
        tenant_id=current_user.tenant_id if current_user.user_type != 0 else None
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": [LoginLogResponse.model_validate(log) for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "timestamp": int(time.time()),
    }


@router.get("/operation", response_model=Response)
async def get_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    module: Optional[str] = Query(None, description="功能模块"),
    status: Optional[int] = Query(None, description="状态:1成功,0失败"),
    method: Optional[str] = Query(None, description="HTTP方法"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    current_user: User = Depends(deps.require_permissions("log:operation:list")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get operation logs.
    
    Requires permission: log:operation:list
    """
    logs, total = await LogService.get_operation_logs(
        db,
        page=page,
        page_size=page_size,
        username=username,
        module=module,
        status=status,
        method=method,
        start_time=start_time,
        end_time=end_time,
        tenant_id=current_user.tenant_id if current_user.user_type != 0 else None
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": [OperationLogResponse.model_validate(log) for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "timestamp": int(time.time()),
    }


@router.get("/online", response_model=Response)
async def get_online_users(
    current_user: User = Depends(deps.require_permissions("log:online:list")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get online users.
    
    Requires permission: log:online:list
    """
    users = await LogService.get_online_users(
        db,
        tenant_id=current_user.tenant_id if current_user.user_type != 0 else None
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": [OnlineUserResponse.model_validate(user) for user in users],
        "timestamp": int(time.time()),
    }


@router.post("/online/{user_id}/force-logout", response_model=Response)
async def force_logout_user(
    user_id: int,
    current_user: User = Depends(deps.require_permissions("log:online:force-logout")),
    db: AsyncSession = Depends(get_db),
):
    """
    Force logout a user.
    
    Requires permission: log:online:force-logout
    """
    from app.core.redis import RedisClient
    
    redis = RedisClient.get_client()
    session_key = f"user_session:{user_id}"
    
    # Delete session from Redis
    await redis.delete(session_key)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": None,
        "timestamp": int(time.time()),
    }

