import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
    JWT_COOKIE_CSRF_PROTECT = os.getenv("JWT_COOKIE_CSRF_PROTECT", "false").lower() == "true"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "8"))
    )
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://sitefitness:sitefitness@localhost:5432/sitefitness",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    PUBLIC_FRONTEND_ORIGIN = os.getenv("PUBLIC_FRONTEND_ORIGIN", FRONTEND_ORIGIN)
    FRONTEND_ORIGINS = list(
        dict.fromkeys(
            origin
            for origin in [FRONTEND_ORIGIN, PUBLIC_FRONTEND_ORIGIN]
            if origin
        )
    )
    OPENWA_API_URL = os.getenv("OPENWA_API_URL", "").rstrip("/")
    OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
    OPENWA_SESSION_ID = os.getenv("OPENWA_SESSION_ID", "")
    OPENWA_DEFAULT_COUNTRY_CODE = os.getenv("OPENWA_DEFAULT_COUNTRY_CODE", "51")
    OPENWA_TIMEOUT_SECONDS = int(os.getenv("OPENWA_TIMEOUT_SECONDS", "10"))
