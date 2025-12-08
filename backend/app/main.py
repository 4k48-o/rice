"""
FastAPI main application.
"""
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import settings, init_db, close_db
from app.core.redis import RedisClient
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📝 Environment: {settings.APP_ENV}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Initialize database
    if settings.is_development:
        await init_db()
        print("✅ Database initialized")
    
    # Initialize Snowflake ID generator
    from app.utils.snowflake import init_snowflake
    init_snowflake(
        datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
        worker_id=settings.SNOWFLAKE_WORKER_ID,
        epoch=settings.SNOWFLAKE_EPOCH
    )
    print(f"✅ Snowflake ID generator initialized (DC:{settings.SNOWFLAKE_DATACENTER_ID}, Worker:{settings.SNOWFLAKE_WORKER_ID})")

    
    yield
    
    # Shutdown
    await close_db()
    print("👋 Application shutdown")



# Custom JSONResponse to preserve Chinese characters
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from datetime import datetime, date
import json

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime, date objects, and large integers."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # Handle large integers (Snowflake IDs) by converting to string to avoid JavaScript precision loss
        # JavaScript Number.MAX_SAFE_INTEGER is 2^53 - 1 = 9007199254740991
        if isinstance(obj, int) and abs(obj) > 9007199254740991:
            return str(obj)
        return super().default(obj)

class JSONResponse(FastAPIJSONResponse):
    """Custom JSON response that preserves non-ASCII characters (e.g., Chinese)."""
    
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=JSONEncoder,
        ).encode("utf-8")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant Enterprise Management System API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
    default_response_class=JSONResponse,  # Use custom JSON response
)




# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# I18n Middleware
from app.middleware.i18n import I18nMiddleware
app.add_middleware(I18nMiddleware)

# Operation Log Middleware
from app.middleware.log import OperationLogMiddleware
app.add_middleware(OperationLogMiddleware)




# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to response."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
# Exception handlers
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AppException
from app.core.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
