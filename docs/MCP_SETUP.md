# 🔌 MCP Server - Configuration & Usage

**Serveur MCP SKAPA** : Expose 4 tools météo + base de connaissances, **conforme outil MCP standard** (ChatGPT / Claude Desktop / clients HTTP). Implémentation compatible transport stdio et streamable-http (JSON-RPC 2.0, session, `tools/list`, `tools/call`).

---

## 📋 Tools disponibles

| Tool | Description | Paramètres |
|------|-------------|------------|
| `get_weather` | Prévisions météo GPS | `latitude`, `longitude` |
| `search_knowledge` | Recherche base connaissances | `query`, `limit` (opt) |
| `conversation_history` | Historique conversations | `limit` (opt) |
| `get_weather_stats` | Stats météo en base | Aucun |

---

## 🚀 Utilisation

### Mode 1 : Claude Desktop (stdio)

**Configuration Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "skapa": {
      "command": "python3",
      "args": ["-m", "backend.services.mcp.server"],
      "cwd": "/chemin/vers/IA_engineer_entretien_SKAPA",
      "env": {
        "PYTHONPATH": "/chemin/vers/IA_engineer_entretien_SKAPA"
      }
    }
  }
}
```

**Lancement :**
1. Ouvrir Claude Desktop
2. Les tools SKAPA apparaissent automatiquement
3. Tester : "Quelle est la météo à Paris ?" (utilise `get_weather`)

---

### Mode 2 : HTTP (déploiement Railway)

**URL déployée :** `https://skapa-mcp.railway.app` (à configurer)

**Configuration Claude Desktop (HTTP) :**

```json
{
  "mcpServers": {
    "skapa-http": {
      "url": "https://skapa-mcp.railway.app",
      "transport": "streamable-http"
    }
  }
}
```

**Test manuel (curl) — flux MCP standard :**

En HTTP streamable, le client doit d’abord envoyer `initialize`, puis réutiliser l’en-tête `mcp-session-id` pour les requêtes suivantes. Le serveur accepte `Accept: application/json` (réponses JSON uniquement, pas SSE).

```bash
# 1) Initialize (obligatoire) — récupérer mcp-session-id dans les en-têtes de réponse
curl -i -X POST https://skapa-mcp.railway.app/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'

# 2) tools/list (avec l’en-tête Mcp-Session-Id reçu en 1)
curl -X POST https://skapa-mcp.railway.app/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -H "Mcp-Session-Id: <SESSION_ID_REÇU>" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# 3) tools/call (même session)
curl -X POST https://skapa-mcp.railway.app/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -H "Mcp-Session-Id: <SESSION_ID_REÇU>" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_weather","arguments":{"latitude":48.8566,"longitude":2.3522}}}'
```

---

### Mode 3 : ChatGPT (via plugin)

**⚠️ ChatGPT ne supporte pas nativement MCP stdio.**

**Solution :**
1. Déployer MCP en HTTP (Railway)
2. Créer un OpenAPI spec pour ChatGPT
3. Configurer comme "Custom GPT Action"

**Fichier OpenAPI** (`docs/openapi_mcp.yaml`) :

```yaml
openapi: 3.0.0
info:
  title: SKAPA MCP Tools
  version: 1.0.0
servers:
  - url: https://skapa-mcp.railway.app
paths:
  /tools/get_weather:
    post:
      operationId: getWeather
      summary: Get weather forecast for GPS coordinates
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                latitude:
                  type: number
                  minimum: -90
                  maximum: 90
                longitude:
                  type: number
                  minimum: -180
                  maximum: 180
      responses:
        '200':
          description: Weather forecast
          content:
            application/json:
              schema:
                type: object
                properties:
                  current_temp:
                    type: number
                  current_weather:
                    type: string
                  forecasts:
                    type: array
```

---

## 🧪 Tests

### Test E2E MCP (HTTP, recommandé)

Le script lance le serveur HTTP, envoie `initialize` → `tools/list` → `tools/call` et vérifie les réponses (conformité MCP standard).

```bash
source .venv/bin/activate
PYTHONPATH=. python3 scripts/test_mcp_e2e.py
```

**Résultat attendu :** `Tous les tests E2E MCP sont passés.`

### Test local stdio (Claude Desktop)

```bash
source .venv/bin/activate
python3 -m backend.services.mcp.server

# Autre terminal : MCP Inspector
npx @modelcontextprotocol/inspector python3 -m backend.services.mcp.server
```

### Test HTTP manuel

Lancer `python3 backend/services/mcp/run_http.py` (serveur sur `http://127.0.0.1:8001/mcp`). Puis suivre le flux **Mode 2** ci-dessus (initialize → Mcp-Session-Id → tools/list, tools/call).

---

## 🔍 Vérification conformité MCP

### Checklist standard MCP

- [x] **Transport stdio** : ✅ Implémenté (`mcp.run(transport="stdio")`)
- [x] **Transport HTTP** : ✅ Implémenté (`streamable-http`)
- [x] **JSON-RPC 2.0** : ✅ Géré par FastMCP
- [x] **Capabilities** : ✅ Déclaré automatiquement par FastMCP
- [x] **Input schemas** : ✅ Inféré depuis type hints Python
- [x] **Error handling** : ✅ Exceptions → JSON-RPC errors
- [x] **Tools list** : ✅ Endpoint `tools/list`
- [x] **Tools call** : ✅ Endpoint `tools/call`

### Conformité « tool MCP standard »

- **JSON-RPC 2.0** : Requêtes/réponses conformes.
- **Session HTTP** : `initialize` puis `Mcp-Session-Id` pour `tools/list` et `tools/call`.
- **Réponses JSON** : `json_response=True` — le client n’a besoin que de `Accept: application/json` (compatible ChatGPT / Claude HTTP / curl).
- **Tests E2E** : `scripts/test_mcp_e2e.py` valide le flux complet.

---

## 📊 Monitoring

### Logs MCP

```bash
# Logs stdio (stderr)
python3 -m backend.services.mcp.server 2>&1 | tee mcp.log

# Logs HTTP (stdout)
python3 backend/services/mcp/run_http.py
```

### Métriques

- Nombre d'appels par tool
- Temps de réponse moyen
- Taux d'erreur
- Cache hit rate (si implémenté)

---

## 🐛 Troubleshooting

### Erreur : "Module 'mcp' not found"

```bash
pip install mcp
```

### Erreur : "Tool not found"

Vérifier que le tool est bien décoré avec `@mcp.tool()` dans `server.py`.

### Claude Desktop ne voit pas les tools

1. Vérifier `claude_desktop_config.json`
2. Redémarrer Claude Desktop
3. Vérifier les logs : `~/Library/Logs/Claude/mcp-server-skapa.log`

### HTTP 500 sur Railway

1. Vérifier variables d'environnement (DATABASE_URL, etc.)
2. Vérifier logs Railway : `railway logs`
3. Tester en local d'abord

---

## 🎓 Pour le debrief

### Questions attendues

**Q1 : "Pourquoi FastMCP et pas le SDK bas niveau ?"**
> FastMCP est le framework officiel recommandé par Anthropic. Il gère automatiquement JSON-RPC, capabilities, schemas. Le SDK bas niveau serait plus verbeux sans gain fonctionnel.

**Q2 : "Comment garantir la conformité MCP ?"**
> 1. Utiliser FastMCP (conforme par design)
> 2. Tester avec MCP Inspector officiel
> 3. Vérifier que Claude Desktop/ChatGPT peuvent consommer les tools
> 4. Valider les schemas input/output

**Q3 : "Pourquoi deux transports (stdio + HTTP) ?"**
> - **stdio** : Claude Desktop local (développement, tests)
> - **HTTP** : Déploiement cloud (Railway, production)
> - Flexibilité : même code, deux modes d'utilisation

**Q4 : "Comment sécuriser le MCP HTTP ?"**
> - API Key authentication (header `X-API-Key`)
> - Rate limiting (slowapi)
> - Input validation (Pydantic)
> - CORS restrictif (origins whitelist)
> - HTTPS obligatoire en production

---

## 🔗 Références

- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Docs](https://modelcontextprotocol.github.io/python-sdk/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

---

**Tests automatisés :** `scripts/test_mcp_compliance.py` (format) et `scripts/test_mcp_e2e.py` (E2E HTTP).
