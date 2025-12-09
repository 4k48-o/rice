"""
Dictionary type API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.dict_type import DictTypeCreate, DictTypeUpdate, DictTypeResponse
from app.schemas import Response
from app.services.dict_type_service import dict_type_service
from app.core.i18n import i18n
from app.core.permissions import require_permissions
import time

router = APIRouter(prefix="/dict-types", tags=["Dictionary Types"])


@router.get("", response_model=Response)
@require_permissions(["dict:list"])
async def list_dict_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all dictionary types with pagination and filters.
    
    Requires dict:list permission.
    """
    dict_types, total = await dict_type_service.get_all_dict_types(
        db,
        current_user.tenant_id,
        page,
        page_size,
        keyword,
        status
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": [DictTypeResponse.model_validate(dt) for dt in dict_types],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "timestamp": int(time.time())
    }


@router.get("/{dict_type_id}", response_model=Response)
@require_permissions(["dict:query"])
async def get_dict_type(
    dict_type_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dictionary type by ID.
    
    Requires dict:query permission.
    """
    dict_type = await dict_type_service.get_dict_type(db, dict_type_id, current_user.tenant_id)
    
    if not dict_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictTypeResponse.model_validate(dict_type),
        "timestamp": int(time.time())
    }


@router.post("", response_model=dict)
@require_permissions(["dict:create"])
async def create_dict_type(
    dict_type_data: DictTypeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new dictionary type."""
    try:
        dict_type = await dict_type_service.create_dict_type(db, dict_type_data, current_user.tenant_id)
        await db.commit()
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            error_msg = i18n.t("dict.codeExists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictTypeResponse.model_validate(dict_type),
        "timestamp": int(time.time())
    }


@router.put("/{dict_type_id}", response_model=dict)
@require_permissions(["dict:update"])
async def update_dict_type(
    dict_type_id: str,
    dict_type_data: DictTypeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a dictionary type."""
    try:
        dict_type = await dict_type_service.update_dict_type(
            db, dict_type_id, dict_type_data, current_user.tenant_id
        )
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            error_msg = i18n.t("dict.codeExists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    if not dict_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    await db.commit()
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictTypeResponse.model_validate(dict_type),
        "timestamp": int(time.time())
    }


@router.delete("/{dict_type_id}", response_model=dict)
@require_permissions(["dict:delete"])
async def delete_dict_type(
    dict_type_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a dictionary type."""
    try:
        success = await dict_type_service.delete_dict_type(db, dict_type_id, current_user.tenant_id)
    except ValueError as e:
        error_msg = str(e)
        if "associated data" in error_msg:
            error_msg = i18n.t("dict.typeHasData")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
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

