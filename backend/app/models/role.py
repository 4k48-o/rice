"""
Role model.
"""
from typing import List

from sqlalchemy import BigInteger, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TenantMixin

class Role(BaseModel, TenantMixin):
    """Role model."""
    
    __tablename__ = "roles"
    __table_args__ = {"comment": "角色表"}
    
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="角色名称"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="角色编码"
    )
    sort: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="显示顺序"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="状态:0禁用,1正常"
    )
    data_scope: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="数据权限:1全部,2本部门及以下,3本部门,4仅本人,5自定义"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"

    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        primaryjoin="Role.id==user_roles.c.role_id",
        secondaryjoin="User.id==user_roles.c.user_id",
        back_populates="roles",
        lazy="selectin"
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        primaryjoin="Role.id==role_permissions.c.role_id",
        secondaryjoin="Permission.id==role_permissions.c.permission_id",
        back_populates="roles",
        lazy="selectin"
    )
    custom_departments = relationship(
        "Department",
        secondary="role_departments",
        primaryjoin="Role.id==role_departments.c.role_id",
        secondaryjoin="role_departments.c.department_id==Department.id",
        backref="roles",
        lazy="selectin"
    )
