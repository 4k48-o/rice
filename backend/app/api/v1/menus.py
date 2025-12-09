"""
Menu API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.menu import MenuTreeNode, MenuCreate, MenuUpdate, MenuResponse
from app.schemas import Response
from app.services.menu_service import menu_service
from app.core.i18n import i18n
from app.core.permissions import require_permissions
import time

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.get("", response_model=Response)
@require_permissions(["menu:list"])
async def list_menus(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    menu_type: Optional[int] = None,
    status: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all menus with pagination and filters.
    
    Requires menu:list permission.
    """
    menus, total = await menu_service.get_all_menus(
        db,
        current_user.tenant_id,
        page,
        page_size,
        keyword,
        menu_type,
        status
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": [MenuResponse.model_validate(menu) for menu in menus],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "timestamp": int(time.time())
    }


@router.get("/tree/all", response_model=Response)
@require_permissions(["menu:list"])
async def get_menu_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete menu tree (without permission filtering).
    
    For admin use. Requires menu:list permission.
    """
    menu_tree = await menu_service.get_all_menus_tree(db, current_user.tenant_id)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": menu_tree,
        "timestamp": int(time.time())
    }


@router.get("/user", response_model=Response)
async def get_user_menu_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's menu tree.
    
    Returns menu tree based on user's permissions.
    """
    # Get user's accessible menus
    menus = await menu_service.get_user_menus(db, current_user)
    
    # Build tree structure
    menu_tree = menu_service.build_menu_tree(menus)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": menu_tree,
        "timestamp": int(time.time())
    }


@router.get("/{menu_id}", response_model=Response)
@require_permissions(["menu:query"])
async def get_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get menu by ID.
    
    Requires menu:query permission.
    """
    menu = await menu_service.get_menu_by_id(db, menu_id)
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    # Check tenant
    if menu.tenant_id != current_user.tenant_id and current_user.user_type != 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=i18n.t("forbidden")
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": MenuResponse.model_validate(menu),
        "timestamp": int(time.time())
    }


@router.post("", response_model=dict)
@require_permissions(["menu:create"])
async def create_menu(
    menu_data: MenuCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new menu."""
    try:
        menu = await menu_service.create_menu(db, menu_data, current_user.tenant_id)
        await db.commit()
    except ValueError as e:
        error_msg = str(e)
        # Try to translate common error messages
        if "Invalid parent menu" in error_msg:
            error_msg = i18n.t("menu.invalid_parent")
        elif "Circular reference" in error_msg:
            error_msg = i18n.t("menu.circular_reference")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": MenuResponse.model_validate(menu),
        "timestamp": int(time.time())
    }


@router.put("/{menu_id}", response_model=dict)
@require_permissions(["menu:update"])
async def update_menu(
    menu_id: str,
    menu_data: MenuUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a menu."""
    try:
        menu = await menu_service.update_menu(db, menu_id, menu_data)
    except ValueError as e:
        error_msg = str(e)
        # Try to translate common error messages
        if "Invalid parent menu" in error_msg:
            error_msg = i18n.t("menu.invalid_parent")
        elif "Circular reference" in error_msg:
            error_msg = i18n.t("menu.circular_reference")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    await db.commit()
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": MenuResponse.model_validate(menu),
        "timestamp": int(time.time())
    }


@router.delete("/{menu_id}", response_model=dict)
@require_permissions(["menu:delete"])
async def delete_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a menu."""
    success = await menu_service.delete_menu(db, menu_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    await db.commit()
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": None,
        "timestamp": int(time.time())
    }
