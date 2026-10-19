import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures application-wide logging with consistent formatting and log levels.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Custom log format with timestamp, level, logger name, and message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Adjust external chatty loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)

    logger = logging.getLogger("app")
    logger.info("Logging configured successfully (level=%s, env=%s)", logging.getLevelName(log_level), settings.APP_ENV)


logger = logging.getLogger("app")

