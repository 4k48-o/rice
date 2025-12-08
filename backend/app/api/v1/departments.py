"""
Department API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.department import (
    DepartmentTreeNode,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from app.services.department_service import department_service
from app.core.i18n import i18n
from app.core.permissions import require_permissions
import time

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=dict)
@require_permissions("dept:list")
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all departments (flat list).
    
    Requires permission: dept:list
    """
    departments = await department_service.get_departments(db, current_user.tenant_id)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": [DepartmentResponse.model_validate(d) for d in departments],
        "timestamp": int(time.time())
    }


@router.get("/tree", response_model=dict)
@require_permissions("dept:list")
async def get_department_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get department tree structure.
    
    Requires permission: dept:list
    """
    departments = await department_service.get_departments(db, current_user.tenant_id)
    tree = department_service.build_department_tree(departments)
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": tree,
        "timestamp": int(time.time())
    }


@router.get("/{dept_id}", response_model=dict)
@require_permissions("dept:query")
async def get_department(
    dept_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get department details.
    
    Requires permission: dept:query
    """
    # Debug: Log the request
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Getting department: dept_id={dept_id}, tenant_id={current_user.tenant_id}")
    
    department = await department_service.get_department_by_id(db, dept_id, current_user.tenant_id)
    
    if not department:
        logger.warning(f"Department not found: dept_id={dept_id}, tenant_id={current_user.tenant_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=i18n.t("not_found")
        )
    
    return {
        "code": 200,
        "message": i18n.t("success"),
        "data": DepartmentResponse.model_validate(department),
        "timestamp": int(time.time())
    }


@router.post("", response_model=dict)
@require_permissions("dept:create")
async def create_department(
    dept_data: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new department.
    
    Requires permission: dept:create
    """
    try:
        department = await department_service.create_department(
            db, dept_data, current_user.tenant_id
        )
        await db.commit()
        
        return {
            "code": 200,
            "message": i18n.t("success"),
            "data": DepartmentResponse.model_validate(department),
            "timestamp": int(time.time())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{dept_id}", response_model=dict)
@require_permissions("dept:update")
async def update_department(
    dept_id: str,
    dept_data: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a department.
    
    Requires permission: dept:update
    """
    try:
        # Debug: Log the request
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Updating department: dept_id={dept_id}, tenant_id={current_user.tenant_id}")
        
        department = await department_service.update_department(db, dept_id, dept_data, current_user.tenant_id)
        
        if not department:
            logger.warning(f"Department not found: dept_id={dept_id}, tenant_id={current_user.tenant_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=i18n.t("not_found")
            )
        
        await db.commit()
        
        return {
            "code": 200,
            "message": i18n.t("success"),
            "data": DepartmentResponse.model_validate(department),
            "timestamp": int(time.time())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{dept_id}", response_model=dict)
@require_permissions("dept:delete")
async def delete_department(
    dept_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a department (soft delete).
    
    Requires permission: dept:delete
    """
    try:
        success = await department_service.delete_department(db, dept_id, current_user.tenant_id)
        
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
