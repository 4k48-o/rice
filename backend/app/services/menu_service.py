"""
Menu service for menu management and tree building.
"""
from typing import List, Optional, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import Menu
from app.models.user import User
from app.schemas.menu import MenuTreeNode, MenuCreate, MenuUpdate


class MenuService:
    """Menu service."""
    
    @staticmethod
    async def get_user_menus(db: AsyncSession, user: User) -> List[Menu]:
        """
        Get menus accessible to user based on their permissions.
        
        Uses Redis cache to improve performance.
        
        Args:
            db: Database session
            user: Current user
            
        Returns:
            List of menus user can access
        """
        # Try to get from cache
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        cache_key = f"user_menus:{user.id}"
        
        # Check cache
        cached_menu_ids = await redis.get(cache_key)
        if cached_menu_ids:
            # Parse cached menu IDs
            menu_ids = [int(id_str) for id_str in cached_menu_ids.split(",")]
            stmt = select(Menu).where(
                Menu.id.in_(menu_ids),
                Menu.is_deleted == False
            ).order_by(Menu.sort.asc(), Menu.id.asc())
            result = await db.execute(stmt)
            return list(result.scalars().all())
        
        # Cache miss - fetch from database
        # Superadmin sees all menus
        if user.user_type == 0:
            stmt = select(Menu).where(
                Menu.tenant_id == user.tenant_id,
                Menu.status == 1,
                Menu.is_deleted == False
            ).order_by(Menu.sort.asc(), Menu.id.asc())
            result = await db.execute(stmt)
            menus = list(result.scalars().all())
        else:
            # Get user's permissions
            user_permissions = await MenuService._get_user_permissions(db, user)
            
            # Get menus matching user's permissions
            stmt = select(Menu).where(
                Menu.tenant_id == user.tenant_id,
                Menu.status == 1,
                Menu.visible == 1,
                Menu.is_deleted == False
            ).order_by(Menu.sort.asc(), Menu.id.asc())
            
            result = await db.execute(stmt)
            all_menus = list(result.scalars().all())
            
            # Filter by permissions
            menus = []
            for menu in all_menus:
                # Directories and menus without permission code are accessible
                if menu.type == 1 or not menu.permission_code:
                    menus.append(menu)
                # Check if user has permission
                elif menu.permission_code in user_permissions:
                    menus.append(menu)
        
        # Cache menu IDs for 5 minutes
        if menus:
            menu_ids_str = ",".join(str(menu.id) for menu in menus)
            await redis.set(cache_key, menu_ids_str, ex=300)  # 5 minutes TTL
        
        return menus

    
    @staticmethod
    async def _get_user_permissions(db: AsyncSession, user: User) -> Set[str]:
        """Get all permission codes for a user."""
        from app.models.associations import UserRole, RolePermission
        from app.models.permission import Permission
        
        # Get user's roles
        stmt = select(UserRole.role_id).where(UserRole.user_id == user.id)
        result = await db.execute(stmt)
        role_ids = [row[0] for row in result.all()]
        
        if not role_ids:
            return set()
        
        # Get permissions for these roles
        stmt = select(Permission.code).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).where(
            RolePermission.role_id.in_(role_ids),
            Permission.status == 1,
            Permission.is_deleted == False
        )
        result = await db.execute(stmt)
        permissions = {row[0] for row in result.all() if row[0]}
        
        return permissions
    
    @staticmethod
    def build_menu_tree(menus: List[Menu]) -> List[MenuTreeNode]:
        """
        Build menu tree from flat list.
        
        Args:
            menus: Flat list of menus
            
        Returns:
            Tree structure with nested children
        """
        # Convert to dict for quick lookup
        menu_dict = {menu.id: MenuTreeNode.model_validate(menu) for menu in menus}
        
        # Build tree
        root_menus = []
        for menu in menus:
            menu_node = menu_dict[menu.id]
            
            if menu.parent_id is None or menu.parent_id == 0:
                # Root menu
                root_menus.append(menu_node)
            else:
                # Child menu
                parent = menu_dict.get(menu.parent_id)
                if parent:
                    parent.children.append(menu_node)
        
        return root_menus
    
    @staticmethod
    async def create_menu(db: AsyncSession, menu_data: MenuCreate, tenant_id: int) -> Menu:
        """Create a new menu."""
        # Validate parent menu
        if not await MenuService.validate_parent_menu(db, menu_data.parent_id, tenant_id):
            raise ValueError("Invalid parent menu")
        
        menu = Menu(
            **menu_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(menu)
        await db.flush()
        await db.refresh(menu)
        
        # Clear cache after create
        await MenuService._clear_menu_cache()
        
        return menu
    
    @staticmethod
    async def update_menu(db: AsyncSession, menu_id: int, menu_data: MenuUpdate) -> Optional[Menu]:
        """Update a menu."""
        stmt = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        
        if not menu:
            return None
        
        # Get update data
        update_data = menu_data.model_dump(exclude_unset=True)
        
        # Validate parent menu if being updated
        if 'parent_id' in update_data:
            new_parent_id = update_data['parent_id']
            
            # Validate parent exists
            if not await MenuService.validate_parent_menu(db, new_parent_id, menu.tenant_id):
                raise ValueError("Invalid parent menu")
            
            # Check circular reference
            if not await MenuService.check_circular_reference(db, menu_id, new_parent_id):
                raise ValueError("Circular reference detected")
        
        # Update fields
        for field, value in update_data.items():
            setattr(menu, field, value)
        
        await db.flush()
        await db.refresh(menu)
        
        # Clear cache after update
        await MenuService._clear_menu_cache()
        
        return menu
    
    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int) -> bool:
        """Soft delete a menu."""
        stmt = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()
        
        if not menu:
            return False
        
        menu.is_deleted = True
        await db.flush()
        
        # Clear cache after delete
        await MenuService._clear_menu_cache()
        
        return True
    
    @staticmethod
    async def get_all_menus(
        db: AsyncSession,
        tenant_id: int,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        menu_type: Optional[int] = None,
        status: Optional[int] = None
    ) -> tuple[List[Menu], int]:
        """
        Get all menus with pagination and filters.
        
        Returns:
            Tuple of (menus, total_count)
        """
        # Build query
        stmt = select(Menu).where(
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False
        )
        
        # Apply filters
        if keyword:
            stmt = stmt.where(Menu.name.ilike(f"%{keyword}%"))
        if menu_type is not None:
            stmt = stmt.where(Menu.type == menu_type)
        if status is not None:
            stmt = stmt.where(Menu.status == status)
        
        # Get total count
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Menu.sort.asc(), Menu.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        menus = list(result.scalars().all())
        
        return menus, total
    
    @staticmethod
    async def get_menu_by_id(db: AsyncSession, menu_id: int) -> Optional[Menu]:
        """Get a single menu by ID."""
        stmt = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_menus_tree(db: AsyncSession, tenant_id: int) -> List[MenuTreeNode]:
        """
        Get complete menu tree (without permission filtering).
        For admin use only.
        """
        stmt = select(Menu).where(
            Menu.tenant_id == tenant_id,
            Menu.is_deleted == False
        ).order_by(Menu.sort.asc(), Menu.id.asc())
        
        result = await db.execute(stmt)
        menus = list(result.scalars().all())
        
        return MenuService.build_menu_tree(menus)
    
    @staticmethod
    async def validate_parent_menu(db: AsyncSession, parent_id: Optional[int], tenant_id: int) -> bool:
        """
        Validate that parent menu exists.
        
        Returns:
            True if valid (parent_id is None or parent exists)
        """
        if parent_id is None or parent_id == 0:
            return True
        
        parent = await MenuService.get_menu_by_id(db, parent_id)
        if not parent:
            return False
        
        # Check tenant
        if parent.tenant_id != tenant_id:
            return False
        
        return True
    
    @staticmethod
    async def check_circular_reference(
        db: AsyncSession,
        menu_id: int,
        new_parent_id: Optional[int]
    ) -> bool:
        """
        Check if setting new_parent_id would create a circular reference.
        
        Returns:
            True if no circular reference (safe to update)
        """
        if new_parent_id is None or new_parent_id == 0:
            return True
        
        # Can't set self as parent
        if menu_id == new_parent_id:
            return False
        
        # Check if new_parent is a descendant of menu_id
        current_id = new_parent_id
        visited = set()
        
        while current_id and current_id != 0:
            if current_id in visited:
                # Infinite loop detected in existing data
                return False
            
            if current_id == menu_id:
                # Circular reference detected
                return False
            
            visited.add(current_id)
            
            # Get parent of current
            parent = await MenuService.get_menu_by_id(db, current_id)
            if not parent:
                break
            
            current_id = parent.parent_id
        
        return True
    
    @staticmethod
    async def _clear_menu_cache():
        """Clear all menu caches."""
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        
        # Delete all user menu caches
        # Note: This is a simple implementation. For production,
        # consider using Redis SCAN for better performance
        try:
            # Try to delete pattern (requires Redis 2.8+)
            cursor = 0
            pattern = "user_menus:*"
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            # Fallback: just log the error
            print(f"Warning: Failed to clear menu cache: {e}")


# Global instance
menu_service = MenuService()

