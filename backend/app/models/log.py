"""
Log models.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, SmallInteger, Text, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel, TenantMixin


class LoginLog(BaseModel, TenantMixin):
    """Login log model."""
    
    __tablename__ = "sys_login_log"
    __table_args__ = {"comment": "登录日志表"}
    
    user_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户名"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="状态:1成功,0失败"
    )
    ip: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="登录IP"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="IP归属地"
    )
    browser: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="浏览器"
    )
    os: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="操作系统"
    )
    msg: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="提示消息"
    )
    login_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="登录时间"
    )


class OperationLog(BaseModel, TenantMixin):
    """Operation log model."""
    
    __tablename__ = "sys_opt_log"
    __table_args__ = {"comment": "操作日志表"}
    
    user_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="用户ID"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="用户名"
    )
    module: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="功能模块"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="操作摘要"
    )
    method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="请求方法"
    )
    url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="请求路径"
    )
    ip: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="请求IP"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="IP归属地"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="UA系统"
    )
    params: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="请求参数"
    )
    result: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="响应结果"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="状态:1成功,0失败"
    )
    error_msg: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="错误消息"
    )
    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="耗时(ms)"
    )
