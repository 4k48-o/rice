"""
User service.
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role import Role
from app.models.associations import UserRole
from app.models.tenant import Tenant

from app.core.security import get_password_hash


class UserService:
    """User business logic."""
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str, tenant_id: int = None) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Optional[User]: User object
        """
        stmt = select(User).where(
            User.username == username,
            User.is_deleted == False
        )
        if tenant_id is not None:
            stmt = stmt.where(User.tenant_id == tenant_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str, tenant_id: int = None) -> Optional[User]:
        """
        Alias for get_by_username for backward compatibility.
        """
        return await UserService.get_by_username(db, username, tenant_id)
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(
            User.id == user_id, 
            User.is_deleted == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        username: str = None,
        phone: str = None,
        status: int = None,
        dept_id: int = None,
        tenant_id: int = None
    ) -> Tuple[List[User], int]:
        """
        Get user list with pagination and filtering.
        """
        # Build base query
        base_stmt = select(User).where(User.is_deleted == False)
        
        if tenant_id:
            base_stmt = base_stmt.where(User.tenant_id == tenant_id)
        if username:
            base_stmt = base_stmt.where(User.username.like(f"%{username}%"))
        if phone:
            base_stmt = base_stmt.where(User.phone.like(f"%{phone}%"))
        if status is not None:
            base_stmt = base_stmt.where(User.status == status)
        if dept_id:
            base_stmt = base_stmt.where(User.dept_id == dept_id)
            
        # Count total (optimized)
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Pagination
        stmt = base_stmt.order_by(User.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(stmt)
        return result.scalars().all(), total

    @staticmethod
    async def create_user(
        db: AsyncSession, 
        user_in: dict, # Using dict or Schema
        tenant_id: int = 0
    ) -> User:
        """Create a new user with roles."""
        # Check if username exists
        stmt = select(User).where(User.username == user_in["username"])
        result = await db.execute(stmt)
        if result.scalars().first():
            raise ValueError("Username already exists")
            
        hashed_password = get_password_hash(user_in["password"])
        
        db_user = User(
            username=user_in["username"],
            password=hashed_password,
            email=user_in.get("email"),
            phone=user_in.get("phone"),
            real_name=user_in.get("real_name"),
            nickname=user_in.get("nickname"),
            dept_id=user_in.get("dept_id"),
            position=user_in.get("position"),
            gender=user_in.get("gender", 0),
            status=user_in.get("status", 1),
            remark=user_in.get("remark"),
            tenant_id=tenant_id,
            user_type=2 # Normal user
        )
        db.add(db_user)
        await db.flush() # Get ID
        
        # Handle roles
        if "role_ids" in user_in and user_in["role_ids"]:
            for role_id in user_in["role_ids"]:
                user_role = UserRole(
                    user_id=db_user.id, 
                    role_id=role_id,
                    tenant_id=tenant_id
                )
                db.add(user_role)
                
        return db_user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_in: dict
    ) -> Optional[User]:
        """Update user."""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
            
        # Update basic fields
        for field in ["email", "phone", "real_name", "nickname", "dept_id", "position", "gender", "status", "remark"]:
            if field in user_in and user_in[field] is not None:
                setattr(user, field, user_in[field])
                
        # Update roles if provided
        if "role_ids" in user_in and user_in["role_ids"] is not None:
            # Delete existing roles
            stmt = delete(UserRole).where(UserRole.user_id == user_id)
            await db.execute(stmt)
            
            # Add new roles
            if user_in["role_ids"]:  # Only add if list is not empty
                for role_id in user_in["role_ids"]:
                    user_role = UserRole(
                        user_id=user_id, 
                        role_id=role_id,
                        tenant_id=user.tenant_id
                    )
                    db.add(user_role)
        
        await db.flush()  # Flush changes to get updated user
        await db.refresh(user)  # Refresh to get latest state
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Soft delete user."""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False
            
        user.is_deleted = True
        # user.deleted_at = datetime.now() # Handled by mixin if implemented, else manual
        
        return True

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        user_id: int,
        password: str
    ) -> bool:
        """Reset user password."""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False
            
        hashed_password = get_password_hash(password)
        user.password = hashed_password
        user.password_updated_at = datetime.now()
        user.must_change_password = False
        
        return True
    
    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
        """Get all roles for a user."""
        stmt = select(Role).join(
            UserRole, UserRole.role_id == Role.id
        ).where(
            UserRole.user_id == user_id,
            Role.is_deleted == False
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

# Global instance
user_service = UserService()
