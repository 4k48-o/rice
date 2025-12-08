"""
Department model for organizational structure.
"""
from typing import Optional
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TenantMixin


class Department(BaseModel, TenantMixin):
    """Department model for organizational hierarchy."""
    
    __tablename__ = "departments"
    __table_args__ = {"comment": "部门表"}
    
    # Parent relationship
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="父部门ID,NULL表示顶级部门"
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="部门名称"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="部门编码"
    )
    
    # Leader
    leader_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="部门负责人ID"
    )
    
    # Contact
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱"
    )
    
    # Display
    sort: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="排序(升序)"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1启用"
    )
    
    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name={self.name})>"
