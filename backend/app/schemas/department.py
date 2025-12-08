"""
Department schemas for request/response.
"""
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_serializer


class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., description="部门名称")
    code: str = Field(..., description="部门编码")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    leader_id: Optional[int] = Field(None, description="部门负责人ID")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1启用")
    
    @field_serializer('parent_id', 'leader_id')
    def serialize_large_int(self, value: Optional[int], _info) -> Optional[Union[str, int]]:
        """Convert large integers to strings to avoid JavaScript precision loss."""
        if value is None:
            return None
        # JavaScript Number.MAX_SAFE_INTEGER is 2^53 - 1 = 9007199254740991
        if abs(value) > 9007199254740991:
            return str(value)
        return value


class DepartmentCreate(DepartmentBase):
    """Schema for creating department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department."""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    leader_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    """Schema for department response."""
    id: int
    tenant_id: int
    leader_name: Optional[str] = Field(None, description="负责人姓名")
    
    @field_serializer('id', 'tenant_id')
    def serialize_id(self, value: int, _info) -> Union[str, int]:
        """Convert large integers to strings to avoid JavaScript precision loss."""
        # JavaScript Number.MAX_SAFE_INTEGER is 2^53 - 1 = 9007199254740991
        if abs(value) > 9007199254740991:
            return str(value)
        return value
    
    class Config:
        from_attributes = True


class DepartmentTreeNode(DepartmentResponse):
    """Department tree node with children."""
    children: List["DepartmentTreeNode"] = Field(default_factory=list, description="子部门")
    
    class Config:
        from_attributes = True
