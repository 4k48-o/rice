"""
Department service for department management and tree building.
"""
import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentTreeNode, DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.utils.cache import DepartmentCache

logger = logging.getLogger(__name__)


class DepartmentService:
    """Department service."""
    
    @staticmethod
    async def get_departments(db: AsyncSession, tenant_id: str) -> List[Department]:
        """
        Get all departments for a tenant.
        Uses cache when available, falls back to database on cache miss.
        
        Args:
            db: Database session
            tenant_id: Tenant ID (0 for superadmin means all departments)
            
        Returns:
            List of departments
        """
        # Try to get from cache
        try:
            cached_data = await DepartmentCache.get_departments_list(tenant_id)
            if cached_data:
                # Reconstruct Department objects from cached data
                dept_list = []
                for dept_dict in cached_data:
                    # Create Department object from cached dict
                    # Note: We reconstruct the object with all necessary fields
                    dept = Department(
                        id=dept_dict['id'],
                        tenant_id=dept_dict['tenant_id'],
                        parent_id=dept_dict.get('parent_id'),
                        name=dept_dict['name'],
                        code=dept_dict['code'],
                        leader_id=dept_dict.get('leader_id'),
                        phone=dept_dict.get('phone'),
                        email=dept_dict.get('email'),
                        sort=dept_dict.get('sort', 0),
                        status=dept_dict.get('status', 1),
                        remark=dept_dict.get('remark'),
                        is_deleted=False,
                        # BaseModel fields (if present in cache)
                        created_at=dept_dict.get('created_at'),
                        updated_at=dept_dict.get('updated_at'),
                        created_by=dept_dict.get('created_by'),
                        updated_by=dept_dict.get('updated_by'),
                    )
                    dept_list.append(dept)
                logger.debug(f"Cache hit for departments list: tenant_id={tenant_id}, count={len(dept_list)}")
                return dept_list
        except Exception as e:
            logger.warning(f"Failed to get departments from cache, falling back to DB: {e}")
        
        # Cache miss or error - query database
        stmt = select(Department).where(
            Department.is_deleted == False
        )
        # Superadmin (tenant_id="0") can access all departments
        if tenant_id != "0":
            stmt = stmt.where(Department.tenant_id == tenant_id)
        stmt = stmt.order_by(Department.sort.asc(), Department.id.asc())
        
        result = await db.execute(stmt)
        departments = list(result.scalars().all())
        
        # Write to cache (async, don't wait for it)
        try:
            await DepartmentCache.set_departments_list(tenant_id, departments)
        except Exception as e:
            logger.warning(f"Failed to set departments list to cache: {e}")
        
        return departments
    
    @staticmethod
    async def get_department_by_id(db: AsyncSession, dept_id: str, tenant_id: str = None) -> Optional[Department]:
        """
        Get department by ID.
        Uses cache when available, falls back to database on cache miss.
        
        Args:
            db: Database session
            dept_id: Department ID
            tenant_id: Optional tenant ID for filtering (for security)
            
        Returns:
            Optional[Department]: Department object
        """
        logger.info(f"Querying department: id={dept_id}, tenant_id={tenant_id}, is_superadmin={tenant_id == '0'}")
        
        # Try to get from cache
        try:
            cached_data = await DepartmentCache.get_department_detail(dept_id)
            if cached_data:
                # Reconstruct Department object from cached data
                dept = Department(
                    id=cached_data['id'],
                    tenant_id=cached_data['tenant_id'],
                    parent_id=cached_data.get('parent_id'),
                    name=cached_data['name'],
                    code=cached_data['code'],
                    leader_id=cached_data.get('leader_id'),
                    phone=cached_data.get('phone'),
                    email=cached_data.get('email'),
                    sort=cached_data.get('sort', 0),
                    status=cached_data.get('status', 1),
                    remark=cached_data.get('remark'),
                    is_deleted=False,
                    # BaseModel fields (if present in cache)
                    created_at=cached_data.get('created_at'),
                    updated_at=cached_data.get('updated_at'),
                    created_by=cached_data.get('created_by'),
                    updated_by=cached_data.get('updated_by'),
                )
                # Check tenant_id filter if provided
                if tenant_id is not None and tenant_id != "0" and dept.tenant_id != tenant_id:
                    logger.warning(f"Cached department tenant_id mismatch: cached={dept.tenant_id}, requested={tenant_id}")
                    # Fall through to DB query for security check
                else:
                    logger.debug(f"Cache hit for department detail: dept_id={dept_id}")
                    return dept
        except Exception as e:
            logger.warning(f"Failed to get department from cache, falling back to DB: {e}")
        
        # Cache miss or error - query database
        stmt = select(Department).where(
            Department.id == dept_id,
            Department.is_deleted == False
        )
        # Superadmin (tenant_id="0") can access all departments, so don't filter by tenant_id
        if tenant_id is not None and tenant_id != "0":
            stmt = stmt.where(Department.tenant_id == tenant_id)
            logger.info(f"Applied tenant filter: tenant_id={tenant_id}")
        else:
            logger.info(f"No tenant filter applied (superadmin or None)")
        
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        
        if not dept:
            # Check if department exists but is deleted or belongs to different tenant
            stmt_check = select(Department).where(Department.id == dept_id)
            result_check = await db.execute(stmt_check)
            dept_check = result_check.scalar_one_or_none()
            if dept_check:
                logger.warning(f"Department exists but: is_deleted={dept_check.is_deleted}, tenant_id={dept_check.tenant_id}, requested_tenant_id={tenant_id}")
            else:
                logger.warning(f"Department not found in database: id={dept_id}")
        else:
            logger.info(f"Department found: id={dept.id}, name={dept.name}, tenant_id={dept.tenant_id}")
            # Write to cache (async, don't wait for it)
            try:
                await DepartmentCache.set_department_detail(dept_id, dept)
            except Exception as e:
                logger.warning(f"Failed to set department detail to cache: {e}")
        
        return dept
    
    @staticmethod
    def build_department_tree(departments: List[Department]) -> List[DepartmentTreeNode]:
        """
        Build department tree from flat list.
        
        Args:
            departments: Flat list of departments
            
        Returns:
            Tree structure with nested children
        """
        # Convert to dict for quick lookup
        dept_dict = {}
        for dept in departments:
            # Ensure tenant_id is string (database might return int for old data)
            dept_dict_entry = {
                "id": str(dept.id),
                "tenant_id": str(dept.tenant_id) if dept.tenant_id is not None else "0",
                "name": dept.name,
                "code": dept.code,
                "parent_id": str(dept.parent_id) if dept.parent_id else None,
                "leader_id": str(dept.leader_id) if dept.leader_id else None,
                "phone": dept.phone,
                "email": dept.email,
                "sort": dept.sort,
                "status": dept.status,
                "remark": dept.remark,
                "leader_name": None,
            }
            node = DepartmentTreeNode.model_validate(dept_dict_entry)
            dept_dict[dept.id] = node
        
        # Build tree
        root_depts = []
        for dept in departments:
            dept_node = dept_dict[dept.id]
            
            if dept.parent_id is None or dept.parent_id == 0:
                # Root department
                root_depts.append(dept_node)
            else:
                # Child department
                parent = dept_dict.get(dept.parent_id)
                if parent:
                    parent.children.append(dept_node)
        
        return root_depts
    
    @staticmethod
    async def create_department(
        db: AsyncSession,
        dept_data: DepartmentCreate,
        tenant_id: str
    ) -> Department:
        """Create a new department."""
        # Validate parent exists if specified
        if dept_data.parent_id:
            parent = await DepartmentService.get_department_by_id(db, dept_data.parent_id)
            if not parent:
                raise ValueError("Parent department not found")
        
        dept = Department(
            **dept_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(dept)
        await db.flush()
        await db.refresh(dept)
        
        # Clear cache after creation
        try:
            await DepartmentCache.clear_all_cache(tenant_id, dept_id=None)
            logger.debug(f"Cleared cache after creating department: tenant_id={tenant_id}")
        except Exception as e:
            logger.warning(f"Failed to clear cache after creating department: {e}")
        
        return dept
    
    @staticmethod
    async def update_department(
        db: AsyncSession,
        dept_id: str,
        dept_data: DepartmentUpdate,
        tenant_id: str = None
    ) -> Optional[Department]:
        """
        Update a department.
        
        Args:
            db: Database session
            dept_id: Department ID
            dept_data: Update data
            tenant_id: Optional tenant ID for security check
            
        Returns:
            Optional[Department]: Updated department or None if not found
        """
        dept = await DepartmentService.get_department_by_id(db, dept_id, tenant_id)
        if not dept:
            return None
        
        # Get tenant_id from department if not provided
        actual_tenant_id = tenant_id if tenant_id is not None else dept.tenant_id
        
        # Validate parent if being updated
        update_data = dept_data.model_dump(exclude_unset=True)
        if "parent_id" in update_data and update_data["parent_id"]:
            # Prevent circular reference
            if update_data["parent_id"] == dept_id:
                raise ValueError("Department cannot be its own parent")
            
            parent = await DepartmentService.get_department_by_id(db, update_data["parent_id"], tenant_id)
            if not parent:
                raise ValueError("Parent department not found")
        
        # Update fields
        for field, value in update_data.items():
            setattr(dept, field, value)
        
        await db.flush()
        await db.refresh(dept)
        
        # Clear cache after update
        try:
            await DepartmentCache.clear_all_cache(actual_tenant_id, dept_id=dept_id)
            logger.debug(f"Cleared cache after updating department: tenant_id={actual_tenant_id}, dept_id={dept_id}")
        except Exception as e:
            logger.warning(f"Failed to clear cache after updating department: {e}")
        
        return dept
    
    @staticmethod
    async def delete_department(db: AsyncSession, dept_id: str, tenant_id: str = None) -> bool:
        """
        Soft delete a department.
        
        Args:
            db: Database session
            dept_id: Department ID
            tenant_id: Optional tenant ID for security check
        
        Note: Should check if department has children or users before deleting.
        """
        dept = await DepartmentService.get_department_by_id(db, dept_id, tenant_id)
        if not dept:
            return False
        
        # Get tenant_id from department if not provided
        actual_tenant_id = tenant_id if tenant_id is not None else dept.tenant_id
        
        # Check if has children
        stmt = select(Department).where(
            Department.parent_id == dept_id,
            Department.is_deleted == False
        )
        result = await db.execute(stmt)
        if result.first():
            raise ValueError("Cannot delete department with children")
        
        dept.is_deleted = True
        await db.flush()
        
        # Clear cache after deletion
        try:
            await DepartmentCache.clear_all_cache(actual_tenant_id, dept_id=dept_id)
            logger.debug(f"Cleared cache after deleting department: tenant_id={actual_tenant_id}, dept_id={dept_id}")
        except Exception as e:
            logger.warning(f"Failed to clear cache after deleting department: {e}")
        
        return True
    
    @staticmethod
    async def get_sub_departments(
        db: AsyncSession,
        dept_id: str,
        include_self: bool = True
    ) -> List[str]:
        """
        Get all sub-department IDs recursively.
        
        Args:
            db: Database session
            dept_id: Parent department ID
            include_self: Whether to include the parent ID itself (default: True)
            
        Returns:
            List of department IDs (strings)
        """
        dept_ids = [dept_id] if include_self else []
        
        # Get direct children
        stmt = select(Department.id).where(
            Department.parent_id == dept_id,
            Department.is_deleted == False
        )
        result = await db.execute(stmt)
        child_ids = [str(row[0]) for row in result.all()]
        
        # Recursively get sub-children
        for child_id in child_ids:
            sub_ids = await DepartmentService.get_sub_departments(db, child_id, include_self=True)
            dept_ids.extend(sub_ids)
        
        return dept_ids


# Global instance
department_service = DepartmentService()
