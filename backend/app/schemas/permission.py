"""
Permission schemas for request/response.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限标识,如user:list")
    type: int = Field(1, description="类型:1菜单,2按钮,3API")
    parent_id: Optional[int] = Field(None, description="父权限ID")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1启用")


class PermissionCreate(PermissionBase):
    """Schema for creating permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating permission."""
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[int] = None
    parent_id: Optional[int] = None
    sort: Optional[int] = None
    status: Optional[int] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: int
    tenant_id: int
    
    class Config:
        from_attributes = True


class PermissionTreeNode(PermissionResponse):
    """Permission tree node with children."""
    children: List["PermissionTreeNode"] = Field(default_factory=list, description="子权限")
    
    class Config:
        from_attributes = True
