"""
Log schemas.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class LoginLogResponse(BaseModel):
    """Login log response schema."""
    
    id: str
    user_id: Optional[str] = None
    username: str
    status: int = Field(description="状态:1成功,0失败")
    ip: Optional[str] = None
    location: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    msg: Optional[str] = None
    login_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class OperationLogResponse(BaseModel):
    """Operation log response schema."""
    
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    module: Optional[str] = None
    summary: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    ip: Optional[str] = None
    location: Optional[str] = None
    user_agent: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    status: int = Field(description="状态:1成功,0失败")
    error_msg: Optional[str] = None
    duration: int = Field(description="耗时(ms)")
    created_at: datetime
    
    class Config:
        from_attributes = True


class OnlineUserResponse(BaseModel):
    """Online user response schema."""
    
    user_id: str
    username: str
    real_name: Optional[str] = None
    ip: Optional[str] = None
    location: Optional[str] = None
    login_time: datetime
    last_active_time: datetime

