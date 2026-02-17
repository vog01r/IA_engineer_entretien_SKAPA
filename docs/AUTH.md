# Authentification SKAPA

## Vue d'ensemble

SKAPA utilise un système dual-auth :

| Client | Méthode | Transport |
|---|---|---|
| Frontend React | JWT (access + refresh tokens) | httpOnly cookies |
| Bot Telegram | API Key | Header `X-API-Key` |
| MCP Server | API Key | Header `X-API-Key` |

---

## JWT (Frontend web)

### Pourquoi JWT et pas sessions serveur ?

- **Stateless** : pas de stockage côté serveur, scalable horizontalement
- **Dual token** : access court (1h) + refresh long (7j) → UX fluide sans re-login constant
- **HS256** : symétrique, simple, suffisant pour ce scope (secret partagé, un seul service)

### Pourquoi httpOnly cookies et pas localStorage ?

localStorage est accessible via `document.cookie` → vulnérable XSS.
httpOnly cookies ne sont jamais accessibles en JavaScript → XSS ne peut pas voler le token.

### Flux d'authentification

```
POST /auth/login  {email, password}
    → verify bcrypt hash
    → create access_token (1h) + refresh_token (7j)
    → Set-Cookie: skapa_access_token=...; HttpOnly; SameSite=lax; Secure
    → Set-Cookie: skapa_access_token_refresh=...; HttpOnly; SameSite=lax; Secure

GET /weather/ (requête authentifiée)
    → Cookie: skapa_access_token=<jwt>
    → decode + verify signature (JWT_SECRET, HS256)
    → verify expiration
    → inject user dict dans le handler

POST /auth/refresh
    → Cookie: skapa_access_token_refresh=<jwt>
    → verify refresh token
    → issue new access_token
    → Set-Cookie: skapa_access_token=...; HttpOnly
```

### Configuration cookies

| Attribut | Valeur dev | Valeur prod | Rôle |
|---|---|---|---|
| `HttpOnly` | `true` | `true` | Bloque accès JS (XSS) |
| `Secure` | `false` | `true` | HTTPS uniquement |
| `SameSite` | `lax` | `lax` | Protection CSRF basique |
| `Max-Age` | access: 3600 | access: 3600 | Expiration automatique |

`SameSite=lax` : bloque les requêtes cross-site initiées par des formulaires tiers (CSRF), tout en autorisant les navigations normales (redirections OAuth, liens).

### Endpoints auth

| Route | Auth requise | Rate limit | Description |
|---|---|---|---|
| `POST /auth/register` | Non | 10/min | Création compte |
| `POST /auth/login` | Non | 10/min | Connexion |
| `GET /auth/me` | JWT | — | Profil utilisateur |
| `POST /auth/refresh` | Refresh cookie | — | Renouveler access token |
| `POST /auth/logout` | Non | — | Supprime les cookies |

---

## API Key (Bot / MCP)

### Pourquoi API Key et pas JWT pour les services ?

Les services (bot, MCP) sont des processus backend, pas des utilisateurs humains :
- Pas de notion de session ou d'expiration pertinente
- Pas de UI pour gérer un refresh
- API Key simple, partagée en variable d'environnement, révocable instantanément

### Transmission

```
GET /weather/fetch?latitude=48.85&longitude=2.35
X-API-Key: <valeur de API_KEY dans .env>
```

### Sécurité comparaison

La comparaison utilise `secrets.compare_digest()` (stdlib Python) pour éviter les timing attacks.
`==` sur str Python s'arrête au premier caractère différent → un attaquant peut mesurer les délais pour reconstituer la clé.

---

## Rate limiting

Implémenté avec `slowapi` (wrapper FastAPI de `limits`).

| Route | Limite | Justification |
|---|---|---|
| `POST /auth/login` | 10/min par IP | Brute-force protection |
| `POST /auth/register` | 10/min par IP | Spam comptes |
| `POST /agent/ask` | 30/min par IP | Coût appel LLM (OpenAI) |

Réponse en cas de dépassement : `HTTP 429 Too Many Requests`.

---

## Variables d'environnement requises

```bash
# JWT — générer avec : openssl rand -hex 64
JWT_SECRET=<secret_long_et_aleatoire>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Cookies
COOKIE_SECURE=false   # false en dev (HTTP), true en prod (HTTPS)
COOKIE_SAMESITE=lax

# API Key pour services (bot, MCP)
API_KEY=<cle_aleatoire>
```

---

## Code source

- `backend/web/auth/security.py` — JWT creation/decode, bcrypt
- `backend/web/auth/endpoints.py` — routes register/login/refresh/logout
- `backend/web/auth/dependencies.py` — `get_current_user` (dual-auth injectable)
- `backend/shared/config/config.py` — variables d'environnement
