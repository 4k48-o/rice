"""
User-Role and Role-Permission association models.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, String, UniqueConstraint, func, event
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin


class UserRole(Base, TenantMixin, TimestampMixin):
    """User-Role association."""
    
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
        {"comment": "用户角色关联表"}
    )
    
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="主键ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    role_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="角色ID"
    )


class RolePermission(Base, TenantMixin, TimestampMixin):
    """Role-Permission association."""
    
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        {"comment": "角色权限关联表"}
    )
    
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="主键ID"
    )
    role_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="角色ID"
    )
    permission_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="权限ID"
    )


class RoleDepartment(Base):
    """Role-Department association (for custom data scope)."""
    
    __tablename__ = "role_departments"
    __table_args__ = (
        UniqueConstraint('role_id', 'department_id', name='uk_role_department'),
        {"comment": "角色部门关联表(自定义数据权限)"}
    )
    
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="主键ID"
    )
    role_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="角色ID"
    )
    department_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="部门ID"
    )


# Event listeners to generate Snowflake ID for association tables
@event.listens_for(UserRole, "before_insert", propagate=True)
def generate_user_role_id(mapper, connection, target):
    """Generate Snowflake ID for UserRole."""
    if target.id is None or target.id == "":
        from app.utils.snowflake import generate_id
        target.id = generate_id()


@event.listens_for(RolePermission, "before_insert", propagate=True)
def generate_role_permission_id(mapper, connection, target):
    """Generate Snowflake ID for RolePermission."""
    if target.id is None or target.id == "":
        from app.utils.snowflake import generate_id
        target.id = generate_id()


@event.listens_for(RoleDepartment, "before_insert", propagate=True)
def generate_role_department_id(mapper, connection, target):
    """Generate Snowflake ID for RoleDepartment."""
    if target.id is None or target.id == "":
        from app.utils.snowflake import generate_id
        target.id = generate_id()
