import os
from datetime import timedelta


def _parse_cors_origins() -> str | list[str]:
    """Flask-CORS accepts '*' or a list of origins; support comma-separated env."""
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts if parts else "*"


def _database_url() -> str:
    """Normalize DATABASE_URL for SQLAlchemy (Render/Heroku use postgres://)."""
    uri = os.getenv("DATABASE_URL", "sqlite:///litup.db")
    if uri.startswith("postgres://"):
        uri = "postgresql://" + uri[len("postgres://") :]
    return uri


class Config:
    # 32+ chars avoids PyJWT "insecure key length" warnings for HS256 in dev
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-please-change-this-secret-key-32bytes!!",
    )

    # Works for SQLite (dev) and Postgres (prod via DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))
    )

    # Allow separate hosting of frontend (GitHub Pages) during dev/prod
    CORS_ORIGINS = _parse_cors_origins()


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False

