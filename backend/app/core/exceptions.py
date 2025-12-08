"""
Global exception classes.
"""
from typing import Any, Optional

class AppException(Exception):
    """Base exception for application."""
    def __init__(
        self, 
        code: int = 500, 
        message: str = "Internal Server Error", 
        data: Any = None,
        http_status_code: int = 500
    ):
        self.code = code
        self.message = message
        self.data = data
        self.http_status_code = http_status_code
        super().__init__(message)

class BusinessException(AppException):
    """
    Business logic exception.
    Usually returns HTTP 200 with specific error code, or HTTP 400.
    """
    def __init__(
        self, 
        code: int = 400, 
        message: str = "Business Error", 
        data: Any = None,
        http_status_code: int = 200 # Often 200 in enterprise apps to let frontend handle by code
    ):
        super().__init__(
            code=code, 
            message=message, 
            data=data,
            http_status_code=http_status_code
        )

class SystemException(AppException):
    """
    System level exception.
    """
    def __init__(
        self, 
        code: int = 500, 
        message: str = "System Error", 
        data: Any = None,
        http_status_code: int = 500
    ):
        super().__init__(
            code=code, 
            message=message, 
            data=data,
            http_status_code=http_status_code
        )

# Predefined Common Exceptions

class AuthException(BusinessException):
    """Authentication failed."""
    def __init__(self, message: str = "Authentication failed", data: Any = None):
        super().__init__(code=401, message=message, data=data, http_status_code=401)

class PermissionException(BusinessException):
    """Permission denied."""
    def __init__(self, message: str = "Permission denied", data: Any = None):
        super().__init__(code=403, message=message, data=data, http_status_code=403)

class NotFoundException(BusinessException):
    """Resource not found."""
    def __init__(self, message: str = "Resource not found", data: Any = None):
        super().__init__(code=404, message=message, data=data, http_status_code=404)

class ValidationError(BusinessException):
    """Data validation error."""
    def __init__(self, message: str = "Validation error", data: Any = None):
        super().__init__(code=422, message=message, data=data, http_status_code=422)
