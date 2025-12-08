"""
Role service for role management and permission assignment.
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.permission import Permission
from app.models.associations import RolePermission, UserRole
from app.schemas.role import RoleCreate, RoleUpdate
from app.schemas.permission import PermissionResponse


class RoleService:
    """Role service."""
    
    @staticmethod
    async def get_roles(db: AsyncSession, tenant_id: str) -> List[Role]:
        """
        Get all roles for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of roles
        """
        stmt = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.is_deleted == False
        ).order_by(Role.sort.asc(), Role.id.asc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        stmt = select(Role).where(
            Role.id == role_id,
            Role.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_role_permissions(db: AsyncSession, role_id: str) -> List[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            db: Database session
            role_id: Role ID
            
        Returns:
            List of permissions
        """
        stmt = select(Permission).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).where(
            RolePermission.role_id == role_id,
            Permission.is_deleted == False
        ).order_by(Permission.sort.asc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def create_role(
        db: AsyncSession,
        role_data: RoleCreate,
        tenant_id: str
    ) -> Role:
        """Create a new role with permissions."""
        # Extract permission_ids
        permission_ids = role_data.permission_ids
        role_dict = role_data.model_dump(exclude={"permission_ids"})
        
        # Create role
        role = Role(**role_dict, tenant_id=tenant_id)
        db.add(role)
        await db.flush()
        await db.refresh(role)
        
        # Assign permissions
        if permission_ids:
            await RoleService._assign_permissions(db, role.id, permission_ids)
        
        return role
    
    @staticmethod
    async def update_role(
        db: AsyncSession,
        role_id: str,
        role_data: RoleUpdate
    ) -> Optional[Role]:
        """Update a role and its permissions."""
        role = await RoleService.get_role_by_id(db, role_id)
        if not role:
            return None
        
        # Extract permission_ids if present
        update_data = role_data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)
        
        # Update role fields
        for field, value in update_data.items():
            setattr(role, field, value)
        
        await db.flush()
        
        # Update permissions if provided
        if permission_ids is not None:
            # Remove old permissions
            await db.execute(
                delete(RolePermission).where(RolePermission.role_id == role_id)
            )
            # Assign new permissions
            if permission_ids:
                await RoleService._assign_permissions(db, role_id, permission_ids)
        
        await db.refresh(role)
        return role
    
    @staticmethod
    async def delete_role(db: AsyncSession, role_id: str) -> bool:
        """
        Soft delete a role.
        
        Checks if role is assigned to any users before deletion.
        """
        role = await RoleService.get_role_by_id(db, role_id)
        if not role:
            return False
        
        # Check if role is assigned to users
        stmt = select(UserRole).where(UserRole.role_id == role_id)
        result = await db.execute(stmt)
        if result.first():
            raise ValueError("Cannot delete role assigned to users")
        
        role.is_deleted = True
        await db.flush()
        return True
    
    @staticmethod
    async def _assign_permissions(
        db: AsyncSession,
        role_id: str,
        permission_ids: List[int]
    ) -> None:
        """
        Assign permissions to a role.
        
        Args:
            db: Database session
            role_id: Role ID
            permission_ids: List of permission IDs
        """
        # Validate permissions exist
        stmt = select(Permission.id).where(
            Permission.id.in_(permission_ids),
            Permission.is_deleted == False
        )
        result = await db.execute(stmt)
        valid_ids = {row[0] for row in result.all()}
        
        invalid_ids = set(permission_ids) - valid_ids
        if invalid_ids:
            raise ValueError(f"Invalid permission IDs: {invalid_ids}")
        
        # Get role to get tenant_id
        role = await db.get(Role, role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        
        # Create role-permission associations
        for perm_id in permission_ids:
            role_perm = RolePermission(
                role_id=role_id, 
                permission_id=perm_id,
                tenant_id=role.tenant_id
            )
            db.add(role_perm)
        
        await db.flush()


# Global instance
role_service = RoleService()
