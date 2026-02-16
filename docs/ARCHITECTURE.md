# Architecture SKAPA - Structure Modulaire

**Date** : Février 2026  
**Version** : 2.0.0 (après refactoring)

---

## 📁 Structure du projet

```
.
├── backend/                    # Backend FastAPI (nouveau)
│   ├── web/                   # API web (JWT auth)
│   │   ├── auth/             # Module authentification
│   │   │   ├── security.py   # JWT + password hashing
│   │   │   ├── dependencies.py  # Middleware get_current_user
│   │   │   └── endpoints.py  # Routes /auth/*
│   │   ├── weather/          # Module météo
│   │   └── agent/            # Module agent IA
│   │
│   ├── services/             # Services externes (API Key auth)
│   │   ├── bot/             # Bot Telegram
│   │   └── mcp/             # MCP server
│   │
│   ├── shared/              # Code partagé
│   │   ├── config/         # Configuration (env vars)
│   │   ├── db/             # Database SQLite
│   │   └── models/         # Pydantic models
│   │
│   └── main.py             # Entry point FastAPI
│
├── frontend/               # Frontend React (inchangé)
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/      # LoginForm, RegisterForm
│   │   │   └── ProtectedRoute.jsx
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   └── services/
│   │       └── api.js
│   └── package.json
│
├── infra/                  # Infrastructure (nouveau)
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   └── docker-compose.yml
│   └── railway/
│       └── railway.toml
│
├── docs/                   # Documentation
│   ├── JWT_IMPLEMENTATION.md  # Doc complète JWT
│   └── AUTH.md            # (ancien, à supprimer)
│
├── data/                  # Database SQLite
│   └── skapa.db
│
├── app/                   # (ancien, à supprimer après migration)
│
├── requirements.txt       # Dependencies Python
├── .env.example          # Template env vars
└── README.md             # Ce fichier
```

---

## 🎯 Séparation des responsabilités

### 1. Backend Web (`backend/web/`)

**Authentification** : JWT avec httpOnly cookies  
**Utilisateurs** : Utilisateurs web (navigateur)  
**Routes** :
- `/auth/register` - Création de compte
- `/auth/login` - Authentification
- `/auth/me` - Profil utilisateur
- `/auth/refresh` - Renouvellement token
- `/auth/logout` - Déconnexion
- `/weather/*` - Endpoints météo (protégés JWT)
- `/agent/*` - Endpoints agent IA (protégés JWT)

### 2. Services Externes (`backend/services/`)

**Authentification** : API Key (X-API-Key header)  
**Utilisateurs** : Bot Telegram, MCP Server  
**Routes** : Appels directs via API Key (backward compatible)

### 3. Code Partagé (`backend/shared/`)

**Config** : Variables d'environnement  
**Database** : CRUD SQLite (users, weather, conversations)  
**Models** : Pydantic models réutilisables

### 4. Frontend (`frontend/`)

**Framework** : React + Vite  
**Authentification** : JWT httpOnly cookies  
**State** : AuthContext (React Context API)

### 5. Infrastructure (`infra/`)

**Docker** : Dockerfiles + docker-compose  
**Railway** : Configuration déploiement prod

---

## 🚀 Démarrage rapide

### Développement local

**Backend :**
```bash
# Installer dependencies
pip install -r requirements.txt

# Lancer le serveur
python -m uvicorn backend.main:app --reload --port 8000
```

**Frontend :**
```bash
cd frontend
npm install
npm run dev
```

**Avec Docker Compose :**
```bash
cd infra/docker
docker-compose up --build
```

Accès :
- Backend : http://localhost:8000
- Frontend : http://localhost:5173
- Docs API : http://localhost:8000/docs

---

## 📝 Variables d'environnement

Copier `.env.example` vers `.env` et remplir :

```bash
# JWT Settings
JWT_SECRET=your_jwt_secret_here_256_bits
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Cookie Settings
COOKIE_NAME=skapa_access_token
COOKIE_SECURE=false  # true en production (HTTPS)
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=

# API Key (services externes)
API_KEY=your_api_key_here_256_bits

# Database
DATABASE_URL=sqlite:///./data/skapa.db

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

---

## 📚 Documentation

- **[JWT_IMPLEMENTATION.md](docs/JWT_IMPLEMENTATION.md)** : Documentation complète de l'authentification JWT
  - Architecture détaillée
  - Justifications techniques bloc par bloc
  - Analyse sécurité/performance
  - Tests & validation

- **[infra/README.md](infra/README.md)** : Guide infrastructure & déploiement

---

## 🔄 Migration depuis l'ancienne structure

### Changements principaux

1. **`app/` → `backend/`** : Nouvelle structure modulaire
2. **`app/core/` → `backend/web/auth/`** : Module auth dédié
3. **`app/api/v1/endpoints/` → `backend/web/*/`** : Endpoints par module
4. **`app/bot/` → `backend/services/bot/`** : Services externes séparés
5. **`app/config.py` → `backend/shared/config/`** : Config partagée
6. **`Dockerfile` → `infra/docker/`** : Infrastructure séparée

### Imports à mettre à jour

**Avant :**
```python
from app.config import JWT_SECRET
from app.core.security import hash_password
from app.db.crud import get_user_by_id
```

**Après :**
```python
from backend.shared.config import JWT_SECRET
from backend.web.auth.security import hash_password
from backend.shared.db import get_user_by_id
```

---

## ✅ Avantages de la nouvelle structure

1. ✅ **Clarté** : Séparation claire front/back/services/infra
2. ✅ **Maintenabilité** : Modifications localisées par module
3. ✅ **Testabilité** : Tests unitaires par module
4. ✅ **Évolutivité** : Facile d'ajouter de nouveaux modules
5. ✅ **Documentation** : Structure auto-documentée

---

## 🔗 Liens utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Security](https://owasp.org/)

---

**Auteur** : Benjamin Chabanis  
**Contact** : chabanisb@icloud.com  
**Repository** : https://github.com/vog01r/IA_engineer_entretien_SKAPA
