"""Application configuration. Secrets must come from environment in production."""
import os
from datetime import timedelta
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-change-in-production")

    BASE_DIR = Path(__file__).resolve().parent
    INSTANCE_DIR = BASE_DIR / "instance"

    # SQLAlchemy — use DATABASE_URL; default SQLite (absolute path, Windows-safe)
    _sqlite_path = (INSTANCE_DIR / "app.db").resolve().as_posix()
    _db_url = os.environ.get("DATABASE_URL", f"sqlite:///{_sqlite_path}")
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True, "pool_recycle": 300}
        if _db_url.startswith("mysql")
        else {}
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT in httpOnly cookies
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "60"))
    )

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    ALLOW_PUBLIC_ADMIN_REGISTRATION = (
        os.environ.get("ALLOW_PUBLIC_ADMIN_REGISTRATION", "false").lower() == "true"
    )

    MAX_FAILED_LOGIN_ATTEMPTS = int(os.environ.get("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_MINUTES = int(os.environ.get("LOCKOUT_MINUTES", "15"))

    CAPTCHA_TTL_SECONDS = 600
