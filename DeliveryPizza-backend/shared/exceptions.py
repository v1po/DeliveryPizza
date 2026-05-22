"""
Custom exceptions for microservices.
"""
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base API exception."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


# Authentication exceptions
class InvalidCredentialsException(BaseAPIException):
    """Invalid credentials provided."""
    
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS",
        )


class TokenExpiredException(BaseAPIException):
    """Token has expired."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            error_code="TOKEN_EXPIRED",
        )


class InvalidTokenException(BaseAPIException):
    """Invalid token provided."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            error_code="INVALID_TOKEN",
        )


class TokenBlacklistedException(BaseAPIException):
    """Token has been blacklisted."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            error_code="TOKEN_REVOKED",
        )


# Authorization exceptions
class PermissionDeniedException(BaseAPIException):
    """User doesn't have required permissions."""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED",
        )


# Resource exceptions
class NotFoundException(BaseAPIException):
    """Resource not found."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            error_code="NOT_FOUND",
        )


class AlreadyExistsException(BaseAPIException):
    """Resource already exists."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} already exists",
            error_code="ALREADY_EXISTS",
        )


# Validation exceptions
class ValidationException(BaseAPIException):
    """Validation error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


# Service exceptions
class ServiceUnavailableException(BaseAPIException):
    """External service is unavailable."""
    
    def __init__(self, service: str = "Service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} is temporarily unavailable",
            error_code="SERVICE_UNAVAILABLE",
        )
