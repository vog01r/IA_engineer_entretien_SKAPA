import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.agent import router as agent_router
from app.api.v1.endpoints.mcp_info import router as mcp_info_router
from app.api.v1.endpoints.weather import router as weather_router
from app.config import ALLOWED_ORIGINS, API_KEY, AUTH_KEY

load_dotenv()

app = FastAPI(title="API Météo + MCP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check_token(t: str):
    return AUTH_KEY and t == AUTH_KEY


def verify_api_key(request: Request, x_api_key: str | None = Header(None, alias="X-API-Key")):
    """Vérifie la clé API. Les requêtes OPTIONS (preflight CORS) sont autorisées sans clé."""
    if request.method == "OPTIONS":
        return None
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY non configurée")
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Clé API invalide")
    return x_api_key


app.include_router(
    weather_router,
    tags=["Météo"],
    prefix="/weather",
    dependencies=[Depends(verify_api_key)],
)

app.include_router(
    agent_router,
    tags=["Agent"],
    prefix="/agent",
    dependencies=[Depends(verify_api_key)],
)

app.include_router(
    mcp_info_router,
    prefix="/mcp",
    tags=["MCP"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "API Météo", "docs": "/docs", "weather": "/weather"}
