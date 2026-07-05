"""
Application-wide configuration and settings.
"""

from pydantic import BaseModel


class Settings(BaseModel):
    """Global application settings loaded from environment or defaults."""

    app_name: str = "Healthcare Supply Chain API"
    app_version: str = "0.1.0"
    debug: bool = True

    # CORS - allow the frontend dev server by default
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database (placeholder – swap for a real DB URL later)
    database_url: str = "sqlite:///./supply_chain.db"


settings = Settings()
