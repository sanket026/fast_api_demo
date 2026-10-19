import logging
from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class UserNotFoundError(AppException):
    """Raised when a requested user is not found."""

    def __init__(self, user_id: int) -> None:
        super().__init__(
            message=f"User with ID {user_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserAlreadyExistsError(AppException):
    """Raised when a user creation or update violates unique constraints."""

    def __init__(self, field: str, value: str) -> None:
        super().__init__(
            message=f"A user with this {field} '{value}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
            details={"field": field, "value": value},
        )


class DatabaseConnectionError(AppException):
    """Raised when the database connection cannot be established or verified."""

    def __init__(self, message: str = "Database connection is unavailable.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom and centralized exception handlers on the FastAPI application.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        content = {
            "error": exc.__class__.__name__,
            "detail": exc.message,
        }
        if exc.details is not None:
            content["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "detail": "Request validation failed.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log full traceback internally, never leak internal details to clients
        logger.exception("Unhandled server error on %s %s: %s", request.method, request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "detail": "An unexpected error occurred. Please try again later.",
            },
        )

