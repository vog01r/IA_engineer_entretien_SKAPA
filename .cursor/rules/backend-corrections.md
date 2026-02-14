---
description: Corrections backend à effectuer
globs:
  - "app/**/*.py"
  - ".gitignore"
  - ".env*"
---

# Corrections backend

Liste des problèmes identifiés pendant l'analyse du code (QCM partie 2).

## Sécurité

### .gitignore mal configuré
- `.env` commenté ligne 1 → sera versionné
- `.venv/`, `venv/`, `env/` commentés → seront versionnés
- Manque `*.db`, `database.db`

**Fix :**
Décommenter tout ça, ajouter les db.

### CORS ouvert (app/app.py)
```python
allow_origins=["*"]  # Trop permissif
```

**Fix :**
Variable d'environnement avec liste de domaines autorisés.

### DEBUG hardcodé (config.py)
```python
DEBUG = True  # Ignore .env, dangereux en prod
```

**Fix :**
Lire depuis env avec défaut False.

### Incohérence BDD
Trois chemins différents :
- .env : `database.db`
- config.py : `weather.db`
- crud.py : `"database.db"` hardcodé

**Fix :**
Unifier, une seule source de vérité.

## Bugs fonctionnels

### Agent IA (app/agent/agent.py)

**Fichier actuellement vide avec commentaires trompeurs.**

Problèmes à corriger lors de l'implémentation :
- Contexte RAG récupéré mais pas injecté dans le prompt
- System prompt trop vague (pas d'instructions sur utilisation contexte)
- Température 0.7 trop haute pour Q&A factuel (mettre 0.1)
- Pas de try/except

### Connexions DB (crud.py)

Pattern actuel :
```python
conn = _get_conn()
c.execute(...)
conn.close()
```

Problème : si exception avant close(), fuite de connexion.

**Fix :**
```python
with sqlite3.connect(DATABASE_PATH) as conn:
    c.execute(...)
```

### Recherche inefficace (crud.py)

`search_chunks` utilise `LIKE '%query%'` → recherche lexicale pure.
Pas de recherche sémantique.

Pour ce test, documenter la limitation.
En prod : migration vers embeddings + base vectorielle.

### Validation API (weather.py)

Latitude/longitude non validées, `9999` accepté.

**Fix :**
Pydantic validators avec Field(ge=-90, le=90).

## Ordre recommandé

1. Sécurité (gitignore, env, CORS, DEBUG)
2. Agent IA 
3. DB (context managers)
4. Validation API

Un commit par correction.
