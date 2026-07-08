"""
Application-wide configuration and settings.

Reads from environment variables (loaded via ``python-dotenv``) with
safe defaults suitable for local development.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from the backend root directory
load_dotenv()


def _parse_cors_origins() -> list[str]:
    """Parse a comma-separated CORS_ORIGINS env var into a list."""
    raw = os.getenv("CORS_ORIGINS")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    # Fallback: allow common local dev servers
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]


class Settings(BaseModel):
    """Global application settings loaded from environment or defaults."""

    app_name: str = os.getenv("APP_NAME", "Healthcare Supply Chain API")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # CORS — allow the frontend dev server by default
    cors_origins: list[str] = _parse_cors_origins()

    # Database connection URL
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://smarthealth:smarthealth_dev@localhost:5432/smarthealth_db",
    )


settings = Settings()
