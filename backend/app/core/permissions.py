"""
Permission control decorators and data scope filtering.
"""
from enum import IntEnum
from typing import List, Callable, Set
from functools import wraps

from fastapi import HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.core.i18n import i18n


async def clear_user_permission_cache(user_id) -> None:
    """
    Clear permission cache for a user.
    This should be called when user's roles or permissions change.
    
    Args:
        user_id: User ID
    """
    from app.utils.cache import PermissionCache
    await PermissionCache.clear_all_user_cache(user_id)


class DataScope(IntEnum):
    """Data scope for role-based data filtering."""
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门数据
    DEPT_AND_SUB = 3     # 本部门及下级数据
    SELF = 4             # 仅本人数据
    CUSTOM = 5           # 自定义部门数据


def require_permissions(*permission_codes: str):
    """
    Decorator to require specific permissions (AND logic).
    
    Usage:
        @router.get("/users")
        @require_permissions("user:list")
        async def list_users(...):
            ...
    
    Args:
        *permission_codes: Permission codes required (e.g., "user:list", "user:create")
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by FastAPI)
            current_user: User = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t("unauthorized")
                )
            
            # Superadmin bypasses permission check
            if current_user.user_type == 0:
                return await func(*args, **kwargs)
            
            # Get database session
            db: AsyncSession = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not found"
                )
            
            # Get user's permissions
            user_permissions = await get_user_permissions(db, current_user)
            
            # Check if user has all required permissions
            missing_permissions = set(permission_codes) - user_permissions
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t("forbidden")
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permission_codes: str):
    """
    Decorator to require any of the specified permissions (OR logic).
    
    Args:
        *permission_codes: Permission codes (user needs at least one)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t("unauthorized")
                )
            
            # Superadmin bypasses permission check
            if current_user.user_type == 0:
                return await func(*args, **kwargs)
            
            db: AsyncSession = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not found"
                )
            
            user_permissions = await get_user_permissions(db, current_user)
            
            # Check if user has any of the required permissions
            if not any(perm in user_permissions for perm in permission_codes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t("forbidden")
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_roles(*role_codes: str):
    """
    Decorator to require specific roles.
    
    Args:
        *role_codes: Role codes required (e.g., "admin", "manager")
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=i18n.t("unauthorized")
                )
            
            # Superadmin bypasses role check
            if current_user.user_type == 0:
                return await func(*args, **kwargs)
            
            db: AsyncSession = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not found"
                )
            
            user_roles = await get_user_roles(db, current_user)
            
            # Check if user has any of the required roles
            if not any(role in user_roles for role in role_codes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=i18n.t("forbidden")
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def get_user_permissions(db: AsyncSession, user: User) -> Set[str]:
    """
    Get all permission codes for a user.
    Uses cache to improve performance.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Set of permission codes
    """
    from app.utils.cache import PermissionCache
    
    # Try to get from cache first
    cached_permissions = await PermissionCache.get_user_permissions(user.id)
    if cached_permissions is not None:
        return cached_permissions
    
    # Cache miss, query from database
    from app.models.associations import UserRole, RolePermission
    from app.models.permission import Permission
    
    # Get user's roles
    stmt = select(UserRole.role_id).where(UserRole.user_id == user.id)
    result = await db.execute(stmt)
    role_ids = [row[0] for row in result.all()]
    
    if not role_ids:
        permissions = set()
    else:
        # Get permissions for these roles
        # Only get type=2 permissions (actual permissions, not groups)
        stmt = select(Permission.code).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).where(
            RolePermission.role_id.in_(role_ids),
            Permission.status == 1,
            Permission.is_deleted == False,
            Permission.type == 2  # Only actual permissions, not groups (type=1)
        )
        result = await db.execute(stmt)
        permissions = {row[0] for row in result.all() if row[0]}
    
    # Cache the result (fire and forget, don't wait for completion)
    await PermissionCache.set_user_permissions(user.id, permissions)
    
    return permissions


async def get_user_roles(db: AsyncSession, user: User) -> Set[str]:
    """
    Get all role codes for a user.
    Uses cache to improve performance.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        Set of role codes
    """
    from app.utils.cache import PermissionCache
    
    # Try to get from cache first
    cached_roles = await PermissionCache.get_user_roles(user.id)
    if cached_roles is not None:
        return cached_roles
    
    # Cache miss, query from database
    from app.models.associations import UserRole
    from app.models.role import Role
    
    stmt = select(Role.code).join(
        UserRole, UserRole.role_id == Role.id
    ).where(
        UserRole.user_id == user.id,
        Role.status == 1,
        Role.is_deleted == False
    )
    result = await db.execute(stmt)
    roles = {row[0] for row in result.all() if row[0]}
    
    # Cache the result (fire and forget, don't wait for completion)
    await PermissionCache.set_user_roles(user.id, roles)
    
    return roles


async def get_user_data_scope(db: AsyncSession, user: User) -> DataScope:
    """
    Get user's data scope (the most permissive one if user has multiple roles).
    Uses cache to improve performance.
    
    Args:
        db: Database session
        user: User object
        
    Returns:
        DataScope enum value
    """
    from app.utils.cache import PermissionCache
    
    # Try to get from cache first
    cached_data_scope = await PermissionCache.get_user_data_scope(user.id)
    if cached_data_scope is not None:
        return DataScope(cached_data_scope)
    
    # Cache miss, query from database
    from app.models.associations import UserRole
    from app.models.role import Role
    
    stmt = select(Role.data_scope).join(
        UserRole, UserRole.role_id == Role.id
    ).where(
        UserRole.user_id == user.id,
        Role.status == 1,
        Role.is_deleted == False
    )
    result = await db.execute(stmt)
    data_scopes = [row[0] for row in result.all() if row[0] is not None]
    
    if not data_scopes:
        data_scope = DataScope.SELF  # Default to most restrictive
    else:
        # Return the most permissive scope (lowest number)
        data_scope = DataScope(min(data_scopes))
    
    # Cache the result
    await PermissionCache.set_user_data_scope(user.id, data_scope.value)
    
    return data_scope


async def apply_data_scope_filter(db: AsyncSession, query, user: User, model, user_field: str = "created_by"):
    """
    Apply data scope filter to a query.
    Optimized to minimize database queries.
    
    Args:
        db: Database session (Required for async queries)
        query: SQLAlchemy query
        user: Current user
        model: Model class to filter
        user_field: Field name for user ownership (default: "created_by")
        
    Returns:
        Filtered query
    """
    # Superadmin sees all data
    if user.user_type == 0:
        return query
    
    # Get user roles with their data scopes - optimized single query
    from app.models.associations import UserRole, RoleDepartment
    from app.models.role import Role
    
    # Single query to get all roles with data_scope for the user
    stmt = select(Role.id, Role.data_scope).join(
        UserRole, UserRole.role_id == Role.id
    ).where(
        UserRole.user_id == user.id,
        Role.status == 1,
        Role.is_deleted == False
    )
    
    result = await db.execute(stmt)
    roles_data = result.all()
    
    if not roles_data:
        # No role => No data access (safe default? or SELF?)
        # Let's default to SELF to be safe but usable
        return query.where(getattr(model, user_field) == user.id)

    # Extract role IDs and data scopes
    role_ids = [row[0] for row in roles_data]
    data_scopes = [row[1] for row in roles_data if row[1] is not None]
    
    # Find the most permissive scope (min value)
    # 1:ALL, 2:DEPT, 3:DEPT_AND_SUB, 4:SELF, 5:CUSTOM
    if not data_scopes:
        scope = DataScope.SELF
    else:
        scope = DataScope(min(data_scopes))
    
    # Apply filter based on scope
    if scope == DataScope.ALL:
        return query
        
    elif scope == DataScope.SELF:
        return query.where(getattr(model, user_field) == user.id)
        
    elif scope == DataScope.DEPT:
        if hasattr(model, 'dept_id'):
            return query.where(model.dept_id == user.dept_id)
        else:
            return query.where(getattr(model, user_field) == user.id)
            
    elif scope == DataScope.DEPT_AND_SUB:
        if hasattr(model, 'dept_id'):
            # Fetch self + sub departments
            from app.services.department_service import DepartmentService
            dept_ids = await DepartmentService.get_sub_departments(db, user.dept_id)
            dept_ids.append(user.dept_id)
            return query.where(model.dept_id.in_(dept_ids))
        else:
            return query.where(getattr(model, user_field) == user.id)
            
    elif scope == DataScope.CUSTOM:
        # Optimized: Single query to get all custom dept IDs for all CUSTOM scope roles
        custom_role_ids = [row[0] for row in roles_data if row[1] == DataScope.CUSTOM.value]
        
        if custom_role_ids:
            # Single query to get all custom department IDs
            stmt_custom = select(RoleDepartment.department_id).where(
                RoleDepartment.role_id.in_(custom_role_ids)
            )
            res_custom = await db.execute(stmt_custom)
            custom_dept_ids = {row[0] for row in res_custom.all()}
        else:
            custom_dept_ids = set()
        
        if hasattr(model, 'dept_id'):
            if custom_dept_ids:
                return query.where(model.dept_id.in_(custom_dept_ids))
            else:
                # Custom scope but no depts configured -> Empty result
                return query.where(1 == 0)
        else:
            return query.where(getattr(model, user_field) == user.id)
            
    return query
