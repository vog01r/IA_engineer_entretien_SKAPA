"""
Entry point FastAPI - Backend SKAPA.

Architecture :
- web/ : API web avec authentification JWT (utilisateurs web)
- services/ : Services externes avec authentification API Key (bot, MCP)
- shared/ : Code partagé (config, DB, models)

Justifications :
- Séparation claire front/back/services
- Dual auth : JWT (web) + API Key (services)
- CORS configuré pour frontend
- Rate limiting (slowapi) : protection brute-force sur /auth et coût LLM sur /agent
"""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.web.auth.endpoints import router as auth_router
from backend.web.weather.endpoints import router as weather_router
from backend.web.agent.endpoints import router as agent_router
from backend.web.auth.dependencies import get_current_user
from backend.shared.config import ALLOWED_ORIGINS
from backend.shared.cache import get_cache_stats, clear_cache

load_dotenv()

# Rate limiter basé sur l'IP du client.
# Justification get_remote_address : simple, sans infra supplémentaire.
# En prod derrière un reverse proxy, configurer X-Forwarded-For.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SKAPA Backend API",
    version="1.0.0",
    description="Backend modulaire : Web (JWT) + Services (API Key)",
)

# Enregistrer le limiter et son handler d'erreur (retourne HTTP 429)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Requis pour httpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes Web (JWT auth)
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# Routes Weather (API Key auth pour services, JWT pour web)
app.include_router(
    weather_router,
    prefix="/weather",
    tags=["Weather"],
)

# Routes Agent (API Key auth pour services, JWT pour web)
app.include_router(
    agent_router,
    prefix="/agent",
    tags=["Agent"],
)

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint avec liens vers documentation."""
    return {
        "message": "SKAPA Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "auth": "/auth/login",
        "architecture": {
            "web": "JWT authentication (httpOnly cookies)",
            "services": "API Key authentication (bot, MCP)",
            "shared": "Config, DB, Models",
        },
    }


@app.get("/cache/stats", tags=["Monitoring"], dependencies=[Depends(get_current_user)])
async def cache_stats():
    """Retourne les statistiques du cache (hits, misses, hit rate). Auth requise."""
    stats = get_cache_stats()
    return {
        "cache": stats,
        "interpretation": {
            "hit_rate": f"{stats['hit_rate']:.1f}%",
            "efficiency": "excellent" if stats['hit_rate'] > 70 else "good" if stats['hit_rate'] > 50 else "poor",
        },
    }


@app.post("/cache/clear", tags=["Monitoring"], dependencies=[Depends(get_current_user)])
async def cache_clear():
    """Vide le cache (utile pour debug ou refresh forcé). Auth requise."""
    clear_cache()
    return {"message": "Cache cleared successfully"}
