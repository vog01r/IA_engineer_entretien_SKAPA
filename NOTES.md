# Notes de corrections - Projet SKAPA

Documentation des modifications pour explication lors du debrief technique.

---

## 1. Fix .gitignore (fix(security))

**Problème :** Lignes commentées = fichier pas ignoré → secrets potentiellement versionnés.

**Ce qu'on a fait :**
- Décommenter `.env` (clés API, secrets)
- Décommenter `.venv/`, `venv/`, `env/` (environnements virtuels)
- Ajouter `*.db`, `*.sqlite`, `database.db` (base de données locale)

**Pourquoi c'est critique :** Un `.gitignore` commenté ne protège rien. `.env` en clair sur un repo = clés exposées, compromission possible.

**Si on te challenge :** "Pourquoi .gitignore seul ne suffit pas si .env était déjà commité ?" → `.gitignore` n'affecte que les fichiers *untracked*. Une fois un fichier suivi par git, le mettre dans .gitignore ne le retire pas du tracking.

---

## 2. Retrait .env du Git (fix(security))

**Problème :** .env était déjà tracké (à cause du .gitignore cassé). Même après fix du .gitignore, git continuait à le suivre.

**Ce qu'on a fait :** `git rm --cached .env` + commit

**Explication :** `--cached` = retire du suivi git mais garde le fichier sur le disque. Sans `--cached`, le fichier serait supprimé localement.

**Limite à connaître :** Les anciens commits gardent .env dans l'historique. Pour purger complètement : `git filter-repo` ou BFG. Risqué sur repo partagé (réécrit l'historique).

---

## 3. .env.example (docs)

**Problème :** Pas de template pour les nouveaux devs → confusion sur les variables à configurer, risque de copier un .env de prod par erreur.

**Ce qu'on a fait :** Fichier sans secrets, placeholders uniquement. Liste exhaustive des vars (API_KEY, DATABASE_URL, OPENAI_API_KEY, ALLOWED_ORIGINS, etc.).

**Pourquoi :** Documenter la config sans exposer de secrets. Jamais versionner de vraies clés.

---

## 4. Fix CORS (fix(security))

**Problème :** `allow_origins=["*"]` = n'importe quel site peut faire des requêtes cross-origin vers l'API. Avec `allow_credentials=True`, fuite de cookies possible.

**Ce qu'on a fait :**
1. **config.py** : `ALLOWED_ORIGINS` lu depuis env, split par virgule
2. **app.py** : `allow_origins=ALLOWED_ORIGINS` au lieu de `["*"]`
3. **Gestion du cas vide** : Si `ALLOWED_ORIGINS=""` → `[]` (pas `[""]` qui ferait bugger CORS)

```python
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
```

**Pourquoi le strip() et le if :** 
- `strip()` : enlève espaces avant/après (ex: "http://a.com, http://b.com")
- `if origin.strip()` : filtre les chaînes vides pour éviter `[""]`

**Si on te challenge :** "Pourquoi pas juste split ?" → `"".split(",")` donne `[""]`. Une origine vide peut faire échouer la validation CORS ou accepter des requêtes invalides.

---

## 5. Fix DEBUG (config.py) — commit séparé

**Problème :** `DEBUG = True` hardcodé = en prod les stack traces s'affichent, infos sensibles exposées.

**Ce qu'on a fait :** `DEBUG = os.getenv("DEBUG", "false").lower() == "true"`

**Pourquoi défaut "false" :** Fail-safe. Si la var n'est pas set → on assume prod, pas de debug.

**Pourquoi commit séparé :** One fix = one atomic commit. CORS et DEBUG sont deux corrections distinctes.

---

## 6. Unification chemin BDD (fix(config))

**Problème :** 3 sources de vérité pour le chemin DB → .env, config.py (défaut weather.db), crud.py (hardcodé database.db). Risque de 3 bases différentes selon l'ordre de chargement.

**Ce qu'on a fait :**
- config.py : DATABASE_URL lu depuis env (défaut `sqlite:///database.db`), DATABASE_PATH = extraction du path
- crud.py : `from app.config import DATABASE_PATH` au lieu de hardcodé

**Pourquoi .replace("sqlite:///", "") :** SQLite URL format. Pour `sqlite:///database.db` → `database.db`. Pour `sqlite:////data/db.db` (absolu) → `/data/db.db`.

**Si on te challenge :** "Et si on utilise PostgreSQL plus tard ?" → Le replace ne marche que pour SQLite. Il faudrait un parser d'URL (urllib.parse) ou une lib type sqlalchemy pour les autres backends. Pour ce scope SQLite uniquement, c'est suffisant.

---

## 7. Context managers DB (fix(db))

**Problème :** Pattern `conn = _get_conn()` ... `conn.close()` → si exception avant close(), la connexion reste ouverte (fuite). En charge, on peut épuiser le pool.

**Ce qu'on a fait :** Remplacer par `with sqlite3.connect(DATABASE_PATH) as conn:` partout. Suppression de `_get_conn()`.

**Pourquoi ça marche :** Le context manager garantit que `__exit__` est appelé même en cas d'exception → connexion fermée correctement.

**Important :** Garder `conn.commit()` explicite dans les fonctions d'écriture (INSERT/UPDATE/DELETE/CREATE). Sans ça, les modifs peuvent ne pas être persistées. Les SELECT n'ont pas besoin de commit.

---

## 8. Documentation limitation search_chunks (docs)

**Problème (QCM Q2.8) :** search_chunks utilise LIKE → recherche lexicale pure. "quel temps fait-il ?" ne matche pas "prévisions météorologiques".

**Ce qu'on a fait :** Docstring enrichie explicite sur la limitation, avec exemples et recommandation prod (pgvector, ChromaDB).

**Pourquoi documenter :** Éviter que quelqu'un s'attende à une recherche sémantique. Clarifier le scope pour le debrief.

---

## 9. Validation API weather (fix(api))

**Problème :** latitude/longitude non validés → `9999`, `-9999` acceptés. Range valide : lat -90 à 90, lon -180 à 180.

**Ce qu'on a fait :** Modèle Pydantic `WeatherParams` avec `Field(ge=..., le=...)`. Utilisé via `Depends()` dans `fetch_weather` et `list_weather_by_location`.

**Pourquoi Pydantic :** Validation automatique, message d'erreur 422 explicite (ex: "ensure this value is less than or equal to 90"). FastAPI injecte le modèle depuis les query params.

**Note :** fetch_weather n'a plus de valeurs par défaut (lat/lon requis). Si besoin de defaults : `Field(43.6599, ge=-90, le=90)`.

---

## 10. Agent IA RAG (fix(agent)) — 4 commits

### Commit 1/4 : Structure + injection contexte RAG

**Problème (QCM Q3.1) :** Contexte RAG récupéré mais jamais injecté dans le prompt → l'agent répondait sans base de connaissances.

**Ce qu'on a fait :**
- Classe `Agent` avec `__init__(model, api_key, provider)`
- Méthode `ask(question)` : search_chunks → build context → injecter dans user message
- Format : `{"role": "user", "content": f"Contexte:\n{context}\n\nQuestion: {question}"}`

**Pourquoi injecter dans le user et pas le system :** Les deux marchent. Mettre dans le user rend explicite que le contexte change à chaque question. Le system prompt reste stable.

**Dépendance :** `openai` ajoutée à requirements.txt.

### Commit 2/4 : System prompt structuré

**Problème (QCM Q2.7) :** Prompt vague → hallucinations, pas de citation des sources.

**Ce qu'on a fait :** Règles strictes : (1) uniquement le contexte, (2) "Je ne dispose pas..." si absent, (3) citer la source, (4) pas d'extrapolation. Format réponse : concise, factuelle, avec source.

### Commit 3/4 : Température 0.1

**Problème (QCM Q3.1) :** temperature=0.7 → réponses trop variables/créatives pour Q&A factuel.

**Ce qu'on a fait :** temperature=0.1 → réponses plus cohérentes et prévisibles.

### Commit 4/4 : Gestion d'erreur

**Problème (QCM Q3.1) :** Pas de try/except → crash si API LLM échoue ou DB pose problème.

**Ce qu'on a fait :** try/except global, message si context_chunks vide, fallback si content None.

---

## 11. Endpoint POST /agent/ask (feat(agent))

**Problème :** Le frontend appelle POST /agent/ask mais l'endpoint n'existait pas (placeholder seul).

**Ce qu'on a fait :**
- `QuestionRequest` Pydantic : `{question: str}`
- Instanciation Agent au chargement (model, api_key, provider depuis env)
- `OPENAI_MODEL` (défaut gpt-4o-mini), `OPENAI_API_KEY`
- Retourne `{"answer": str}`

**Pourquoi initialiser l'Agent au module load :** Éviter de recréer le client à chaque requête. Alternative : singleton ou dependency injection FastAPI.

---

## 12. Service API frontend (feat(frontend))

**Fichier :** `frontend/src/services/api.js`

**Ce qu'on a fait :**
- `weatherAPI` : getAll(), fetchWeather(lat, lon), getByLocation(lat, lon)
- `agentAPI` : ask(question) → POST /agent/ask
- Header `X-API-Key` sur toutes les requêtes
- Variables `VITE_API_URL`, `VITE_API_KEY` (préfixe VITE_ requis pour exposition au client)
- `handleResponse` : throw Error si !response.ok

**Pourquoi VITE_ :** Vite n'expose que les variables préfixées pour éviter de divulguer des secrets au build.

---

## 13. Composant WeatherDashboard (feat(frontend))

**Fichier :** `frontend/src/components/WeatherDashboard.jsx`

**Fonctionnalités :**
- Fetch `weatherAPI.getAll()` au mount
- États : loading, error, empty, data
- Grille responsive : 1 col mobile, 2 tablette, 3 desktop (Tailwind grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- Cards : latitude, longitude, time, temperature_2m

**Détails techniques :**
- `useEffect` avec cleanup (`cancelled`) pour éviter setState après unmount (race condition si nav rapide)
- Key fallback : `id` ou `${lat}-${lon}-${time}` si pas d'id

**Si on te challenge :** "Pourquoi le cancelled ?" → Si l'utilisateur quitte la page avant la fin du fetch, la réponse arrive et setState serait appelé sur un composant démonté → warning React "Can't perform a React state update on an unmounted component".

---

## 14. Composant LocationSearch (feat(frontend))

**Fichier :** `frontend/src/components/LocationSearch.jsx`

**Fonctionnalités :**
- Form latitude / longitude avec validation côté client
- Plages : lat -90 à 90, lon -180 à 180 (aligné avec validation backend)
- `weatherAPI.fetchWeather(lat, lon)` au submit
- États : loading, message succès (vert) ou erreur (rouge)

**Validation :** `validateCoords()` avant appel API — évite requêtes inutiles, feedback immédiat si coordonnées invalides.

**Style :** Card blanche, inputs avec focus:ring, bouton bleu, messages colorés (bg-green-100 / bg-red-100).

**Amélioration (consigne "lieu donné") :** Remplacement lat/lon manuels par boutons villes (Paris, Lyon, Marseille, Toulouse, Bordeaux). Plus conforme à "récupération météo pour un lieu donné".

---

## 14b. Base de connaissances + ingestion (feat(agent))

**Problème :** Agent retournait "Aucun contexte pertinent" car knowledge_chunks était vide.

**Solution :**
- knowledge_base/guide_meteo.txt : contenu sur Paris, Lyon, Marseille, Toulouse, météo
- scripts/ingest_knowledge.py : ingestion par paragraphes
- Amélioration search_chunks : extraction mots-clés ("quelle météo à Paris" → Paris, météo), recherche OR sur les mots

**Commande :** `python scripts/ingest_knowledge.py` — à lancer une fois pour peupler la base.

---

## 15. Composant ChatInterface (feat(frontend))

**Fichier :** `frontend/src/components/ChatInterface.jsx`

**Fonctionnalités :**
- Liste messages `{role: "user"|"assistant", content: string}`
- Input + bouton Envoyer → `agentAPI.ask(question)`
- Ajout message user puis réponse assistant à l'historique
- Auto-scroll avec `useRef` + `scrollIntoView({ behavior: "smooth" })`
- Loading : affiche "Réflexion..." pendant la réponse

**Style :** User à droite (bg-blue-500), assistant à gauche (bg-gray-200). Zone messages h-96 overflow-y-auto. Erreur API affichée comme message assistant.

**useRef pour scroll :** Élément invisible en bas de la liste, `ref` dessus. `useEffect` sur `messages` appelle `scrollToBottom()` pour garder le dernier message visible.

---

## 16. Layout App.jsx (feat(frontend))

**Fichier :** `frontend/src/App.jsx`

**Structure :** Container max-w-7xl, titre h1, 3 sections space-y-8 avec WeatherDashboard, LocationSearch, ChatInterface.

**Style :** bg-gray-50 min-h-screen, titre text-4xl center, sections avec bg-white shadow rounded p-6.

---

## 17. Fix Tailwind v4 + PostCSS (fix(frontend))

**Problème :** Tailwind v4 a déplacé le plugin PostCSS dans `@tailwindcss/postcss`. L'ancienne config `tailwindcss: {}` dans postcss.config.js provoquait une erreur.

**Solution :** Utiliser le plugin Vite officiel `@tailwindcss/vite` :
- `npm install -D @tailwindcss/vite`
- Ajouter `tailwindcss()` dans vite.config.js
- Remplacer `@tailwind base/components/utilities` par `@import "tailwindcss"` dans index.css
- Retirer `tailwindcss` de postcss.config.js (le plugin Vite gère Tailwind)

---

## Récap des commits (ordre)

1. `fix(security): correction .gitignore` 
2. `fix(security): retrait .env de l'historique Git`
3. `docs: ajout template .env.example`
4. `fix(security): restriction CORS via liste blanche environnement`
5. `fix(security): DEBUG depuis variable environnement avec défaut sûr`
6. `fix(config): unification chemin base de données`
7. `fix(db): context managers pour connexions SQLite`
8. `docs(db): documentation limitation recherche LIKE dans search_chunks`
9. `fix(api): validation coordonnées GPS avec Pydantic`
10a. `fix(agent): implémentation Agent + injection contexte RAG`
10b. `fix(agent): system prompt structuré avec règles strictes`
10c. `fix(agent): température 0.1 pour Q&A factuel`
10d. `fix(agent): gestion d'erreur dans ask()`
11. `feat(agent): endpoint POST /agent/ask`
12. `feat(frontend): service API météo et agent`
13. `feat(frontend): composant WeatherDashboard`
14. `feat(frontend): composant LocationSearch`
15. `feat(frontend): composant ChatInterface`
16. `feat(frontend): layout App.jsx avec 3 composants`
17. `fix(frontend): Tailwind v4 avec @tailwindcss/vite`
18. `fix(frontend): regrouper les prévisions météo par lieu, limiter à 24h`
19. `fix(ux): message météo avec résumé et layout 2 colonnes`

---

## 18. WeatherDashboard regroupement (fix(frontend))

**Problème :** 672 cards affichées (168h × 4 villes) → liste infinie illisible.

**Ce qu'on a fait :**
- Fonction `groupByLocation(data)` : regroupe par clé `latitude,longitude`
- Pour chaque lieu : titre avec coordonnées, tri par date asc
- `slice(0, 24)` : seulement les 24 prochaines heures par lieu
- Grid responsive : `grid-cols-2 sm:grid-cols-3 md:grid-cols-4` (max 4 cards par ligne)

---

## 19. Message météo + layout 2 colonnes (fix(ux))

**Problème 1 :** Message technique "Météo récupérée : 168 prévisions enregistrées pour Paris." peu utile pour l'utilisateur.

**Solution message :**
- Backend : ajout `current=temperature_2m,weather_code` dans l'appel Open-Meteo
- Mapping WMO → libellés français (ciel dégagé, couvert, pluie, etc.)
- Réponse enrichie : `summary: { current_temp, weather_label }`
- Frontend LocationSearch : affiche "Paris : 2°C, couvert. Prévisions enregistrées." au lieu du message technique

**Problème 2 :** LocationSearch et ChatInterface invisibles (en bas après 672 cards).

**Solution layout :**
- Grid 2 colonnes : `grid-cols-1 lg:grid-cols-2 gap-8`
- Colonne gauche : LocationSearch + ChatInterface
- Colonne droite : WeatherDashboard
- Mobile : empilement vertical (grid-cols-1)

---

## Serveur MCP (feat(mcp))

**Objectif :** Exposer 3 tools MCP connectables depuis Claude Desktop ou un client MCP.

**Implémentation :**
- **Framework :** FastMCP (MCP Python SDK officiel)
- **Transport :** stdio (requis pour Claude Desktop)
- **Outils :**
  1. `get_weather(latitude, longitude)` — Appel direct Open-Meteo, retourne température actuelle + prévisions 24h avec libellés WMO
  2. `search_knowledge(query, limit=5)` — Utilise `search_chunks()` depuis `app.db.crud`
  3. `conversation_history(limit=10)` — Utilise `get_conversations()` depuis `app.db.crud`

**Structured output (get_weather) :** Modèles Pydantic `WeatherResponse` et `WeatherForecastItem` pour que le SDK génère un schéma de sortie exploitable par les clients MCP (aligné sur weather_structured.py du repo SDK).

**Gestion d'erreurs get_weather :** Un seul `try/except RequestException` → retourne `{"error": True, "message": "..."}` au lieu de laisser l'exception remonter. Le LLM peut expliquer le problème à l'utilisateur.

**Installation :** `pip install mcp` suffit pour le serveur. `mcp[cli]` ajoute la commande `mcp` et l'Inspector pour tester — optionnel, la spec dit "pip install mcp".

**Pourquoi FastMCP et pas le Server low-level ?** Le SDK Python recommande FastMCP : API plus simple (@mcp.tool()), gestion automatique du transport stdio via `mcp.run(transport="stdio")`, moins de boilerplate. Le Server low-level existe (mcp.server.Server) mais demande plus de code manuel.

**Pourquoi stdio ?** Claude Desktop lance le serveur en subprocess et communique via stdin/stdout. Pas de port, pas de réseau — idéal pour une app locale.

**Pourquoi get_weather appelle Open-Meteo directement et pas /weather/fetch ?** Le serveur MCP tourne en processus séparé (stdio). Appeler l'API interne nécessiterait une URL (localhost:8000). Appel direct = pas de dépendance au backend FastAPI, fonctionne même si l'API est arrêtée.

**Conformité spec :** Tous les points couverts (3 tools, inputs/outputs, stdio, config Claude Desktop). Choix assumé : Open-Meteo au lieu de l'API interne (hint autorisait les deux).

**Lancement :** `python -m app.mcp.server` (depuis la racine, venv activé)

**Testé avec Cursor MCP :** Config dans `~/.cursor/mcp.json`, serveur SKAPA ajouté. Test get_weather(Paris) : OK. Fonctionne parfaitement.

**Claude Desktop :** Ajouter dans `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) :
```json
{
  "mcpServers": {
    "skapa": {
      "command": "/chemin/absolu/.venv/bin/python",
      "args": ["-m", "app.mcp.server"],
      "cwd": "/chemin/absolu/IA_engineer_entretien_SKAPA",
      "env": {}
    }
  }
}
```
(Utiliser le python du venv pour éviter conflits de dépendances.)

**Questions possibles en debrief :**
- "C'est quoi MCP ?" → Model Context Protocol, standard pour exposer des outils/contexte aux LLM de manière standardisée.
- "Pourquoi 3 tools et pas plus ?" → Spec du test. On pourrait ajouter ask_agent (appel LLM) mais nécessiterait config OpenAI et plus de complexité.
- "get_weather ne stocke pas en BDD ?" → Non, le tool MCP est read-only pour le client. Le endpoint /weather/fetch de l'API fait le stockage. Évite duplication de logique.
- "Pourquoi Pydantic pour la sortie ?" → Structured output : le SDK génère un schéma JSON que les clients peuvent valider. Aligné sur les exemples officiels (weather_structured.py).

---

## Points à anticiper en debrief

- **"Pourquoi CORS avec credentials + wildcard est dangereux ?"** → Un site malveillant peut faire des requêtes authentifiées (cookies) vers ton API depuis le navigateur d'une victime connectée.
- **"Pourquoi ne pas utiliser allow_origins=["*"] en dev ?"** → On peut, mais mieux vaut reproduire la config prod. Et si on oublie de restreindre au déploiement = fail.
- **"Tu as testé que ça marche après le fix CORS ?"** → Oui, avec ALLOWED_ORIGINS incluant localhost:5173 (Vite) et 3000 (React classique).
