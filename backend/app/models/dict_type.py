"""
Dictionary type model for system dictionaries.
"""
from typing import Optional
from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TenantMixin


class DictType(BaseModel, TenantMixin):
    """Dictionary type model."""
    
    __tablename__ = "dict_types"
    __table_args__ = {"comment": "字典类型表"}
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="字典类型名称"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="字典类型编码(唯一)"
    )
    
    # Display
    sort: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="排序(升序)"
    )
    
    # Status
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1启用"
    )
    
    def __repr__(self) -> str:
        return f"<DictType(id={self.id}, name={self.name}, code={self.code})>"

