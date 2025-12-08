"""
Role schemas for request/response.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色编码")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1正常")
    data_scope: int = Field(1, description="数据权限:1全部,2本部门及以下,3本部门,4仅本人")


class RoleCreate(RoleBase):
    """Schema for creating role."""
    permission_ids: List[int] = Field(default_factory=list, description="权限ID列表")


class RoleUpdate(BaseModel):
    """Schema for updating role."""
    name: Optional[str] = None
    code: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None
    data_scope: Optional[int] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: int
    tenant_id: int
    
    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Role with permission list."""
    permissions: List["PermissionResponse"] = Field(default_factory=list, description="权限列表")
    
    class Config:
        from_attributes = True


# Forward reference for PermissionResponse
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.permission import PermissionResponse
