import logging
from typing import Dict
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from app.db.session import get_db

logger = logging.getLogger("app.api.health")

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Returns the immediate operational status of the FastAPI service.",
)
def check_health() -> HealthResponse:
    """Returns basic service health information."""
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Readiness Check",
    description="Verifies that the application can actively query the MySQL database.",
    responses={
        503: {
            "description": "Database is unreachable or failed health check query",
            "content": {
                "application/json": {
                    "example": {"error": "DatabaseConnectionError", "detail": "Database connection is unavailable."}
                }
            },
        }
    },
)
def check_readiness(db: Session = Depends(get_db)) -> ReadinessResponse:
    """Verifies database connectivity using an active SELECT 1 ping."""
    try:
        db.execute(text("SELECT 1"))
        return ReadinessResponse(status="ready", database="connected")
    except Exception as exc:
        logger.error("Readiness check failed: %s", str(exc))
        raise DatabaseConnectionError(message="Database connection failed or timed out.") from exc

