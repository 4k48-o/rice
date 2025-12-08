"""
API dependencies.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, decode_token
from app.core.config import settings
from app.models import User

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Query user from database
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
        
    user = await db.get(User, user_id_int)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    # Single Session Check
    if settings.SINGLE_SESSION_MODE:
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        active_token = await redis.get(f"user_session:{user.id}")
        
        if active_token and active_token != token:
            from app.core.i18n import i18n
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=i18n.t("account_logged_in_elsewhere"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    # Check if user is active
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User inactive or disabled",
        )
        
    # Store user in request state for middleware access (e.g. logging)
    # Also store user attributes separately to avoid detached instance errors
    request.state.user = user
    request.state.user_id = user.id
    request.state.username = user.username
    request.state.tenant_id = user.tenant_id
    return user



def require_permissions(*permissions: str):
    """
    Dependency to require specific permissions.
    
    Args:
        *permissions: Required permission codes
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """Check if user has required permissions."""
        from app.core.permissions import get_user_permissions
        
        # Superadmin bypasses permission check
        if current_user.user_type == 0:
            return current_user
        
        # Get user's permissions
        user_permissions = await get_user_permissions(db, current_user)
        
        # Check if user has all required permissions
        missing_permissions = set(permissions) - user_permissions
        if missing_permissions:
            from app.core.i18n import i18n
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=i18n.t("forbidden")
            )
        
        return current_user
    
    return permission_checker
