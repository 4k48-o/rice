"""
Dictionary data API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.dict_data import DictDataCreate, DictDataUpdate, DictDataResponse
from app.schemas import Response
from app.services.dict_data_service import dict_data_service
from app.core.i18n import i18n
from app.core.permissions import require_permissions
import time

router = APIRouter(prefix="/dict-data", tags=["Dictionary Data"])


@router.get("", response_model=Response)
@require_permissions(["dict:list"])
async def list_dict_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    dict_type_id: Optional[str] = None,
    status: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all dictionary data with pagination and filters.
    
    Requires dict:list permission.
    """
    dict_data, total = await dict_data_service.get_all_dict_data(
        db,
        current_user.tenant_id,
        page,
        page_size,
        keyword,
        dict_type_id,
        status
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": {
            "items": [DictDataResponse.model_validate(dd) for dd in dict_data],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        "timestamp": int(time.time())
    }


@router.get("/type/{type_code}", response_model=Response)
async def get_dict_data_by_type(
    type_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dictionary data by type code (public endpoint, cached).
    
    This endpoint does not require authentication, but we still get current_user
    for tenant isolation. For truly public access, you may want to modify this.
    """
    dict_data_list = await dict_data_service.get_dict_data_by_type_cached(
        db, type_code, current_user.tenant_id
    )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": [DictDataResponse.model_validate(dd) for dd in dict_data_list],
        "timestamp": int(time.time())
    }


@router.get("/{dict_data_id}", response_model=Response)
@require_permissions(["dict:query"])
async def get_dict_data(
    dict_data_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dictionary data by ID.
    
    Requires dict:query permission.
    """
    dict_data = await dict_data_service.get_dict_data(db, dict_data_id, current_user.tenant_id)
    
    if not dict_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictDataResponse.model_validate(dict_data),
        "timestamp": int(time.time())
    }


@router.post("", response_model=dict)
@require_permissions(["dict:create"])
async def create_dict_data(
    dict_data_data: DictDataCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new dictionary data."""
    try:
        dict_data = await dict_data_service.create_dict_data(db, dict_data_data, current_user.tenant_id)
        await db.commit()
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            error_msg = i18n.t("dict.typeNotFound")
        elif "already exists" in error_msg:
            error_msg = i18n.t("dict.valueExists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictDataResponse.model_validate(dict_data),
        "timestamp": int(time.time())
    }


@router.put("/{dict_data_id}", response_model=dict)
@require_permissions(["dict:update"])
async def update_dict_data(
    dict_data_id: str,
    dict_data_data: DictDataUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a dictionary data."""
    try:
        dict_data = await dict_data_service.update_dict_data(
            db, dict_data_id, dict_data_data, current_user.tenant_id
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            error_msg = i18n.t("dict.typeNotFound")
        elif "already exists" in error_msg:
            error_msg = i18n.t("dict.valueExists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    if not dict_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("resource_not_found")
        )
    
    await db.commit()
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DictDataResponse.model_validate(dict_data),
        "timestamp": int(time.time())
    }


@router.delete("/{dict_data_id}", response_model=dict)
@require_permissions(["dict:delete"])
async def delete_dict_data(
    dict_data_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a dictionary data."""
    success = await dict_data_service.delete_dict_data(db, dict_data_id, current_user.tenant_id)
    
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

