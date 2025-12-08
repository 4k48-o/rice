"""
Operation log middleware.
"""
import time
import json
from starlette.background import BackgroundTask
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.services.log_service import LogService
from app.utils.ip import IPUtils
from app.middleware.tenant import get_current_tenant_id


class OperationLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log operations.
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Filter out health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"] or request.method == "OPTIONS":
            return await call_next(request)
            
        start_time = time.time()
        
        # Prepare log data (capture pre-execution info)
        ip = IPUtils.get_ip(request)
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        url = request.url.path
        
        # Capture query params
        params = dict(request.query_params)
        
        # Execute request
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_msg = None
        except Exception as e:
            status_code = 500
            error_msg = str(e)
            raise e
        finally:
            # Calculate duration
            duration = int((time.time() - start_time) * 1000)
            
            # Get user info from context (set by Auth/Tenant middleware)
            # We assume user_id and username are available in context or request state
            user_id = None
            username = None
            tenant_id = get_current_tenant_id() or 0
            
            # Try to get from request state (set by deps)
            # Note: User object may be detached from session after request completes
            # So we try to access attributes safely
            if hasattr(request.state, "user"):
                try:
                    user = request.state.user
                    # Try to access id directly (should be cached)
                    user_id = getattr(user, 'id', None)
                    username = getattr(user, 'username', None)
                    tenant_id = getattr(user, 'tenant_id', None)
                except Exception:
                    # If user object is detached, try to get from state directly
                    # Some deps may store user info separately
                    user_id = getattr(request.state, 'user_id', None)
                    username = getattr(request.state, 'username', None)
                    tenant_id = getattr(request.state, 'tenant_id', None)
                
            # Get custom log info from request state (set by decorator)
            module = getattr(request.state, "log_module", None)
            summary = getattr(request.state, "log_summary", None)
            
            # If no manual summary, maybe generic one? 
            # Only record if it's a modification (POST/PUT/DELETE) OR explicitly marked
            should_log = method in ["POST", "PUT", "DELETE"] or module is not None
            
            if should_log:
                # Create a coroutine for logging
                log_coroutine = LogService.create_operation_log(
                    username=username or "Anonymous",
                    user_id=user_id,
                    method=method,
                    url=url,
                    ip=ip,
                    user_agent=user_agent,
                    status=1 if status_code < 400 else 0, # Simple success check
                    duration=duration,
                    module=module,
                    summary=summary,
                    params=params, 
                    error_msg=error_msg,
                    tenant_id=tenant_id or 0
                )

                # Define async wrapper to ensure coroutine is awaited
                async def write_op_log():
                    await log_coroutine
                
                if 'response' in locals():
                    if response.background:
                        # Append to existing background
                        old_bg = response.background
                        async def multiple_tasks():
                            await old_bg()
                            await write_op_log()
                        response.background = BackgroundTask(multiple_tasks)
                    else:
                        response.background = BackgroundTask(write_op_log)
        
        return response
