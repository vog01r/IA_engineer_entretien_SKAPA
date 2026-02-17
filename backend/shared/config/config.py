import os

from dotenv import load_dotenv

load_dotenv()

# Legacy keys (à nettoyer progressivement)
KEY = os.getenv("AUTH_KEY", "")
AUTH_KEY = os.getenv("AUTH_KEY", "")

# API Key pour services externes (bot Telegram, MCP)
API_KEY = os.getenv("API_KEY", "")

# API_BASE_URL : URL pour les appels internes agent → API. Sur Railway, PORT est injecté.
_default_api_base = f"http://127.0.0.1:{os.getenv('PORT', '8000')}"
API_BASE_URL = os.getenv("API_BASE_URL", _default_api_base).rstrip("/")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
DATABASE_PATH = DATABASE_URL.replace("sqlite:///", "")

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# CORS
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

# JWT Configuration (requis uniquement pour l'API web ; service MCP n'utilise pas JWT)
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Cookie Configuration (httpOnly pour sécurité XSS)
COOKIE_NAME = "skapa_access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # True en prod (HTTPS)
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # lax = protection CSRF basique
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)  # None = même domaine uniquement

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
