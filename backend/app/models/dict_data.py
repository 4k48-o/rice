"""
Dictionary data model for system dictionaries.
"""
from typing import Optional
from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TenantMixin


class DictData(BaseModel, TenantMixin):
    """Dictionary data model."""
    
    __tablename__ = "dict_data"
    __table_args__ = {"comment": "字典数据表"}
    
    # Foreign key
    dict_type_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="字典类型ID"
    )
    
    # Basic info
    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="字典标签(显示文本)"
    )
    value: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="字典值"
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
    
    # Extended display fields
    css_class: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="CSS类名"
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="颜色值"
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="图标"
    )
    
    def __repr__(self) -> str:
        return f"<DictData(id={self.id}, label={self.label}, value={self.value})>"

