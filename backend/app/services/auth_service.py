"""
Authentication service.
"""
from datetime import timedelta
from typing import Optional, Tuple

from jose import jwt, JWTError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.core import decode_token
from app.api import deps
from app.services.user_service import user_service
from app.schemas import TokenResponse
from app.core.security import verify_password, create_access_token, create_refresh_token


class AuthService:
    """Authentication business logic."""
    
    @staticmethod
    async def authenticate(
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user.
        
        Args:
            db: Database session
            username: Username
            password: Password
            
        Returns:
            Optional[User]: Authenticated user or None
        """
        user = await user_service.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if user.status != 1: # 1: normal
            # Account locked or disabled
            return None
        return user
    
    @staticmethod
    async def login(
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> dict:
        """
        Login user and generate tokens.
        
        Args:
            db: Database session
            username: Username
            password: Password
            
        Returns:
            dict: Token response data
            
        Raises:
            HTTPException: If authentication fails
        """
        user = await AuthService.authenticate(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Update login info (last login time, ip, etc)
        # Update login info
        user.last_login_ip = "127.0.0.1" # TODO: Get from request
        user.last_login_time = datetime.now()
        await db.commit()
        
        return await AuthService.create_tokens(db, user.id)

    @staticmethod
    async def create_tokens(db: AsyncSession, user_id: str) -> TokenResponse:
        """Create access and refresh tokens for user."""
        user = await user_service.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        claims = {
            "sub": str(user.id),
            "username": user.username,
            "tenant_id": user.tenant_id,
            "type": "access"
        }
        access_token = create_access_token(
            data=claims, expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data={"sub": str(user_id), "type": "refresh"}, 
            expires_delta=refresh_token_expires
        )
        
        # Redis Single Session Storage
        if getattr(settings, "SINGLE_SESSION_MODE", True):
            from app.core.redis import RedisClient
            redis = RedisClient.get_client()
            await redis.set(
                f"user_session:{user.id}", 
                access_token, 
                ex=int(access_token_expires.total_seconds())
            )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user_info={
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "avatar": user.avatar,
                "tenant_id": user.tenant_id
            }
        )

    @staticmethod
    async def refresh_token(
        db: AsyncSession, 
        refresh_token: str
    ) -> dict:
        """
        Refresh access token.
        
        Args:
            db: Database session
            refresh_token: Refresh token string
            
        Returns:
            dict: New token data
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                refresh_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            token_type = payload.get("type")
            if token_type != "refresh":
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
            
        # Verify user still exists and valid
        # user_id is now a string
        user = await user_service.get_by_id(db, user_id)
        if not user or user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
            
        # Create new access token
        claims = {
            "sub": str(user.id),
            "username": user.username,
            "tenant_id": user.tenant_id,
            "type": "access"
        }
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data=claims, expires_delta=access_token_expires)
        
        # Update Redis session if single session mode is enabled
        if getattr(settings, "SINGLE_SESSION_MODE", False):
            from app.core.redis import RedisClient
            redis = RedisClient.get_client()
            await redis.set(
                f"user_session:{user.id}",
                access_token,
                ex=int(access_token_expires.total_seconds())
            )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token, # Return same refresh token
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

# Global instance
auth_service = AuthService()
