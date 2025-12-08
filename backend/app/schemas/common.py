"""
Common Pydantic schemas.
"""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


class ResponseBase(BaseModel):
    """Base response model."""
    
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    timestamp: int = Field(description="时间戳")


class Response(ResponseBase):
    """Standard response model."""
    
    data: Optional[Any] = Field(None, description="响应数据")


T = TypeVar("T")


class DataResponse(ResponseBase, Generic[T]):
    """Generic data response model."""
    
    data: Optional[T] = Field(None, description="响应数据")


class PageData(BaseModel, Generic[T]):
    """Pagination data model."""
    
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页")
    page_size: int = Field(20, description="每页数量")
    total_pages: int = Field(0, description="总页数")


class PageResponse(ResponseBase):
    """Pagination response model."""
    
    data: Optional[PageData] = Field(None, description="分页数据")


class ErrorDetail(BaseModel):
    """Error detail model."""
    
    field: str = Field(description="错误字段")
    message: str = Field(description="错误消息")


class ErrorResponse(ResponseBase):
    """Error response model."""
    
    data: None = None
    errors: Optional[List[ErrorDetail]] = Field(None, description="错误详情")


class PageParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """Calculate offset."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit."""
        return self.page_size
