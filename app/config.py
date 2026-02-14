import os

KEY = os.getenv("AUTH_KEY", "")
AUTH_KEY = os.getenv("AUTH_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///weather.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
