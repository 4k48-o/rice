"""
Menu model for navigation and permission control.
"""
from typing import Optional
from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TenantMixin


class Menu(BaseModel, TenantMixin):
    """Menu model for navigation tree."""
    
    __tablename__ = "menus"
    __table_args__ = {"comment": "菜单表"}
    
    # Parent relationship
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="父菜单ID,NULL表示顶级菜单"
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="菜单名称"
    )
    title: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="菜单标题(用于显示)"
    )
    
    # Route info
    path: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="路由路径"
    )
    component: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="组件路径"
    )
    redirect: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="重定向路径"
    )
    
    # Display
    icon: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="图标"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="排序(升序)"
    )
    
    # Type and permission
    type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="类型:1目录,2菜单,3按钮"
    )
    permission_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="权限标识,如user:list"
    )
    
    # Status and visibility
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1启用"
    )
    visible: Mapped[bool] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="是否可见:0隐藏,1显示"
    )
    
    # Cache and external
    is_cache: Mapped[bool] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="是否缓存:0否,1是"
    )
    is_external: Mapped[bool] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="是否外链:0否,1是"
    )
    
    def __repr__(self) -> str:
        return f"<Menu(id={self.id}, name={self.name}, type={self.type})>"
