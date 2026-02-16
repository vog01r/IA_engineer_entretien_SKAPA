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
- Rate limiting (slowapi)
"""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.web.auth.endpoints import router as auth_router
from backend.shared.config import ALLOWED_ORIGINS

load_dotenv()

app = FastAPI(
    title="SKAPA Backend API",
    version="1.0.0",
    description="Backend modulaire : Web (JWT) + Services (API Key)",
)

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

# TODO: Ajouter weather_router et agent_router après migration

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
