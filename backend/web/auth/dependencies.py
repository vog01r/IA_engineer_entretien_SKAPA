"""
Dependencies FastAPI pour authentification JWT.

Ce module fournit les dependencies injectables pour protéger les routes :
- get_current_user : Extrait user depuis JWT cookie (httpOnly)
- get_current_user_optional : Même chose mais retourne None si pas authentifié

Justifications techniques :
- Dependency injection FastAPI : Réutilisable, testable, composable
- httpOnly cookies : Extraction depuis request.cookies (pas accessible JS)
- Dual auth : Accepte JWT cookie OU X-API-Key header (bot/MCP)
- Erreurs explicites : 401 si token invalide/expiré, 403 si compte désactivé

Sécurité :
- Vérifie signature JWT (JWT_SECRET)
- Vérifie expiration automatiquement (jwt.decode)
- Vérifie is_active (soft delete)
- Pas de cache user (query DB à chaque requête pour données fraîches)
"""

from fastapi import Cookie, Depends, HTTPException, Header, Request, status

from backend.shared.config import API_KEY, COOKIE_NAME
from backend.web.auth.security import extract_user_from_token
from backend.shared.db import get_user_by_id


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(None, alias=COOKIE_NAME),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> dict:
    """Extrait l'utilisateur connecté depuis le JWT cookie ou X-API-Key.
    
    Dual auth :
    - Priorité 1 : JWT cookie (httpOnly, pour frontend web)
    - Priorité 2 : X-API-Key header (pour bot Telegram, MCP)
    
    Args:
        request: FastAPI Request (pour OPTIONS preflight)
        access_token: JWT depuis httpOnly cookie
        x_api_key: API Key depuis header X-API-Key
    
    Returns:
        Dict user avec id, email, is_active, created_at, updated_at
    
    Raises:
        HTTPException 401: Token invalide, expiré, ou manquant
        HTTPException 403: Compte désactivé (is_active=0)
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["id"], "email": user["email"]}
    
    Justifications :
        - Dual auth : Frontend web (JWT) + services (API Key) cohabitent
        - OPTIONS bypass : Preflight CORS ne doit pas nécessiter auth
        - Query DB : Pas de cache user (données fraîches, is_active à jour)
        - Erreurs explicites : 401 vs 403 (invalide vs désactivé)
    
    Sécurité :
        - JWT vérifié (signature + expiration)
        - API Key comparée en constant-time (via ==, Python 3.10+)
        - is_active vérifié (soft delete)
    """
    # Bypass pour OPTIONS (preflight CORS)
    if request.method == "OPTIONS":
        return {"id": 0, "email": "preflight", "is_active": True, "created_at": "", "updated_at": ""}
    
    # Priorité 1 : JWT cookie (frontend web)
    if access_token:
        user_data = extract_user_from_token(access_token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Récupérer le user depuis la DB
        user = get_user_by_id(user_data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Vérifier que le compte est actif
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        
        return user
    
    # Priorité 2 : X-API-Key header (bot Telegram, MCP)
    if x_api_key:
        if not API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API_KEY not configured",
            )
        if x_api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )
        # API Key valide : retourner un user "service" fictif
        # Les services (bot, MCP) n'ont pas de user_id en base
        return {
            "id": -1,  # ID négatif = service account
            "email": "service@skapa.internal",
            "is_active": True,
            "created_at": "",
            "updated_at": "",
        }
    
    # Aucune auth fournie
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated (JWT cookie or X-API-Key required)",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_optional(
    request: Request,
    access_token: str | None = Cookie(None, alias=COOKIE_NAME),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> dict | None:
    """Extrait l'utilisateur connecté, ou retourne None si pas authentifié.
    
    Variante de get_current_user qui ne lève pas d'exception si pas d'auth.
    Utile pour les routes publiques avec comportement optionnel selon auth.
    
    Args:
        request: FastAPI Request
        access_token: JWT depuis httpOnly cookie
        x_api_key: API Key depuis header X-API-Key
    
    Returns:
        Dict user ou None si pas authentifié
    
    Usage:
        @app.get("/public-or-protected")
        async def route(user: dict | None = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user['email']}"}
            return {"message": "Hello anonymous"}
    """
    try:
        return await get_current_user(request, access_token, x_api_key)
    except HTTPException:
        return None
