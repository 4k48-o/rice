"""
Global exception handlers.
"""
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException, SystemException, BusinessException
from app.core.i18n import i18n

async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "code": exc.code,
            "message": i18n.t(exc.message) if exc.message in ["success", "validation_error", "system_error"] else exc.message, 
            # Note: For business exceptions, the message might be a key or a raw string. 
            # Ideally, we should pass keys to BusinessException.
            # For now, let's assume if it matches a key in i18n, it translates.
            "data": exc.data,
            "timestamp": int(time.time()),
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
            "timestamp": int(time.time()),
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        # Sanitize error dict to avoid non-serializable objects (like Exception instances in ctx)
        sanitized = {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        errors.append(sanitized)

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": i18n.t("validation_error"),
            "data": {"errors": errors},
            "timestamp": int(time.time()),
        },
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    print(f"🔥 Unhandled System Exception: {exc}") # Should use logger
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": i18n.t("system_error"),
            "data": str(exc) if True else None, # TODO: Hide details in production settings.DEBUG
            "timestamp": int(time.time()),
        },
    )
