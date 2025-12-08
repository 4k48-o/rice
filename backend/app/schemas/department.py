"""
Department schemas for request/response.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., description="部门名称")
    code: str = Field(..., description="部门编码")
    parent_id: Optional[str] = Field(None, description="父部门ID")
    leader_id: Optional[str] = Field(None, description="部门负责人ID")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1启用")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DepartmentCreate(DepartmentBase):
    """Schema for creating department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department."""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DepartmentResponse(DepartmentBase):
    """Schema for department response."""
    id: str
    tenant_id: str
    leader_name: Optional[str] = Field(None, description="负责人姓名")
    
    class Config:
        from_attributes = True


class DepartmentTreeNode(DepartmentResponse):
    """Department tree node with children."""
    children: List["DepartmentTreeNode"] = Field(default_factory=list, description="子部门")
    
    class Config:
        from_attributes = True
