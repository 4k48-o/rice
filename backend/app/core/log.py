"""
Log decorators.
"""
from functools import wraps
from typing import Optional

from fastapi import Request


def log_module(module: str, summary: str):
    """
    Decorator to mark an endpoint for logging.
    
    Args:
        module: Module name (e.g. "User Management")
        summary: Operation summary (e.g. "Create User")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find Request object in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if request:
                request.state.log_module = module
                request.state.log_summary = summary
            
            # Call original function
            return await func(*args, **kwargs)
        return wrapper
    return decorator
