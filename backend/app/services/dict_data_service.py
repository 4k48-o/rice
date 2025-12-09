"""
Dictionary data service for dictionary data management.
"""
import json
from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dict_data import DictData
from app.schemas.dict_data import DictDataCreate, DictDataUpdate


class DictDataService:
    """Dictionary data service."""
    
    @staticmethod
    async def get_dict_data_by_type_cached(
        db: AsyncSession,
        type_code: str,
        tenant_id: str
    ) -> List[DictData]:
        """
        Get dictionary data by type code with Redis cache.
        
        Args:
            db: Database session
            type_code: Dictionary type code
            tenant_id: Tenant ID
            
        Returns:
            List of dictionary data
        """
        from app.core.redis import RedisClient
        redis = RedisClient.get_client()
        cache_key = f"dict:{tenant_id}:{type_code}"
        
        # Try to get from cache
        cached_data = await redis.get(cache_key)
        if cached_data:
            try:
                data_list = json.loads(cached_data)
                # Convert back to DictData objects (simplified - just return dicts)
                # For full objects, we'd need to reconstruct from DB
                # For now, return cached data as-is and let API layer handle it
                # Actually, let's fetch from DB to ensure consistency
                # Cache hit means we can skip the type lookup
                pass
            except:
                pass
        
        # Get dict type
        from app.services.dict_type_service import dict_type_service
        dict_type = await dict_type_service.get_dict_type_by_code(db, type_code, tenant_id)
        if not dict_type:
            return []
        
        # Get dict data
        stmt = select(DictData).where(
            DictData.dict_type_id == dict_type.id,
            DictData.tenant_id == tenant_id,
            DictData.status == 1,
            DictData.is_deleted == False
        ).order_by(DictData.sort.asc(), DictData.id.asc())
        
        result = await db.execute(stmt)
        dict_data_list = list(result.scalars().all())
        
        # Cache the data (serialize to JSON)
        if dict_data_list:
            cache_data = [
                {
                    "id": item.id,
                    "label": item.label,
                    "value": item.value,
                    "sort": item.sort,
                    "status": item.status,
                    "css_class": item.css_class,
                    "color": item.color,
                    "icon": item.icon,
                }
                for item in dict_data_list
            ]
            await redis.set(cache_key, json.dumps(cache_data), ex=3600)  # 1 hour TTL
        
        return dict_data_list
    
    @staticmethod
    async def get_all_dict_data(
        db: AsyncSession,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        dict_type_id: Optional[str] = None,
        status: Optional[int] = None
    ) -> Tuple[List[DictData], int]:
        """
        Get all dictionary data with pagination and filters.
        
        Returns:
            Tuple of (dict_data, total_count)
        """
        # Build query
        stmt = select(DictData).where(
            DictData.tenant_id == tenant_id,
            DictData.is_deleted == False
        )
        
        # Apply filters
        if keyword:
            stmt = stmt.where(
                or_(
                    DictData.label.ilike(f"%{keyword}%"),
                    DictData.value.ilike(f"%{keyword}%")
                )
            )
        
        if dict_type_id:
            stmt = stmt.where(DictData.dict_type_id == dict_type_id)
        
        if status is not None:
            stmt = stmt.where(DictData.status == status)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        stmt = stmt.order_by(DictData.sort.asc(), DictData.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        dict_data = list(result.scalars().all())
        
        return dict_data, total
    
    @staticmethod
    async def get_dict_data(db: AsyncSession, dict_data_id: str, tenant_id: str) -> Optional[DictData]:
        """Get dictionary data by ID."""
        stmt = select(DictData).where(
            DictData.id == dict_data_id,
            DictData.tenant_id == tenant_id,
            DictData.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_dict_data(db: AsyncSession, dict_data_data: DictDataCreate, tenant_id: str) -> DictData:
        """Create a new dictionary data."""
        # Validate dict_type_id exists
        from app.services.dict_type_service import dict_type_service
        dict_type = await dict_type_service.get_dict_type(db, dict_data_data.dict_type_id, tenant_id)
        if not dict_type:
            raise ValueError("Dictionary type not found")
        
        # Check if value already exists for this type
        stmt = select(DictData).where(
            DictData.dict_type_id == dict_data_data.dict_type_id,
            DictData.value == dict_data_data.value,
            DictData.is_deleted == False
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Dictionary data value already exists for this type")
        
        dict_data = DictData(
            **dict_data_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(dict_data)
        await db.flush()
        await db.refresh(dict_data)
        
        # Clear cache
        await DictDataService._clear_dict_cache_by_type_id(db, dict_data_data.dict_type_id, tenant_id)
        
        return dict_data
    
    @staticmethod
    async def update_dict_data(
        db: AsyncSession,
        dict_data_id: str,
        dict_data_data: DictDataUpdate,
        tenant_id: str
    ) -> Optional[DictData]:
        """Update a dictionary data."""
        dict_data = await DictDataService.get_dict_data(db, dict_data_id, tenant_id)
        if not dict_data:
            return None
        
        # Get update data
        update_data = dict_data_data.model_dump(exclude_unset=True)
        
        # Validate dict_type_id if being updated
        if 'dict_type_id' in update_data:
            from app.services.dict_type_service import dict_type_service
            dict_type = await dict_type_service.get_dict_type(db, update_data['dict_type_id'], tenant_id)
            if not dict_type:
                raise ValueError("Dictionary type not found")
        
        # Check value uniqueness if value is being updated
        if 'value' in update_data:
            new_value = update_data['value']
            dict_type_id = update_data.get('dict_type_id', dict_data.dict_type_id)
            
            stmt = select(DictData).where(
                DictData.dict_type_id == dict_type_id,
                DictData.value == new_value,
                DictData.id != dict_data_id,
                DictData.is_deleted == False
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                raise ValueError("Dictionary data value already exists for this type")
        
        # Update fields
        for field, value in update_data.items():
            setattr(dict_data, field, value)
        
        await db.flush()
        await db.refresh(dict_data)
        
        # Clear cache
        await DictDataService._clear_dict_cache_by_type_id(db, dict_data.dict_type_id, tenant_id)
        
        return dict_data
    
    @staticmethod
    async def delete_dict_data(db: AsyncSession, dict_data_id: str, tenant_id: str) -> bool:
        """Soft delete a dictionary data."""
        dict_data = await DictDataService.get_dict_data(db, dict_data_id, tenant_id)
        if not dict_data:
            return False
        
        dict_type_id = dict_data.dict_type_id
        dict_data.is_deleted = True
        await db.flush()
        
        # Clear cache
        await DictDataService._clear_dict_cache_by_type_id(db, dict_type_id, tenant_id)
        
        return True
    
    @staticmethod
    async def _clear_dict_cache_by_type_id(db: AsyncSession, dict_type_id: str, tenant_id: str):
        """Clear dictionary cache by type ID."""
        # Get dict type to get code
        from app.services.dict_type_service import dict_type_service
        dict_type = await dict_type_service.get_dict_type(db, dict_type_id, tenant_id)
        if dict_type:
            await dict_type_service._clear_dict_cache(tenant_id, dict_type.code)


dict_data_service = DictDataService()

