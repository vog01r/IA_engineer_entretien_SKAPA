# Test AI Agent Engineer — SKAPA

**Objectif :** corriger le code existant, compléter l'agent IA, développer un frontend, implémenter un serveur MCP et un bot Telegram (données météo, base, API, frontend, MCP connectable à ChatGPT ou Claude). Le MCP doit exposer **au moins 3 tools** permettant d'interroger la base (via l'API) pour obtenir des **informations météo en temps réel pour n'importe quel lieu**.

**Stack :** Python · FastAPI · SQLite · LLM API (Claude ou OpenAI) · MCP · Telegram Bot API

**Rendus :** tout se fait sur Git par **une Pull Request vers la branche `main`** du repository. La PR doit contenir :

- **Le QCM** : fichier `INSTRUCTIONS_QCM.md` complété (réponses, justifications, variante 3.3 et 3.8).
- **La méthodologie** : décrite dans la PR ou dans `INSTRUCTIONS_QCM.md`.
- **L'URL de l'application**
- **L'URL du frontend**
- **L'URL de l'API**
- **L'URL du MCP**
- **Agent "Alertes Intelligentes"**

Aucun rendu par zip ni par email : document rempli + code complété + liens fournis dans la même Pull Request vers `main`.


## Agent "Alertes Intelligentes" — Bot Telegram Météo Mondial

### Concept

Un agent IA conversationnel connecté à **Telegram** qui permet de discuter de la météo **partout dans le monde** en temps réel. L'agent s'appuie sur l'API météo (Open-Meteo) et la base SQLite déjà en place dans ce projet.

### Fonctionnalités

- **Conversation naturelle** : l'utilisateur écrit un message du type *"Quel temps fait-il à Tokyo ?"* ou *"Prévisions pour New York demain"* et l'agent répond en langage naturel.
- **Alertes personnalisées** : l'utilisateur configure des seuils (*"Préviens-moi si la température descend sous 0°C à Paris"*, *"Alerte si > 35°C à Marseille"*). L'agent surveille en continu et envoie une notification Telegram dès qu'un seuil est franchi.
- **Historique et tendances** : l'agent interroge la base SQLite pour afficher l'évolution des températures sur une période donnée (*"Montre-moi la tendance sur 7 jours à Lyon"*).

### Architecture prévue

```
Utilisateur Telegram
        │
        ▼
  Bot Telegram (python-telegram-bot)
        │
        ▼
  Agent IA (LLM — parsing intention + génération réponse)
        │
        ├──► API FastAPI existante (/weather/fetch, /weather/location, /weather/range)
        │
        ├──► Open-Meteo Geocoding API (nom de ville → lat/lon)
        │
        └──► Base SQLite (historique, alertes utilisateurs, préférences)
```

### Stack technique

| Composant | Technologie |
|---|---|
| Bot Telegram | `python-telegram-bot` |
| API météo | Open-Meteo (déjà intégré) |
| Géocodage | Open-Meteo Geocoding API |
| Base de données | SQLite (déjà en place) |
| Scheduler alertes | `APScheduler` (vérification périodique des seuils) |
| Agent IA | LLM via MCP ou appel API (Claude, OpenAI) |
| Déploiement | Docker (un conteneur API + un conteneur bot) |

### Exemples d'interactions

```
👤 Utilisateur : "Météo à Barcelone ?"
🤖 Agent : "Actuellement à Barcelone : 18°C, ciel dégagé.
            Prévisions : 20°C demain, 16°C mercredi.
            Veux-tu que je crée une alerte pour cette ville ?"

👤 Utilisateur : "Oui, préviens-moi si ça descend sous 10°C"
🤖 Agent : "Alerte créée : je te préviendrai dès que la
            température à Barcelone passe sous 10°C."

👤 Utilisateur : "Comparaison Paris vs Toulouse cette semaine ?"
🤖 Agent : "Paris : 8°C → 12°C (tendance hausse)
            Toulouse : 11°C → 15°C (tendance hausse)
            Toulouse reste ~3°C plus chaud que Paris cette semaine."
```

## Exercices de code

| Fichier | Exercice | Description |
|---------|----------|-------------|
| `question_3_3_A.py` | 3.3.A | System Prompt amélioré & injection de contexte RAG |
| `question_3_3_B.py` | 3.3.B | Fonction de chunking intelligent (~500 tokens, overlap, respect des phrases) |
| `question_3_3_C.py` | 3.3.C | Endpoint `POST /agent/evaluate` pour évaluer la qualité de l'agent |
| `question_3_8.py` | 3.8 | Script d'analyse de la base de connaissances (stats par source, chunks courts, NULL) |

**Note :** Seule **une variante** de la question 3.3 est à traiter (A, B ou C au choix).

## 🏗️ Architecture

**Structure du projet (après restructuration) :**

```
backend/          # Backend FastAPI (API + Services)
├── web/          # API Web (JWT auth) - Frontend, utilisateurs
├── services/     # Services externes (API Key auth) - Bot, MCP
└── shared/       # Code partagé (config, DB, cache)

frontend/         # Frontend React + Vite + Tailwind
docs/             # Documentation technique
scripts/          # Scripts utilitaires (tests, ingestion)
infra/            # Infrastructure & déploiement
```

**Documentation complète :** Voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

**Améliorations implémentées :**
- ✅ Cache intelligent (géocodage 24h, météo 10min)
- ✅ Timing instrumentation (identification bottlenecks)
- ✅ MCP conforme protocole standard (annotations, schemas)
- ✅ Séparation claire des responsabilités

---

## Rendus attendus

Tout via **Pull Request vers `main`**. Voir `INSTRUCTIONS_QCM.md` pour les détails complets.

| Livrable | Description |
|----------|-------------|
| QCM | `INSTRUCTIONS_QCM.md` complété (5 parties, 35+ questions) |
| Corrections backend | Bugs et failles de sécurité identifiés et corrigés (commits séparés) |
| Frontend | Interface web fonctionnelle (météo, chat agent, données) |
| Serveur MCP | 3+ tools dans `app/mcp/server.py`, connectable Claude Desktop |
| Bot Telegram | Agent conversationnel météo dans `app/bot/` |
| Exercice 3.3 | Une variante au choix (A, B ou C) |
| Exercice 3.8 | Script d'analyse `question_3_8.py` |
| Déploiement | Application accessible en ligne (Railway, Render, Fly.io, etc.) |
| Description PR | Méthodologie + URLs (application, frontend, API, MCP) |
