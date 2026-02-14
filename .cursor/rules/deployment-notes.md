---
description: Notes pour le déploiement
globs:
  - "railway.json"
  - "Procfile"
---

# Déploiement

**Plateforme : Railway**

Choix justifié par :
- Setup simple
- Free tier OK pour démo
- Support Python natif
- Variables env faciles

## Config

**railway.json :**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.app:app --host 0.0.0.0 --port $PORT"
  }
}
```

**Variables env à configurer :**
```
API_KEY=...
DEBUG=false
ALLOWED_ORIGINS=https://app.up.railway.app
DATABASE_URL=sqlite:////data/database.db
```

**Base de données :**
Ajouter volume persistant Railway monté sur `/data` pour que la DB survive aux redéploiements.

## Frontend

**Option retenue : servi par FastAPI**

Compiler frontend :
```bash
cd frontend && npm run build
```

Servir depuis FastAPI :
```python
app.mount("/", StaticFiles(directory="frontend/dist", html=True))
```

Plus simple qu'un déploiement séparé pour ce test.

## Checklist avant push

- [ ] .env dans .gitignore
- [ ] requirements.txt à jour
- [ ] Frontend compilé
- [ ] Variables env configurées Railway
- [ ] Volume persistant créé
- [ ] CORS configuré avec domaine prod

## Tests post-déploiement

- GET `/` → frontend
- GET `/docs` → Swagger
- POST `/weather/fetch` → fonctionne
- POST `/agent/ask` → fonctionne

URLs à noter pour la PR.
