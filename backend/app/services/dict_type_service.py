"""
Dictionary type service for dictionary type management.
"""
from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dict_type import DictType
from app.schemas.dict_type import DictTypeCreate, DictTypeUpdate


class DictTypeService:
    """Dictionary type service."""
    
    @staticmethod
    async def get_all_dict_types(
        db: AsyncSession,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None
    ) -> Tuple[List[DictType], int]:
        """
        Get all dictionary types with pagination and filters.
        
        Returns:
            Tuple of (dict_types, total_count)
        """
        # Build query
        stmt = select(DictType).where(
            DictType.tenant_id == tenant_id,
            DictType.is_deleted == False
        )
        
        # Apply filters
        if keyword:
            stmt = stmt.where(
                or_(
                    DictType.name.ilike(f"%{keyword}%"),
                    DictType.code.ilike(f"%{keyword}%")
                )
            )
        
        if status is not None:
            stmt = stmt.where(DictType.status == status)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        stmt = stmt.order_by(DictType.sort.asc(), DictType.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        dict_types = list(result.scalars().all())
        
        return dict_types, total
    
    @staticmethod
    async def get_dict_type(db: AsyncSession, dict_type_id: str, tenant_id: str) -> Optional[DictType]:
        """Get dictionary type by ID."""
        stmt = select(DictType).where(
            DictType.id == dict_type_id,
            DictType.tenant_id == tenant_id,
            DictType.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_dict_type_by_code(db: AsyncSession, code: str, tenant_id: str) -> Optional[DictType]:
        """Get dictionary type by code."""
        stmt = select(DictType).where(
            DictType.code == code,
            DictType.tenant_id == tenant_id,
            DictType.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_dict_type(db: AsyncSession, dict_type_data: DictTypeCreate, tenant_id: str) -> DictType:
        """Create a new dictionary type."""
        # Check if code already exists
        existing = await dict_type_service.get_dict_type_by_code(db, dict_type_data.code, tenant_id)
        if existing:
            raise ValueError("Dictionary type code already exists")
        
        dict_type = DictType(
            **dict_type_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(dict_type)
        await db.flush()
        await db.refresh(dict_type)
        
        return dict_type
    
    @staticmethod
    async def update_dict_type(
        db: AsyncSession,
        dict_type_id: str,
        dict_type_data: DictTypeUpdate,
        tenant_id: str
    ) -> Optional[DictType]:
        """Update a dictionary type."""
        dict_type = await DictTypeService.get_dict_type(db, dict_type_id, tenant_id)
        if not dict_type:
            return None
        
        # Get update data
        update_data = dict_type_data.model_dump(exclude_unset=True)
        
        # Check code uniqueness if code is being updated
        if 'code' in update_data and update_data['code'] != dict_type.code:
            existing = await dict_type_service.get_dict_type_by_code(db, update_data['code'], tenant_id)
            if existing:
                raise ValueError("Dictionary type code already exists")
        
        # Update fields
        for field, value in update_data.items():
            setattr(dict_type, field, value)
        
        await db.flush()
        await db.refresh(dict_type)
        
        # Clear cache for this dict type
        await DictTypeService._clear_dict_cache(tenant_id, dict_type.code)
        
        return dict_type
    
    @staticmethod
    async def delete_dict_type(db: AsyncSession, dict_type_id: str, tenant_id: str) -> bool:
        """Soft delete a dictionary type."""
        dict_type = await DictTypeService.get_dict_type(db, dict_type_id, tenant_id)
        if not dict_type:
            return False
        
        # Check if there are any dict_data associated
        from app.models.dict_data import DictData
        stmt = select(func.count()).select_from(DictData).where(
            DictData.dict_type_id == dict_type_id,
            DictData.is_deleted == False
        )
        result = await db.execute(stmt)
        count = result.scalar() or 0
        
        if count > 0:
            raise ValueError("Cannot delete dictionary type with associated data")
        
        dict_type.is_deleted = True
        await db.flush()
        
        # Clear cache
        await DictTypeService._clear_dict_cache(tenant_id, dict_type.code)
        
        return True
    
    @staticmethod
    async def _clear_dict_cache(tenant_id: str, type_code: str):
        """Clear dictionary cache for a specific type."""
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        cache_key = f"dict:{tenant_id}:{type_code}"
        await redis.delete(cache_key)


dict_type_service = DictTypeService()

