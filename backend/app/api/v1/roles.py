"""
Role API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions
from app.schemas.permission import PermissionResponse, PermissionTreeNode
from app.services.role_service import role_service
from app.services.permission_service import permission_service
from app.core.i18n import i18n
from app.core.permissions import require_permissions
import time

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=dict)
@require_permissions("role:list")
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all roles.
    
    Requires permission: role:list
    """
    roles = await role_service.get_roles(db, current_user.tenant_id)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": [RoleResponse.model_validate(r) for r in roles],
        "timestamp": int(time.time())
    }


@router.get("/permissions/tree", response_model=dict)
@require_permissions("role:list")
async def get_permission_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get permission tree.
    
    Requires permission: role:list
    """
    permissions = await permission_service.get_permissions(db, current_user.tenant_id)
    tree = permission_service.build_permission_tree(permissions)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": tree,
        "timestamp": int(time.time())
    }


@router.get("/{role_id}", response_model=dict)
@require_permissions("role:query")
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get role details with permissions.
    
    Requires permission: role:query
    """
    role = await role_service.get_role_by_id(db, role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("not_found")
        )
    
    # Get role permissions
    permissions = await role_service.get_role_permissions(db, role_id)
    
    # Build response
    role_dict = RoleResponse.model_validate(role).model_dump()
    role_dict["permissions"] = [PermissionResponse.model_validate(p) for p in permissions]
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": role_dict,
        "timestamp": int(time.time())
    }


@router.post("", response_model=dict)
@require_permissions("role:create")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new role.
    
    Requires permission: role:create
    """
    try:
        role = await role_service.create_role(db, role_data, current_user.tenant_id)
        await db.commit()
        
        return {
            "code": 200,
            "message": i18n.t("success"),
            "data": RoleResponse.model_validate(role),
            "timestamp": int(time.time())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=dict)
@require_permissions("role:update")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a role.
    
    Requires permission: role:update
    """
    try:
        role = await role_service.update_role(db, role_id, role_data)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t("not_found")
            )
        
        await db.commit()
        
        return {
            "code": 200,
            "message": i18n.t("success"),
            "data": RoleResponse.model_validate(role),
            "timestamp": int(time.time())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}", response_model=dict)
@require_permissions("role:delete")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a role (soft delete).
    
    Requires permission: role:delete
    """
    try:
        success = await role_service.delete_role(db, role_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t("not_found")
            )
        
        await db.commit()
        
        return {
            "code": 200,
            "message": i18n.t("success"),
            "data": None,
            "timestamp": int(time.time())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
