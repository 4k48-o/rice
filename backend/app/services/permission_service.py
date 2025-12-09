"""
Permission service for permission management and tree building.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.schemas.permission import PermissionTreeNode, PermissionCreate, PermissionUpdate


class PermissionService:
    """Permission service."""
    
    @staticmethod
    async def get_permissions(db: AsyncSession, tenant_id: str) -> List[Permission]:
        """
        Get all permissions for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of permissions
        """
        stmt = select(Permission).where(
            Permission.tenant_id == tenant_id,
            Permission.is_deleted == False
        ).order_by(Permission.sort.asc(), Permission.id.asc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    def build_permission_tree(permissions: List[Permission]) -> List[PermissionTreeNode]:
        """
        Build permission tree from flat list.
        
        Args:
            permissions: Flat list of permissions
            
        Returns:
            Tree structure with nested children
        """
        if not permissions:
            return []
        
        # Convert to dict for quick lookup, ensure children is initialized
        perm_dict = {}
        for perm in permissions:
            perm_node = PermissionTreeNode.model_validate(perm)
            # Ensure children list is initialized
            if not hasattr(perm_node, 'children') or perm_node.children is None:
                perm_node.children = []
            perm_dict[perm.id] = perm_node
        
        # Build tree
        root_perms = []
        for perm in permissions:
            perm_node = perm_dict[perm.id]
            
            # Check if it's a root permission (parent_id is None, "0", or 0)
            parent_id = perm.parent_id
            if parent_id is None or parent_id == "0" or parent_id == 0:
                # Root permission
                root_perms.append(perm_node)
            else:
                # Child permission - find parent
                parent = perm_dict.get(str(parent_id))
                if parent:
                    # Ensure parent's children list is initialized
                    if not hasattr(parent, 'children') or parent.children is None:
                        parent.children = []
                    parent.children.append(perm_node)
                else:
                    # Parent not found, treat as root
                    root_perms.append(perm_node)
        
        return root_perms
    
    @staticmethod
    async def create_permission(
        db: AsyncSession,
        perm_data: PermissionCreate,
        tenant_id: str
    ) -> Permission:
        """Create a new permission."""
        perm = Permission(
            **perm_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(perm)
        await db.flush()
        await db.refresh(perm)
        return perm
    
    @staticmethod
    async def update_permission(
        db: AsyncSession,
        perm_id: str,
        perm_data: PermissionUpdate
    ) -> Optional[Permission]:
        """Update a permission."""
        stmt = select(Permission).where(
            Permission.id == perm_id,
            Permission.is_deleted == False
        )
        result = await db.execute(stmt)
        perm = result.scalar_one_or_none()
        
        if not perm:
            return None
        
        # Update fields
        update_data = perm_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(perm, field, value)
        
        await db.flush()
        await db.refresh(perm)
        return perm


# Global instance
permission_service = PermissionService()
