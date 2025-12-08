"""
User model.
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TenantMixin


class User(BaseModel, TenantMixin):
    """User model."""
    
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}
    
    # Basic info
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码bcrypt哈希值"
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="真实姓名"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称"
    )
    
    # Contact info
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="邮箱"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="手机号"
    )
    
    # User type and department
    user_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="用户类型:0超级管理员,1租户管理员,2普通用户"
    )
    dept_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="部门ID"
    )
    position: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="职位"
    )
    
    # Status
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        index=True,
        comment="状态:0禁用,1正常,2锁定"
    )
    
    # Avatar and gender
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="头像URL"
    )
    gender: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="性别:0未知,1男,2女"
    )
    
    # Login info
    last_login_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="最后登录IP"
    )
    login_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="登录次数"
    )
    
    # Password policy
    password_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="密码更新时间"
    )
    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="是否必须修改密码"
    )
    
    # Relationships
    roles = relationship(
        "Role",
        secondary="user_roles",
        primaryjoin="User.id==user_roles.c.user_id",
        secondaryjoin="Role.id==user_roles.c.role_id",
        back_populates="users",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
