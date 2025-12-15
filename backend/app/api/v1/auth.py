"""
Authentication API endpoints.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, security
from app.api import deps
from app.core.config import settings
from app.core.i18n import i18n
from app.models.user import User
from app.schemas import LoginRequest, TokenResponse, Response
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.services.log_service import LogService
from app.utils.ip import IPUtils

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Response)
async def login(
    login_data: LoginRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    User login endpoint.
    """
    ip = IPUtils.get_ip(request)
    user_agent = request.headers.get("user-agent", "")
    
    # Authenticate and generate tokens
    user = await user_service.get_by_username(db, login_data.username)

    if not user:
        # Log failure (User not found)
        await LogService.create_login_log(
            username=login_data.username,
            status=0,
            ip=ip,
            msg="用户不存在",
            user_agent=user_agent
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t("login_failed")
        )
    
    if not security.verify_password(login_data.password, user.password):
        # Log failure (Password mismatch)
        await LogService.create_login_log(
            username=login_data.username,
            status=0,
            ip=ip,
            user_id=user.id,
            msg="密码错误",
            user_agent=user_agent,
            tenant_id=user.tenant_id
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=i18n.t("login_failed")
        )
    
    if user.status != 1:
        # Log failure (User disabled)
        await LogService.create_login_log(
            username=login_data.username,
            status=0,
            ip=ip,
            user_id=user.id,
            msg="账号已禁用",
            user_agent=user_agent,
            tenant_id=user.tenant_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=i18n.t("user_inactive")
        )

    # Check password expiration
    if security.is_password_expired(user.password_updated_at):
         # Log success but warn (or strictly failure? typically success but forces change)
         # Let's count as success login but prompt change
        background_tasks.add_task(
            LogService.create_login_log,
            username=login_data.username,
            status=1,
            ip=ip,
            user_id=user.id,
            msg="密码过期需重置",
            user_agent=user_agent,
            tenant_id=user.tenant_id
        )
        return {
            "code": 10003, # Password Expired
            "message": i18n.t("password_expired"),
            "data": {"must_change_password": True},
            "timestamp": int(time.time())
        }

    # Update user's last login time and IP
    user.last_login_time = datetime.now()
    user.last_login_ip = ip
    user.login_count = (user.login_count or 0) + 1
    await db.commit()
    
    token_data = await auth_service.create_tokens(db, user.id)
    
    # Log success
    background_tasks.add_task(
        LogService.create_login_log,
        username=login_data.username,
        status=1,
        ip=ip,
        user_id=user.id,
        msg="登录成功",
        user_agent=user_agent,
        tenant_id=user.tenant_id
    )
    
    return {
        "code": 200,
        "message": i18n.t("login_success"),
        "data": token_data.model_dump(),
        "timestamp": int(time.time()),
    }


@router.post("/refresh", response_model=Response)
async def refresh_token(
    refresh_token: str, # TODO: Use a Pydantic model for body
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token.
    """
    token_data = await auth_service.refresh_token(db, refresh_token)
    
    return {
        "code": 200,
        "message": "Token refreshed successfully",
        "data": token_data,
        "timestamp": int(time.time()),
    }


@router.post("/logout", response_model=Response)
async def logout(
    request: Request,
    current_user: User = Depends(deps.get_current_user),
):
    """
    User logout endpoint.
    Blacklists the current access token and clears user session.
    """
    from app.core.security import blacklist_token, decode_token, get_token_expiry_seconds
    
    # Get token from authorization header
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    token = auth_header.replace("Bearer ", "")
    
    # Decode token to get expiry time
    payload = decode_token(token)
    if payload:
        # Add token to blacklist with remaining TTL
        expires_in = get_token_expiry_seconds(payload)
        if expires_in > 0:
            await blacklist_token(token, expires_in)
    
    # Clear user session in Redis (if single session mode is enabled)
    if settings.SINGLE_SESSION_MODE:
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        await redis.delete(f"user_session:{current_user.id}")
    
    return {
        "code": 200,
        "message": "Logout successful",
        "data": None,
        "timestamp": int(time.time()),
    }


@router.get("/user-info", response_model=Response)
async def get_user_info(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user information including roles and permissions.
    """
    from app.core.permissions import get_user_permissions, get_user_roles, get_user_data_scope
    from app.services.user_service import user_service
    
    # Get user roles with details
    roles = await user_service.get_user_roles(db, current_user.id)
    roles_data = [
        {
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "data_scope": role.data_scope
        }
        for role in roles
    ]
    
    # Get user permissions (uses cache)
    if current_user.user_type == 0:
        # Super admin has all permissions
        permissions = ["*"]
    else:
        user_permissions = await get_user_permissions(db, current_user)
        permissions = sorted(list(user_permissions))
    
    # Get data scope
    data_scope = await get_user_data_scope(db, current_user)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "real_name": current_user.real_name,
            "avatar": current_user.avatar,
            "tenant_id": current_user.tenant_id,
            "user_type": current_user.user_type,
            "roles": roles_data,
            "permissions": permissions,
            "data_scope": data_scope.value
        },
        "timestamp": int(time.time()),
    }
