"""
Authentication schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""
    
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    tenant_code: Optional[str] = Field(None, max_length=50, description="租户编码")
    captcha_code: Optional[str] = Field(None, max_length=10, description="验证码")
    captcha_key: Optional[str] = Field(None, description="验证码key")


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str = Field(description="访问令牌")
    token_type: str = Field("Bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间(秒)")
    refresh_token: str = Field(description="刷新令牌")
    user_info: dict = Field(description="用户信息")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="刷新令牌")


class UserInfo(BaseModel):
    """User info schema."""
    
    id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    dept_id: Optional[int] = None
    dept_name: Optional[str] = None
    roles: List[dict] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
