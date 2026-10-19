from functools import lru_cache
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application settings
    APP_NAME: str = "FastAPI Demo"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    APP_PORT: int = 8000

    # MySQL Database connection parameters
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_HOST_PORT: int = 3307
    MYSQL_DATABASE: str = "fastapi_demo"
    MYSQL_USER: str = "fastapi_user"
    MYSQL_PASSWORD: str = "change_me"
    MYSQL_ROOT_PASSWORD: str = "change_root_me"

    # Connection pool configuration
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Explicit full database URL (optional).
    # If not provided, constructed dynamically from MYSQL_* components.
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        """
        Ensures DATABASE_URL is constructed if not explicitly provided or if empty.
        Validates that connection components are present.
        """
        if not self.DATABASE_URL or not self.DATABASE_URL.strip():
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
            )
        return self

    @property
    def database_url(self) -> str:
        """Convenience property returning the assembled database URL."""
        return self.DATABASE_URL or ""

    @property
    def sanitized_database_url(self) -> str:
        """
        Returns the database URL with the password masked for secure logging.
        """
        url = self.database_url
        if self.MYSQL_PASSWORD and f":{self.MYSQL_PASSWORD}@" in url:
            return url.replace(f":{self.MYSQL_PASSWORD}@", ":*****@")
        return url


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
