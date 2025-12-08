"""
Department service for department management and tree building.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentTreeNode, DepartmentCreate, DepartmentUpdate


class DepartmentService:
    """Department service."""
    
    @staticmethod
    async def get_departments(db: AsyncSession, tenant_id: int) -> List[Department]:
        """
        Get all departments for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID (0 for superadmin means all departments)
            
        Returns:
            List of departments
        """
        stmt = select(Department).where(
            Department.is_deleted == False
        )
        # Superadmin (tenant_id=0) can access all departments
        if tenant_id != 0:
            stmt = stmt.where(Department.tenant_id == tenant_id)
        stmt = stmt.order_by(Department.sort.asc(), Department.id.asc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_department_by_id(db: AsyncSession, dept_id: int, tenant_id: int = None) -> Optional[Department]:
        """
        Get department by ID.
        
        Args:
            db: Database session
            dept_id: Department ID
            tenant_id: Optional tenant ID for filtering (for security)
            
        Returns:
            Optional[Department]: Department object
        """
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Querying department: id={dept_id}, tenant_id={tenant_id}, is_superadmin={tenant_id == 0}")
        
        stmt = select(Department).where(
            Department.id == dept_id,
            Department.is_deleted == False
        )
        # Superadmin (tenant_id=0) can access all departments, so don't filter by tenant_id
        if tenant_id is not None and tenant_id != 0:
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
            node = DepartmentTreeNode.model_validate(dept)
            # Add leader_name if needed (will be populated from join in future)
            node.leader_name = None
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
        tenant_id: int
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
        return dept
    
    @staticmethod
    async def update_department(
        db: AsyncSession,
        dept_id: int,
        dept_data: DepartmentUpdate,
        tenant_id: int = None
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
        return dept
    
    @staticmethod
    async def delete_department(db: AsyncSession, dept_id: int, tenant_id: int = None) -> bool:
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
        return True
    
    @staticmethod
    async def get_sub_departments(
        db: AsyncSession,
        dept_id: int,
        include_self: bool = False
    ) -> List[int]:
        """
        Get all sub-department IDs recursively.
        
        Args:
            db: Database session
            dept_id: Parent department ID
            include_self: Whether to include the parent ID itself
            
        Returns:
            List of department IDs
        """
        dept_ids = [dept_id] if include_self else []
        
        # Get direct children
        stmt = select(Department.id).where(
            Department.parent_id == dept_id,
            Department.is_deleted == False
        )
        result = await db.execute(stmt)
        child_ids = [row[0] for row in result.all()]
        
        # Recursively get sub-children
        for child_id in child_ids:
            sub_ids = await DepartmentService.get_sub_departments(db, child_id, include_self=True)
            dept_ids.extend(sub_ids)
        
        return dept_ids


# Global instance
department_service = DepartmentService()
