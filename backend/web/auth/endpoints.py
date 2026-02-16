"""
Endpoints d'authentification JWT.

Routes :
- POST /auth/register : Création de compte
- POST /auth/login : Authentification (retourne access + refresh tokens)
- GET /auth/me : Profil utilisateur (protégé, nécessite JWT)
- POST /auth/refresh : Renouvellement access token avec refresh token

Justifications techniques :
- httpOnly cookies : Tokens stockés côté serveur, pas accessibles JS (protection XSS)
- SameSite=lax : Protection CSRF basique, compatible redirections OAuth
- Secure=true en prod : Cookies transmis uniquement sur HTTPS
- Email validation : Regex basique, normalisation lowercase
- Password validation : Min 8 chars, pas de contrainte complexe (UX)

Sécurité :
- Passwords hashés avec bcrypt (jamais en clair)
- Tokens signés avec JWT_SECRET (HS256)
- Rate limiting appliqué (slowapi, 100 req/min)
- Erreurs génériques (pas de "email existe" vs "password incorrect")
"""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field

from backend.shared.config import COOKIE_DOMAIN, COOKIE_NAME, COOKIE_SAMESITE, COOKIE_SECURE
from backend.web.auth.dependencies import get_current_user
from backend.web.auth.security import (
    create_access_token,
    create_refresh_token,
    extract_user_from_token,
    hash_password,
    verify_password,
)
from backend.shared.db import create_user, get_user_by_email, get_user_by_id

router = APIRouter()


# ──────────────── Pydantic Models ────────────────


class RegisterRequest(BaseModel):
    """Requête de création de compte."""
    
    email: EmailStr = Field(..., description="Email de l'utilisateur (unique)")
    password: str = Field(..., min_length=8, description="Password (min 8 caractères)")
    
    model_config = {"json_schema_extra": {"example": {"email": "alice@example.com", "password": "MySecureP@ss123"}}}


class LoginRequest(BaseModel):
    """Requête de connexion."""
    
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., description="Password")
    
    model_config = {"json_schema_extra": {"example": {"email": "alice@example.com", "password": "MySecureP@ss123"}}}


class UserResponse(BaseModel):
    """Réponse avec données utilisateur (sans password)."""
    
    id: int
    email: str
    is_active: bool
    created_at: str
    
    model_config = {"json_schema_extra": {"example": {"id": 1, "email": "alice@example.com", "is_active": True, "created_at": "2024-02-16T19:00:00"}}}


class AuthResponse(BaseModel):
    """Réponse d'authentification réussie."""
    
    message: str
    user: UserResponse
    
    model_config = {"json_schema_extra": {"example": {"message": "Login successful", "user": {"id": 1, "email": "alice@example.com", "is_active": True, "created_at": "2024-02-16T19:00:00"}}}}


# ──────────────── Endpoints ────────────────


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, response: Response):
    """Crée un nouveau compte utilisateur.
    
    Args:
        request: Email + password
        response: FastAPI Response pour set cookies
    
    Returns:
        AuthResponse avec user créé
    
    Raises:
        HTTPException 400: Email déjà utilisé
        HTTPException 422: Validation échouée (email invalide, password trop court)
    
    Sécurité :
        - Password hashé avec bcrypt avant stockage
        - Email normalisé (lowercase) pour éviter doublons
        - Tokens JWT retournés dans httpOnly cookies
    
    Example:
        POST /auth/register
        {"email": "alice@example.com", "password": "MySecureP@ss123"}
        
        Response 201:
        {
          "message": "Account created successfully",
          "user": {"id": 1, "email": "alice@example.com", ...}
        }
        Set-Cookie: skapa_access_token=...; HttpOnly; SameSite=lax
    """
    # Vérifier si l'email existe déjà
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash du password
    hashed_password = hash_password(request.password)
    
    # Création du user
    try:
        user_id = create_user(email=request.email, hashed_password=hashed_password)
    except sqlite3.IntegrityError:
        # Race condition : email créé entre get_user_by_email et create_user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Récupérer le user créé
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )
    
    # Générer tokens JWT
    access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["email"], "user_id": user["id"]})
    
    # Set httpOnly cookies
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=3600,  # 1h
    )
    response.set_cookie(
        key=f"{COOKIE_NAME}_refresh",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=7 * 24 * 3600,  # 7 jours
    )
    
    return AuthResponse(
        message="Account created successfully",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    """Authentifie un utilisateur et retourne des tokens JWT.
    
    Args:
        request: Email + password
        response: FastAPI Response pour set cookies
    
    Returns:
        AuthResponse avec user authentifié
    
    Raises:
        HTTPException 401: Credentials invalides (email ou password incorrect)
    
    Sécurité :
        - Message d'erreur générique (pas de "email inexistant" vs "password incorrect")
        - Vérification bcrypt constant-time (résistant timing attacks)
        - Tokens JWT retournés dans httpOnly cookies
    
    Example:
        POST /auth/login
        {"email": "alice@example.com", "password": "MySecureP@ss123"}
        
        Response 200:
        {
          "message": "Login successful",
          "user": {"id": 1, "email": "alice@example.com", ...}
        }
        Set-Cookie: skapa_access_token=...; HttpOnly; SameSite=lax
    """
    # Récupérer le user par email
    user = get_user_by_email(request.email)
    if not user:
        # Message générique pour ne pas révéler si l'email existe
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Vérifier le password
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Vérifier que le compte est actif
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Générer tokens JWT
    access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["email"], "user_id": user["id"]})
    
    # Set httpOnly cookies
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=3600,  # 1h
    )
    response.set_cookie(
        key=f"{COOKIE_NAME}_refresh",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=7 * 24 * 3600,  # 7 jours
    )
    
    return AuthResponse(
        message="Login successful",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[dict, Depends(get_current_user)]):
    """Retourne les informations de l'utilisateur connecté.
    
    Args:
        current_user: User injecté par le middleware get_current_user
    
    Returns:
        UserResponse avec données du user
    
    Raises:
        HTTPException 401: Token invalide ou expiré
        HTTPException 403: Compte désactivé
    
    Example:
        GET /auth/me
        Cookie: skapa_access_token=...
        
        Response 200:
        {"id": 1, "email": "alice@example.com", "is_active": true, "created_at": "..."}
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        is_active=bool(current_user["is_active"]),
        created_at=current_user["created_at"],
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(None, alias=f"{COOKIE_NAME}_refresh"),
):
    """Renouvelle l'access token avec le refresh token.
    
    Args:
        response: FastAPI Response pour set nouveau access token
        refresh_token: Refresh token depuis httpOnly cookie
    
    Returns:
        AuthResponse avec user
    
    Raises:
        HTTPException 401: Refresh token invalide ou expiré
        HTTPException 403: Compte désactivé
    
    Example:
        POST /auth/refresh
        Cookie: skapa_access_token_refresh=...
        
        Response 200:
        {"message": "Token refreshed", "user": {...}}
        Set-Cookie: skapa_access_token=...; HttpOnly; SameSite=lax
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    
    # Extraire user depuis refresh token
    user_data = extract_user_from_token(refresh_token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Récupérer le user depuis la DB
    user = get_user_by_id(user_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Vérifier que le compte est actif
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    
    # Générer nouveau access token
    new_access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
    
    # Set nouveau access token dans cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        max_age=3600,  # 1h
    )
    
    return AuthResponse(
        message="Token refreshed successfully",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        ),
    )


@router.post("/logout")
async def logout(response: Response):
    """Déconnecte l'utilisateur en supprimant les cookies.
    
    Args:
        response: FastAPI Response pour delete cookies
    
    Returns:
        Message de confirmation
    
    Example:
        POST /auth/logout
        
        Response 200:
        {"message": "Logged out successfully"}
        Set-Cookie: skapa_access_token=; Max-Age=0
    """
    # Supprimer les cookies en les expirant
    response.delete_cookie(key=COOKIE_NAME, domain=COOKIE_DOMAIN)
    response.delete_cookie(key=f"{COOKIE_NAME}_refresh", domain=COOKIE_DOMAIN)
    
    return {"message": "Logged out successfully"}
