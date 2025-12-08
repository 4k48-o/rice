"""
Base model with common fields for all tables.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="创建人ID"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="更新人ID"
    )


class SoftDeleteMixin:
    """Mixin for soft delete."""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="是否删除"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="删除时间"
    )
    deleted_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="删除人ID"
    )


class TenantMixin:
    """Mixin for multi-tenant support."""
    
    tenant_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
        comment="租户ID,0表示平台级"
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Base model with common fields.
    All business tables should inherit from this.
    """
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="主键ID"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="备注"
    )


# Event listener to generate Snowflake ID before insert
from sqlalchemy import event

@event.listens_for(BaseModel, "before_insert", propagate=True)
def generate_snowflake_id(mapper, connection, target):
    """Generate Snowflake ID for new records."""
    if target.id is None:
        from app.utils.snowflake import generate_id
        target.id = generate_id()

