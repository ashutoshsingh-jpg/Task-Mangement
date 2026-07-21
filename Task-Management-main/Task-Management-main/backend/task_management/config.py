"""Application configuration.

Defines configuration classes that load their values from environment
variables (via python-dotenv), so no secrets are hard-coded in source.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Load variables from a .env file (if present) into the process
# environment before Config reads them.
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # Flask core
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_SECURE: bool = False

    # SQLAlchemy / MySQL
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://user:password@localhost:3306/task_management_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
    )

    # Ping the connection before each checkout from the pool so a MySQL
    # connection that timed out / was dropped by the server doesn't
    # surface as a confusing error on the next request or health check.
    SQLALCHEMY_ENGINE_OPTIONS: dict = {"pool_pre_ping": True}

    # CORS
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")

    # Auth token lifetime (used once JWT/session auth is implemented).
    TOKEN_EXPIRATION: timedelta = timedelta(hours=8)


class DevelopmentConfig(Config):
    """Configuration for local development."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Configuration for production deployment."""

    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True
