"""
Tenant model.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, SmallInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Tenant(BaseModel):
    """Tenant model.
    
    注意：Tenant 不继承 TenantMixin，因为它本身就是租户实体。
    ID 通过 BaseModel 自动使用雪花算法生成。
    """
    
    __tablename__ = "tenants"
    __table_args__ = {"comment": "租户表"}
    
    # id 字段继承自 BaseModel，使用雪花算法自动生成
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="租户名称"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="租户编码"
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1正常"
    )
    domain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="绑定域名"
    )
    expire_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="过期时间"
    )
    package_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="套餐ID"
    )
    account_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="账号数量"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="备注"
    )
    
    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name})>"
