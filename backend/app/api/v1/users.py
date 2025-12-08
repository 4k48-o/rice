"""
User management API endpoints.
"""
from typing import List
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api import deps
from app.schemas import UserListResponse, UserCreate, UserUpdate, UserResponse
from app.schemas.common import Response, PageResponse
from app.services.user_service import user_service
from app.core.exceptions import BusinessException
from app.core.i18n import i18n
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=Response)
async def get_users(
    page: int = 1,
    page_size: int = 20,
    username: str = None,
    phone: str = None,
    status: int = None,
    dept_id: str = None,
    current_user: User = Depends(deps.require_permissions("user:list")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user list.
    Requires permission: user:list
    """
    
    users, total = await user_service.get_user_list(
        db,
        page=page,
        page_size=page_size,
        username=username,
        phone=phone,
        status=status,
        dept_id=dept_id,
        tenant_id=current_user.tenant_id
    )
    
    # Manual conversion because generic Response has data: dict
    # Serialize to dict to ensure datetime fields are properly converted
    items = [UserResponse.model_validate(u).model_dump(mode='json') for u in users]
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": items,
            "total": total
        },
        "timestamp": int(time.time()),
    }


@router.get("/{user_id}", response_model=Response)
async def get_user(
    user_id: str,
    current_user: User = Depends(deps.require_permissions("user:detail")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user details by ID.
    Requires permission: user:detail
    """
    user = await user_service.get_by_id(db, user_id)
    
    if not user:
        return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    # Check tenant access
    if user.tenant_id != current_user.tenant_id and current_user.user_type != 0:
        return {
            "code": 403,
            "message": i18n.t("forbidden"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    # Get user roles
    roles = await user_service.get_user_roles(db, user_id)
    user_dict = UserResponse.model_validate(user).model_dump(mode='json')
    
    user_dict["role_ids"] = [role.id for role in roles]
    user_dict["roles"] = [{"id": role.id, "name": role.name, "code": role.code} for role in roles]
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": user_dict,
        "timestamp": int(time.time()),
    }


@router.get("/{user_id}/roles", response_model=Response)
async def get_user_roles(
    user_id: str,
    current_user: User = Depends(deps.require_permissions("user:detail")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's roles.
    Requires permission: user:detail
    """
    user = await user_service.get_by_id(db, user_id)
    
    if not user:
        return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    # Check tenant access
    if user.tenant_id != current_user.tenant_id and current_user.user_type != 0:
        return {
            "code": 403,
            "message": i18n.t("forbidden"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    roles = await user_service.get_user_roles(db, user_id)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": [{"id": role.id, "name": role.name, "code": role.code} for role in roles],
        "timestamp": int(time.time()),
    }


@router.post("", response_model=Response)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(deps.require_permissions("user:create")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create user.
    Requires permission: user:create
    """
    
    try:
        new_user = await user_service.create_user(
            db,
            user_in.model_dump(),
            tenant_id=current_user.tenant_id
        )
    except ValueError as e:
        return {
            "code": 400,
            "message": str(e),
            "data": None,
            "timestamp": int(time.time()),
        }
        
    return {
        "code": 200,
        "message": i18n.t("user_created"),
        "data": {"id": new_user.id},
        "timestamp": int(time.time()),
    }


@router.put("/{user_id}", response_model=Response)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(deps.require_permissions("user:update")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user.
    Requires permission: user:update
    """
    # Get the user to update
    user = await user_service.get_by_id(db, user_id)
    if not user:
        return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    # Check tenant access
    if user.tenant_id != current_user.tenant_id and current_user.user_type != 0:
        return {
            "code": 403,
            "message": i18n.t("forbidden"),
            "data": None,
            "timestamp": int(time.time()),
        }

    # Update user (username cannot be changed via UserUpdate schema)
    updated_user = await user_service.update_user(
        db,
        user_id,
        user_in.model_dump(exclude_unset=True)
    )
    
    if not updated_user:
        return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
    
    # Commit the transaction
    await db.commit()
        
    return {
        "code": 200,
        "message": i18n.t("user_updated"),
        "data": { "id": user_id },
        "timestamp": int(time.time()),
    }


@router.post("/{user_id}/reset-password", response_model=Response)
async def reset_password(
    user_id: str,
    password_in: dict, # { "password": "new_password" }
    current_user: User = Depends(deps.require_permissions("user:reset-password")),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset user password (Admin).
    Requires permission: user:reset-password
    """
    new_password = password_in.get("password")
    if not new_password or len(new_password) < 6:
         return {
            "code": 400,
            "message": i18n.t("password_min_length"),
            "data": None,
            "timestamp": int(time.time()),
        }

    success = await user_service.reset_password(db, user_id, new_password)
    
    if not success:
         return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
        
    return {
        "code": 200,
        "message": i18n.t("password_reset_success"),
        "data": None,
        "timestamp": int(time.time()),
    }


@router.delete("/{user_id}", response_model=Response)
async def delete_user(
    user_id: str,
    current_user: User = Depends(deps.require_permissions("user:delete")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user.
    Requires permission: user:delete
    """
    success = await user_service.delete_user(db, user_id)
    
    if not success:
          return {
            "code": 404,
            "message": i18n.t("resource_not_found"),
            "data": None,
            "timestamp": int(time.time()),
        }
        
    return {
        "code": 200,
        "message": i18n.t("user_deleted"),
        "data": None,
        "timestamp": int(time.time()),
    }
