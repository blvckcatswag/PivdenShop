import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:PostgreSQL_SuperAdmin_Password1337!@localhost:5432/pivdenshop",
    )
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)

    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    API_DOCS_USERNAME = os.getenv("API_DOCS_USERNAME", "admin")
    API_DOCS_PASSWORD = os.getenv("API_DOCS_PASSWORD", "admin")

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
