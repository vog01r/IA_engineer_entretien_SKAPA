import os

from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("AUTH_KEY", "")
AUTH_KEY = os.getenv("AUTH_KEY", "")
API_KEY = os.getenv("API_KEY", "")
# API_BASE_URL : URL pour les appels internes agent → API. Sur Railway, PORT est injecté.
_default_api_base = f"http://127.0.0.1:{os.getenv('PORT', '8000')}"
API_BASE_URL = os.getenv("API_BASE_URL", _default_api_base).rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
DATABASE_PATH = DATABASE_URL.replace("sqlite:///", "")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
