"""
Security utilities for JWT authentication and password hashing.

Ce module fournit les fonctions cryptographiques pour :
- Génération et vérification de tokens JWT (access + refresh)
- Hashing et vérification de passwords avec bcrypt
- Extraction de données depuis les tokens

Justifications techniques :
- JWT HS256 : Symétrique, simple, suffisant pour ce scope (secret partagé)
- Bcrypt cost=12 : ~250ms par hash, résistant brute-force (2^12 iterations)
- Tokens courts (1h) : Limite fenêtre d'exploitation si volé
- Refresh tokens (7j) : UX fluide sans re-login constant
"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from backend.shared.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET,
)

# Context bcrypt pour hashing passwords
# rounds=12 (cost factor) = ~250ms par hash sur CPU moderne
# Auto-salt : bcrypt génère un salt aléatoire pour chaque hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# ──────────────── Password Hashing ────────────────


def hash_password(password: str) -> str:
    """Hash un password avec bcrypt.
    
    Args:
        password: Password en clair
    
    Returns:
        Hash bcrypt (60 caractères, inclut salt + cost + hash)
    
    Example:
        >>> hash_password("MySecureP@ss123")
        '$2b$12$...'  # 60 chars
    
    Sécurité :
        - Salt automatique (unique par hash)
        - Cost factor 12 = 2^12 iterations (~250ms)
        - Résistant rainbow tables et brute-force
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un password contre son hash bcrypt.
    
    Args:
        plain_password: Password en clair fourni par l'utilisateur
        hashed_password: Hash bcrypt stocké en base
    
    Returns:
        True si le password correspond, False sinon
    
    Example:
        >>> hashed = hash_password("MySecureP@ss123")
        >>> verify_password("MySecureP@ss123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    
    Performance :
        - ~250ms par vérification (cost factor 12)
        - Acceptable pour login (1 vérif par requête)
        - Pas de cache possible (salt unique)
    """
    return pwd_context.verify(plain_password, hashed_password)


# ──────────────── JWT Tokens ────────────────


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crée un JWT access token.
    
    Args:
        data: Payload à encoder (ex: {"sub": "user@example.com", "user_id": 42})
        expires_delta: Durée de validité custom (défaut: JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    Returns:
        Token JWT signé (string)
    
    Example:
        >>> token = create_access_token({"sub": "alice@example.com", "user_id": 1})
        >>> # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    
    Payload JWT :
        - sub : Subject (email de l'utilisateur)
        - user_id : ID de l'utilisateur (pour éviter query DB)
        - exp : Expiration timestamp (UTC)
        - iat : Issued at timestamp (UTC)
    
    Sécurité :
        - Signé avec JWT_SECRET (HS256)
        - Expiration courte (1h par défaut)
        - Pas de données sensibles dans le payload (visible en base64)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Crée un JWT refresh token (long-lived).
    
    Args:
        data: Payload à encoder (ex: {"sub": "user@example.com", "user_id": 42})
    
    Returns:
        Token JWT signé (string)
    
    Usage :
        - Stocké côté client (httpOnly cookie ou localStorage)
        - Utilisé pour obtenir un nouveau access token sans re-login
        - Durée de vie longue (7 jours par défaut)
    
    Sécurité :
        - Même signature que access token (HS256)
        - Expiration longue (7j) pour UX fluide
        - Peut être révoqué via blacklist en base (optionnel)
    """
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Décode et vérifie un JWT token.
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        Payload décodé (dict)
    
    Raises:
        jwt.ExpiredSignatureError: Token expiré
        jwt.InvalidTokenError: Token invalide (signature, format, etc.)
    
    Example:
        >>> token = create_access_token({"sub": "alice@example.com", "user_id": 1})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'alice@example.com'
        >>> payload["user_id"]
        1
    
    Sécurité :
        - Vérifie la signature (JWT_SECRET)
        - Vérifie l'expiration automatiquement
        - Lève exception si invalide (géré par middleware)
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload


def extract_user_from_token(token: str) -> dict | None:
    """Extrait les données utilisateur depuis un token JWT.
    
    Args:
        token: Token JWT
    
    Returns:
        Dict avec {"email": str, "user_id": int} ou None si invalide
    
    Example:
        >>> token = create_access_token({"sub": "alice@example.com", "user_id": 1})
        >>> extract_user_from_token(token)
        {'email': 'alice@example.com', 'user_id': 1}
    
    Usage :
        - Utilisé par le middleware get_current_user
        - Retourne None au lieu de lever exception (gestion d'erreur au niveau supérieur)
    """
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            return None
        return {"email": email, "user_id": user_id}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
