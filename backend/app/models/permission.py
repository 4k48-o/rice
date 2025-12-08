"""
Permission model (Menu/Button).
"""
from typing import Optional

from sqlalchemy import BigInteger, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin, TenantMixin


class Permission(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Permission model (Menu/Resource)."""
    
    __tablename__ = "permissions"
    __table_args__ = {"comment": "权限/菜单表"}
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="主键ID"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
        comment="父级ID"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="菜单名称"
    )
    code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="权限标识"
    )
    type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="类型:1目录,2菜单,3按钮"
    )
    path: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="路由路径"
    )
    component: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="前端组件"
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="图标"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="排序"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1正常"
    )
    visible: Mapped[bool] = mapped_column(
        SmallInteger,  # using SmallInteger for boolean compatibility or explicit Boolean
        nullable=False,
        default=1,
        server_default="1",
        comment="是否可见:0隐藏,1显示"
    )
    
    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        primaryjoin="Permission.id==role_permissions.c.permission_id",
        secondaryjoin="Role.id==role_permissions.c.role_id",
        back_populates="permissions",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"
