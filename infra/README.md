# Infrastructure SKAPA

Configuration Docker et déploiement.

## Structure

```
infra/
├── docker/
│   ├── Dockerfile.backend      # Image backend FastAPI
│   ├── Dockerfile.frontend     # Image frontend React
│   └── docker-compose.yml      # Orchestration locale
└── railway/
    └── railway.toml            # Config Railway (prod)
```

## Développement local

### Avec Docker Compose

```bash
cd infra/docker
docker-compose up --build
```

Accès :
- Backend API : http://localhost:8000
- Frontend : http://localhost:5173
- Docs API : http://localhost:8000/docs

### Sans Docker

**Backend :**
```bash
cd ../..  # Retour à la racine
python -m uvicorn backend.main:app --reload --port 8000
```

**Frontend :**
```bash
cd frontend
npm run dev
```

## Déploiement Railway

1. **Backend** : Déployé depuis `infra/docker/Dockerfile.backend`
2. **Frontend** : Déployé depuis `infra/docker/Dockerfile.frontend`

Variables d'environnement requises :
- `JWT_SECRET` : Secret pour signer les tokens JWT (256 bits)
- `API_KEY` : Clé API pour services externes (bot, MCP)
- `COOKIE_SECURE` : `true` en production (HTTPS)
- `DATABASE_URL` : Path vers SQLite (ou PostgreSQL en prod)

## Architecture

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│   Port 5173 │
└──────┬──────┘
       │ HTTP + JWT cookies
       ▼
┌─────────────┐
│   Backend   │ (FastAPI + SQLite)
│   Port 8000 │
└─────────────┘
       │
       ├─► /auth/*     (JWT auth)
       ├─► /weather/*  (JWT protected)
       └─► /agent/*    (JWT protected)
```

## Sécurité

- **JWT** : httpOnly cookies (protection XSS)
- **CORS** : Configuré pour frontend uniquement
- **HTTPS** : Requis en production (COOKIE_SECURE=true)
- **Rate limiting** : 100 req/min par IP (slowapi)
