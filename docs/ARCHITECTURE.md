# 🏗️ Architecture SKAPA - Documentation Technique

**Date:** 2026-02-17  
**Auteur:** Benjamin Chabanis  
**Version:** 2.0 (restructuré)

---

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    SKAPA Application                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │ Telegram │  │   MCP    │  │  Claude  │  │
│  │  (React) │  │   Bot    │  │  Server  │  │ Desktop  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │              │         │
│       └─────────────┴──────────────┴──────────────┘         │
│                         │                                   │
│                    ┌────▼────┐                              │
│                    │ Backend │                              │
│                    │ FastAPI │                              │
│                    └────┬────┘                              │
│                         │                                   │
│              ┌──────────┼──────────┐                        │
│              │          │          │                        │
│         ┌────▼───┐ ┌───▼────┐ ┌──▼─────┐                  │
│         │ SQLite │ │ OpenAI │ │  Open  │                  │
│         │   DB   │ │  API   │ │ Meteo  │                  │
│         └────────┘ └────────┘ └────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Structure du projet

### Organisation actuelle (après restructuration)

```
IA_engineer_entretien_SKAPA/
├── backend/                    # Backend FastAPI (API + Services)
│   ├── main.py                 # Entry point FastAPI
│   ├── web/                    # API Web (JWT auth)
│   │   ├── auth/               # Authentification utilisateurs
│   │   ├── agent/              # Endpoints agent IA
│   │   └── weather/            # Endpoints météo
│   ├── services/               # Services externes (API Key auth)
│   │   ├── bot/                # Bot Telegram
│   │   │   └── telegram_bot.py
│   │   └── mcp/                # Serveur MCP
│   │       ├── server.py       # Définition tools MCP
│   │       └── run_http.py     # Entry point HTTP
│   └── shared/                 # Code partagé
│       ├── config/             # Configuration
│       ├── db/                 # Database (CRUD)
│       ├── models/             # Modèles Pydantic
│       └── cache.py            # Cache intelligent
│
├── frontend/                   # Frontend React + Vite
│   ├── src/
│   │   ├── components/         # Composants React
│   │   ├── pages/              # Pages
│   │   ├── services/           # API calls
│   │   └── App.tsx             # Entry point
│   ├── public/
│   └── package.json
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Ce fichier
│   └── MCP_SETUP.md            # Configuration MCP
│
├── scripts/                    # Scripts utilitaires
│   ├── test_bot_performance.py
│   ├── test_mcp_compliance.py
│   └── ingest_knowledge.py
│
├── infra/                      # Infrastructure & déploiement
│   ├── README.md               # Guide déploiement
│   └── railway.json            # Config Railway
│
├── data/                       # Données (knowledge base)
│   └── knowledge/
│
├── .env                        # Variables d'environnement (local)
├── .env.example                # Template variables
├── requirements.txt            # Dépendances Python
├── Procfile                    # Déploiement Railway
└── README.md                   # Documentation principale
```

---

## 🎯 Séparation des responsabilités

### 1. Backend (`backend/`)

**Rôle :** API centrale, logique métier, accès données.

#### 1.1 Web (`backend/web/`)
- **Auth** : Authentification JWT, gestion utilisateurs
- **Agent** : Endpoints pour l'agent IA (RAG, LLM)
- **Weather** : Endpoints météo (fetch, location, range)

**Authentification :** JWT (httpOnly cookies)  
**Usage :** Frontend React, applications web

#### 1.2 Services (`backend/services/`)
- **Bot Telegram** : Interface conversationnelle Telegram
- **MCP Server** : Tools MCP pour Claude Desktop/ChatGPT

**Authentification :** API Key (header `X-API-Key`)  
**Usage :** Services externes, bots, MCP

#### 1.3 Shared (`backend/shared/`)
- **Config** : Variables d'environnement, CORS, constantes
- **DB** : CRUD SQLite (weather, conversations, knowledge, alerts)
- **Models** : Modèles Pydantic (validation, serialization)
- **Cache** : Cache intelligent avec TTL (performance)

**Principe :** Code réutilisable entre web et services.

---

### 2. Frontend (`frontend/`)

**Rôle :** Interface utilisateur web (React + Vite + Tailwind).

**Features :**
- Dashboard météo (visualisation données)
- Chat agent IA (interface conversationnelle)
- Gestion alertes (configuration seuils)
- Historique conversations

**Authentification :** JWT (httpOnly cookies)  
**API :** Appels vers `backend/web/`

---

### 3. MCP Server (`backend/services/mcp/`)

**Rôle :** Exposer tools météo + knowledge base à Claude Desktop/ChatGPT (4 tools : get_weather, search_knowledge, conversation_history, get_weather_stats).

**Transports :** stdio (Claude Desktop) · streamable-http (Railway). **Config, tests et conformité :** voir **[\`docs/MCP_SETUP.md\`](MCP_SETUP.md)**.

---

### 4. Bot Telegram (`backend/services/bot/`)

**Rôle :** Interface conversationnelle Telegram (météo + alertes).

**Features :**
- Conversation naturelle (agent IA)
- Commandes `/meteo`, `/alertes`, `/help`
- Alertes personnalisées (canicule, froid)
- Vérification périodique (toutes les heures)

**Architecture :**
```
User → Bot → Agent API → LLM (OpenAI/Claude)
                ↓
         Weather API → Open-Meteo
                ↓
            SQLite DB
```

**Performance :**
- Cache géocodage (24h)
- Cache météo (10min)
- Timing instrumentation (logs)

---

### 5. Documentation (`docs/`)

**Rôle :** Documentation technique pour développeurs et recruteurs.

**Fichiers :**
- `ARCHITECTURE.md` : Ce fichier (vue d'ensemble)
- `MCP_SETUP.md` : Configuration MCP (Claude Desktop, HTTP, ChatGPT)

**Performance bot :** cache TTL dans `backend/shared/cache.py`, instrumentation dans le bot et l’agent ; script `scripts/test_bot_performance.py`.

---

### 6. Infrastructure (`infra/`)

**Rôle :** Déploiement, CI/CD, monitoring.

**Déploiement Railway :**
- Service 1 : Backend API (FastAPI)
- Service 2 : Frontend (React static)
- Service 3 : MCP Server (HTTP)

**Variables d'environnement :**
- `OPENAI_API_KEY` : Clé OpenAI
- `TELEGRAM_BOT_TOKEN` : Token bot Telegram
- `JWT_SECRET` : Secret JWT
- `API_KEY` : Clé API services
- `DATABASE_URL` : URL base de données

---

## 🔐 Sécurité

### Authentification

| Client | Méthode | Usage |
|--------|---------|-------|
| Frontend | JWT (httpOnly cookies) | Utilisateurs web |
| Bot Telegram | API Key (header) | Service externe |
| MCP Server | API Key (header) | Service externe |

Détails implémentation JWT (cookies, refresh, scopes) : voir **NOTES.md** section 28 (Authentification JWT) et code `backend/web/auth/`.

### Secrets

**❌ JAMAIS commiter :**
- `.env` (secrets réels)
- `database.db` (données réelles)
- Clés API hardcodées

**✅ TOUJOURS commiter :**
- `.env.example` (placeholders)
- Code source (sans secrets)

### CORS

**Production :**
```python
ALLOWED_ORIGINS = [
    "https://skapa-frontend.railway.app",
    "https://skapa.com"
]
```

**Développement :**
```python
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000"   # Alternative
]
```

---

## 📊 Flux de données

### 1. Requête météo (Frontend)

```
User (Frontend)
    ↓ GET /weather/fetch?lat=48.85&lon=2.35
Backend API (JWT auth)
    ↓ Vérifier cache (10min TTL)
    ├─ Cache HIT → Return cached data
    └─ Cache MISS → Fetch Open-Meteo
                    ↓ Store in SQLite
                    ↓ Store in cache
                    ↓ Return data
```

### 2. Conversation agent (Telegram Bot)

```
User (Telegram)
    ↓ "Météo à Paris"
Bot Telegram
    ↓ POST /agent/ask (API Key auth)
Backend Agent
    ↓ Parse intention (LLM)
    ├─ Géocodage "Paris" → (48.85, 2.35)
    ├─ Fetch météo → Open-Meteo
    ├─ RAG search → Knowledge base
    └─ Generate answer → LLM (OpenAI/Claude)
        ↓ Store conversation
        ↓ Return answer
Bot Telegram
    ↓ Send message to user
```

### 3. MCP Tool call (Claude Desktop)

```
Claude Desktop
    ↓ tools/call (get_weather)
MCP Server (stdio)
    ↓ Validate params (Pydantic)
    ↓ Fetch Open-Meteo
    ↓ Format response (WeatherResponse)
    ↓ Return JSON-RPC 2.0
Claude Desktop
    ↓ Display to user
```

---

## 🚀 Déploiement

### Local (développement)

```bash
# Backend
cd backend
source ../.venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev  # Port 5173

# Bot Telegram
python -m app.bot.telegram_bot

# MCP Server (stdio)
python3 -m backend.services.mcp.server
```

### Railway (production)

**Services :**
1. **Backend API** : `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
2. **Frontend** : Static site (Vite build)
3. **MCP Server** : `python backend/services/mcp/run_http.py`

**Variables Railway :**
- Définies dans Railway Dashboard
- Pas de `.env` commité
- Secrets rotatés régulièrement

---

## 📈 Performance

### Bottlenecks identifiés

1. **Agent LLM** : 1-5s (70-90% du temps total)
2. **Weather API** : 0.5-1.5s
3. **Géocodage** : 0.2-0.5s

### Optimisations implémentées

1. **Cache intelligent** :
   - Géocodage : 24h TTL
   - Météo : 10min TTL
   - Hit rate attendu : 60-80%

2. **Timing instrumentation** :
   - Logs granulaires (⏱️ [OPERATION] took X.XXs)
   - Identification bottlenecks réels

3. **Async/await** :
   - `asyncio.to_thread()` pour appels bloquants
   - Non-blocking I/O

### Métriques cibles

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps réponse bot | 4-6s | 2-3s | -40 à -50% |
| Cache hit rate | 0% | 60-80% | N/A |
| Temps perçu (UX) | 4-6s | <2s | -60 à -70% |

---

## 🧪 Tests

**Scripts :** `scripts/test_bot_performance.py`, `scripts/test_mcp_compliance.py`, `scripts/test_mcp_e2e.py`, `scripts/ingest_knowledge.py`. **Commandes détaillées :** voir [QUICKSTART.md](../QUICKSTART.md) et [MCP_SETUP.md](MCP_SETUP.md).

---

## 🎓 Choix techniques justifiés

### Pourquoi FastAPI ?
- **Async natif** : Performance I/O-bound
- **Pydantic** : Validation automatique
- **OpenAPI** : Documentation auto-générée
- **Type hints** : Meilleure maintenabilité

### Pourquoi SQLite ?
- **Simplicité** : Pas de serveur externe
- **Performance** : Suffisant pour le cas d'usage
- **Portabilité** : Un seul fichier
- **Trade-off** : Pas de scaling horizontal (acceptable pour MVP)

### Pourquoi FastMCP ?
- **SDK officiel** : Conforme par design
- **Simplicité** : Moins verbeux que SDK bas niveau
- **Type safety** : Pydantic + type hints
- **Trade-off** : Moins de contrôle (acceptable)

### Pourquoi React + Vite ?
- **Performance** : Vite HMR ultra-rapide
- **Écosystème** : Composants réutilisables
- **Type safety** : TypeScript
- **Trade-off** : Complexité (acceptable pour UI riche)

---

## 🔮 Évolutions futures

### Court terme (1-2 semaines)
- [ ] Tests unitaires (pytest)
- [ ] CI/CD (GitHub Actions)
- [ ] Monitoring (Sentry, Datadog)
- [ ] Rate limiting (slowapi)

### Moyen terme (1-2 mois)
- [ ] PostgreSQL (remplacer SQLite)
- [ ] Redis cache (remplacer cache mémoire)
- [ ] Streaming LLM (meilleure UX)
- [ ] Webhooks Telegram (remplacer polling)

### Long terme (3-6 mois)
- [ ] Multi-tenancy (plusieurs utilisateurs)
- [ ] API versioning (v2)
- [ ] Microservices (si scaling nécessaire)
- [ ] Kubernetes (si scaling horizontal)

---

## 📚 Références

- [FastAPI](https://fastapi.tiangolo.com/)
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [Railway Docs](https://docs.railway.app/)

---

**Dernière mise à jour :** 2026-02-17  
**Auteur :** Benjamin Chabanis  
**Contact :** [GitHub](https://github.com/chabanis)
