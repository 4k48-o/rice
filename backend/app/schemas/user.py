"""
User schemas.
"""
import re
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from app.schemas.common import PageParams, Response
from app.core import security
from app.core.exceptions import BusinessException


class UserBase(BaseModel):
    """Base User schema."""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    dept_id: Optional[str] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    gender: Optional[int] = Field(0, description="性别:0未知,1男,2女")
    status: Optional[int] = Field(1, description="状态:0禁用,1正常")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (1[3-9]\d{9})."""
        if v is None or v == "":
            return v
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("Invalid phone number format. Must be 11 digits starting with 1[3-9].")
        return v


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., description="密码")
    role_ids: Optional[List[str]] = Field(None, description="角色ID列表")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not security.validate_password_strength(v):
            raise ValueError("Password is too weak. Must be at least 8 chars, incl. upper, lower, digit, special.")
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    dept_id: Optional[str] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    gender: Optional[int] = Field(None, description="性别:0未知,1男,2女")
    status: Optional[int] = Field(None, description="状态:0禁用,1正常")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    role_ids: Optional[List[str]] = Field(None, description="角色ID列表")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (1[3-9]\d{9})."""
        if v is None or v == "":
            return v
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("Invalid phone number format. Must be 11 digits starting with 1[3-9].")
        return v


class UserResponse(UserBase):
    """User response schema."""
    id: str
    user_type: int
    avatar: Optional[str]
    created_at: datetime
    last_login_time: Optional[datetime]
    role_ids: Optional[List[str]] = Field(default_factory=list, description="角色ID列表")
    roles: Optional[List[dict]] = Field(default_factory=list, description="角色详细信息")
    dept_name: Optional[str] = Field(None, description="部门名称")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema."""
    total: int
    items: List[UserResponse]


class UserPasswordUpdate(BaseModel):
    """User password update schema."""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not security.validate_password_strength(v):
            raise ValueError("Password is too weak")
        return v
