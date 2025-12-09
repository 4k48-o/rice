"""
Dictionary data schemas for request/response.
"""
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.dict_type import DictTypeResponse


class DictDataBase(BaseModel):
    """Base dictionary data schema."""
    dict_type_id: str = Field(..., description="字典类型ID")
    label: str = Field(..., description="字典标签(显示文本)")
    value: str = Field(..., description="字典值")
    sort: int = Field(0, description="排序")
    status: int = Field(1, description="状态:0禁用,1启用")
    css_class: Optional[str] = Field(None, description="CSS类名")
    color: Optional[str] = Field(None, description="颜色值")
    icon: Optional[str] = Field(None, description="图标")
    remark: Optional[str] = Field(None, description="备注")


class DictDataCreate(DictDataBase):
    """Schema for creating dictionary data."""
    pass


class DictDataUpdate(BaseModel):
    """Schema for updating dictionary data."""
    dict_type_id: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None
    css_class: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    remark: Optional[str] = None


class DictDataResponse(DictDataBase):
    """Schema for dictionary data response."""
    id: str
    tenant_id: str
    dict_type: Optional[DictTypeResponse] = Field(None, description="字典类型信息")
    
    class Config:
        from_attributes = True

