from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle manager for startup and shutdown actions.
    """
    setup_logging()
    logger.info("Starting %s in %s environment", settings.APP_NAME, settings.APP_ENV)
    logger.info("Connecting to database at: %s", settings.sanitized_database_url)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_application() -> FastAPI:
    """
    Application factory pattern initializing FastAPI with routers and middlewares.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Production-ready FastAPI demo project with MySQL, Docker, SQLAlchemy 2.0, and Alembic.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Centralized exception handling
    register_exception_handlers(app)

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Routers
    app.include_router(health_router)
    app.include_router(users_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()

