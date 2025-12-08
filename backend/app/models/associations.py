"""
User-Role and Role-Permission association models.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin


class UserRole(Base, TenantMixin):
    """User-Role association."""
    
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
        {"comment": "用户角色关联表"}
    )
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="角色ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="创建人ID"
    )


class RolePermission(Base, TenantMixin):
    """Role-Permission association."""
    
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        {"comment": "角色权限关联表"}
    )
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="角色ID"
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="权限ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="创建人ID"
    )


class RoleDepartment(Base):
    """Role-Department association (for custom data scope)."""
    
    __tablename__ = "role_departments"
    __table_args__ = (
        UniqueConstraint('role_id', 'department_id', name='uk_role_department'),
        {"comment": "角色部门关联表(自定义数据权限)"}
    )
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="角色ID"
    )
    department_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="部门ID"
    )
