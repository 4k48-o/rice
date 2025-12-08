"""
Menu schemas for request/response.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class MenuBase(BaseModel):
    """Base menu schema."""
    name: str = Field(..., description="菜单名称")
    title: str = Field(..., description="菜单标题")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    redirect: Optional[str] = Field(None, description="重定向路径")
    icon: Optional[str] = Field(None, description="图标")
    sort: int = Field(0, description="排序")
    type: int = Field(1, description="类型:1目录,2菜单,3按钮")
    permission_code: Optional[str] = Field(None, description="权限标识")
    status: int = Field(1, description="状态:0禁用,1启用")
    visible: int = Field(1, description="是否可见:0隐藏,1显示")
    is_cache: int = Field(0, description="是否缓存:0否,1是")
    is_external: int = Field(0, description="是否外链:0否,1是")


class MenuCreate(MenuBase):
    """Schema for creating menu."""
    pass


class MenuUpdate(BaseModel):
    """Schema for updating menu."""
    name: Optional[str] = None
    title: Optional[str] = None
    parent_id: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    icon: Optional[str] = None
    sort: Optional[int] = None
    type: Optional[int] = None
    permission_code: Optional[str] = None
    status: Optional[int] = None
    visible: Optional[int] = None
    is_cache: Optional[int] = None
    is_external: Optional[int] = None


class MenuResponse(MenuBase):
    """Schema for menu response."""
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


class MenuTreeNode(MenuResponse):
    """Menu tree node with children."""
    children: List["MenuTreeNode"] = Field(default_factory=list, description="子菜单")
    
    class Config:
        from_attributes = True
