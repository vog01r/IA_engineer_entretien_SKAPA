# Décisions techniques — SKAPA

Ce document centralise les choix techniques effectués lors de la correction et l'implémentation du projet. Pour chaque décision : problème identifié → options analysées → choix retenu → trade-offs.

---

## 1. Sécurité — Suppression de la clé API exposée côté frontend

**Problème identifié :** `VITE_API_KEY` était injectée dans le bundle Vite au build time. Toute variable préfixée `VITE_` est embarquée dans le JS statique, visible par n'importe qui via les DevTools. La clé permettait d'appeler le backend sans restriction.

**Options analysées :**

| Option | Analyse |
|---|---|
| Garder la clé mais l'obfusquer | ❌ L'obfuscation n'est pas de la sécurité — la clé reste extractible |
| Passer la clé via un backend proxy (BFF) | ✅ Correct mais sur-complexe pour ce scope (nécessite une couche supplémentaire) |
| JWT httpOnly cookies | ✅ Standard, natif navigateur, invisible JS — choix retenu |
| Sessions serveur | ⚠️ Nécessite stockage état côté serveur, problème de scaling |

**Décision : JWT httpOnly cookies.**

Le frontend ne stocke plus aucune clé. Il envoie ses cookies automatiquement via `credentials: "include"`. Le token JWT n'est jamais accessible en JavaScript → un XSS ne peut pas le voler.

---

## 2. Authentification — JWT vs Sessions

**Problème :** Choisir un mécanisme d'auth adapté à une architecture avec plusieurs clients (frontend web, bot Telegram, MCP).

**Options analysées :**

| Option | Analyse |
|---|---|
| Sessions côté serveur | ❌ Stateful — nécessite stockage partagé si plusieurs instances |
| JWT en localStorage | ❌ Accessible JS → vulnérable XSS |
| JWT en httpOnly cookies | ✅ Stateless, XSS-proof, support natif navigateur — choix retenu |
| OAuth / OIDC | ⚠️ Correct mais sur-complexe pour ce scope sans provider externe |

**Décision : JWT HS256 + httpOnly cookies.**

- **HS256** (symétrique) : un seul secret partagé, suffisant pour un service mono-instance. RS256 (asymétrique) serait nécessaire si plusieurs services devaient vérifier le token indépendamment.
- **Access token 1h** : fenêtre d'exploitation limitée si le token est compromis.
- **Refresh token 7j** : UX fluide sans re-login constant.
- **SameSite=lax** : bloque les requêtes CSRF cross-site initiées par des formulaires tiers, tout en autorisant les navigations normales (liens, redirections OAuth).

---

## 3. Authentification duale — JWT (web) + API Key (services)

**Problème :** Le bot Telegram et le serveur MCP sont des processus backend, pas des utilisateurs humains. Ils ne peuvent pas gérer un flux login/cookie.

**Options analysées :**

| Option | Analyse |
|---|---|
| JWT pour tous | ❌ Le bot devrait stocker un token, gérer le refresh — complexité inutile |
| API Key unique pour tous | ❌ Pas de distinction utilisateur/service, pas de granularité |
| API Key pour services + JWT pour web | ✅ Chaque client utilise le mécanisme adapté à sa nature — choix retenu |

**Décision : dual-auth dans `get_current_user`.**

- Priorité 1 : JWT cookie → frontend
- Priorité 2 : `X-API-Key` header → bot, MCP
- La clé API est comparée avec `secrets.compare_digest()` (constant-time) pour résister aux timing attacks. L'opérateur `==` sur `str` Python s'arrête au premier caractère différent — un attaquant peut mesurer les délais de réponse pour reconstituer la clé caractère par caractère.

---

## 4. Rate limiting — slowapi

**Problème :** Sans limite de débit, `/auth/login` est exposé au brute-force, et `/agent/ask` peut être abusé (chaque appel déclenche un appel OpenAI facturé).

**Options analysées :**

| Option | Analyse |
|---|---|
| Rien | ❌ Brute-force possible, coûts LLM non maîtrisés |
| Nginx rate limiting | ⚠️ Correct mais nécessite infra supplémentaire |
| slowapi (middleware FastAPI) | ✅ Natif Python, zero infra, decorator simple — choix retenu |
| Redis + token bucket | ⚠️ Plus robuste en multi-instance mais sur-complexe ici |

**Décision : slowapi avec clé = IP client.**

Limites appliquées :
- `POST /auth/login` : 10 req/min — un humain légitime ne fait pas 10 tentatives de login par minute
- `POST /auth/register` : 10 req/min — protection contre la création massive de comptes
- `POST /agent/ask` : 30 req/min — usage normal confortable, abus automatisé bloqué

Limite connue : `get_remote_address` se base sur l'IP. Derrière un reverse proxy (Railway, Nginx), il faut configurer `X-Forwarded-For` pour éviter que toutes les requêtes aient la même IP.

---

## 5. Performance bot — asyncio.to_thread vs httpx async

**Problème :** Le bot Telegram tourne dans une event loop asyncio. Les appels `requests.get()` sont synchrones et bloquent l'event loop entière pendant la durée de la requête réseau.

**Options analysées :**

| Option | Analyse |
|---|---|
| requests synchrone directement | ❌ Bloque l'event loop → bot gelé pendant les appels réseau |
| asyncio.to_thread(requests.get) | ✅ Exécute le bloquant dans un thread séparé, event loop libre — choix retenu |
| httpx.AsyncClient | ✅ Plus propre, natif async, mais refactoring plus lourd |
| aiohttp | ✅ Performant mais API moins familière |

**Décision : `asyncio.to_thread()` sur les fonctions synchrones.**

C'est le pattern le plus sûr pour introduire de l'async sans refactoring massif. `httpx` async serait le choix idéal pour une réécriture complète.

---

## 6. Cache — TTL mémoire vs Redis

**Problème :** Les appels géocodage et météo sont répétitifs et lents (~150-500ms chacun). Sans cache, chaque message Telegram déclenche 2-3 appels réseau inutiles.

**Options analysées :**

| Option | Analyse |
|---|---|
| Pas de cache | ❌ Chaque requête = 3 appels réseau, latence max |
| Redis | ✅ Robuste, multi-instance, persistant — mais nécessite infra |
| Cache mémoire dict + TTL | ✅ Zero infra, thread-safe avec verrou, suffisant mono-instance — choix retenu |
| Cachetools / functools.lru_cache | ⚠️ Pas de TTL natif, données expirées jamais évincées |

**Décision : cache mémoire avec TTL.**

- Géocodage : TTL 24h (les coordonnées GPS d'une ville ne changent pas)
- Météo : TTL 10min (balance fraîcheur vs performance — la météo change peu en 10min, acceptable UX)

Limite connue : le cache est perdu au redémarrage du processus et non partagé entre instances. Redis serait nécessaire en production multi-instance.

---

## 7. MCP — stdio vs streamable-http

**Problème :** Le protocole MCP supporte plusieurs transports. Le choix impacte la compatibilité avec les clients externes.

**Options analysées :**

| Option | Analyse |
|---|---|
| stdio uniquement | ⚠️ Compatible Claude Desktop en local, pas accessible depuis internet |
| HTTP uniquement | ⚠️ Compatible clients externes (ChatGPT, curl), pas Claude Desktop local |
| Les deux (stdio + streamable-http) | ✅ Maximum de compatibilité selon le contexte — choix retenu |

**Décision : double transport via FastMCP.**

- `python -m backend.services.mcp.server` → stdio (Claude Desktop en local)
- `python backend/services/mcp/run_http.py` → streamable-http port 8001 (Railway, clients externes)

`json_response=True` : les réponses sont en JSON pur (pas SSE), compatible avec les clients qui ne gèrent pas les Server-Sent Events.

---

## 8. Structure projet — monorepo vs multi-repo

**Problème :** Le code initial mélangeait backend, bot, MCP et configuration dans les mêmes dossiers.

**Options analysées :**

| Option | Analyse |
|---|---|
| Multi-repo (1 repo par service) | ❌ Sur-complexe pour ce scope, CI/CD plus difficile |
| Monorepo avec séparation par dossiers | ✅ Simple, cohérent, déployable service par service — choix retenu |

**Décision : monorepo structuré.**

```
backend/web/       → API HTTP (JWT)
backend/services/  → Bot + MCP (API Key)
backend/shared/    → Code partagé
frontend/          → React
infra/             → Docker, Railway
docs/              → Documentation
```

La séparation `web/` vs `services/` reflète la séparation des mécanismes d'auth : les routes `web/` sont pour les utilisateurs humains (JWT), les routes `services/` pour les processus machine (API Key).

---

## Références

- [OWASP — httpOnly cookies](https://owasp.org/www-community/HttpOnly)
- [secrets.compare_digest — Python docs](https://docs.python.org/3/library/secrets.html#secrets.compare_digest)
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [slowapi — FastAPI rate limiting](https://github.com/laurentS/slowapi)
- [asyncio.to_thread — Python docs](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
