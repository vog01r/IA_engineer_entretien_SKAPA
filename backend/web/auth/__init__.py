"""Module d'authentification JWT.

Exports :
- security : hash_password, verify_password, create_access_token, decode_token
- dependencies : get_current_user, get_current_user_optional
- endpoints : Auth router (/register, /login, /me, /refresh, /logout)
"""

from .dependencies import get_current_user, get_current_user_optional
from .security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    extract_user_from_token,
    hash_password,
    verify_password,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "extract_user_from_token",
    "get_current_user",
    "get_current_user_optional",
]
