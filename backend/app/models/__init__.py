"""Module initialization."""
import sys
# Increase recursion depth for deep model relationships if needed
sys.setrecursionlimit(2000)

from app.models.base import Base, BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin
from app.models.user import User
from app.models.tenant import Tenant
from app.models.role import Role
from app.models.permission import Permission
from app.models.menu import Menu
from app.models.department import Department
from app.models.associations import UserRole, RolePermission

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantMixin",
    "User",
    "Tenant",
    "Role",
    "Permission",
    "Menu",
    "Department",
    "UserRole",
    "RolePermission",
]


