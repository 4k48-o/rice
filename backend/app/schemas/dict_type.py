"""
Dictionary type schemas for request/response.
"""
from typing import Optional
from pydantic import BaseModel, Field


class DictTypeBase(BaseModel):
    """Base dictionary type schema."""
    name: str = Field(..., description="字典类型名称")
    code: str = Field(..., description="字典类型编码")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1启用")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeCreate(DictTypeBase):
    """Schema for creating dictionary type."""
    pass


class DictTypeUpdate(BaseModel):
    """Schema for updating dictionary type."""
    name: Optional[str] = None
    code: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class DictTypeResponse(DictTypeBase):
    """Schema for dictionary type response."""
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True

