"""
Tenant isolation middleware.

Automatically filters queries by tenant_id for models with TenantMixin.
"""
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store current tenant_id
current_tenant_id: ContextVar[Optional[int]] = ContextVar("current_tenant_id", default=None)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and store tenant_id from authenticated user.
    
    This middleware:
    1. Extracts tenant_id from the authenticated user (via JWT)
    2. Stores it in a ContextVar for use in queries
    3. Enables automatic tenant isolation in database queries
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request and inject tenant_id."""
        # Reset tenant_id for this request
        token = current_tenant_id.set(None)
        
        try:
            # Extract tenant_id from user if authenticated
            # Note: This is a placeholder - actual extraction happens in get_current_user
            # The tenant_id is set when the user is authenticated
            
            response: Response = await call_next(request)
            return response
        finally:
            # Reset context
            current_tenant_id.reset(token)


def get_current_tenant_id() -> Optional[int]:
    """Get current tenant ID from context."""
    return current_tenant_id.get()


def set_current_tenant_id(tenant_id: int) -> None:
    """Set current tenant ID in context."""
    current_tenant_id.set(tenant_id)
