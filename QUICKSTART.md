# 🚀 Guide de démarrage rapide - SKAPA

**Pour tester les améliorations de performance et MCP**

---

## ⚠️ Prérequis

1. **Venv activé** : `source .venv/bin/activate`
2. **Variables d'environnement** : Fichier `.env` configuré
3. **Python 3** : Utiliser `python3` (pas `python` sur macOS)

---

## 🧪 Tests sans backend (tests unitaires)

### Test 1 : Conformité MCP

```bash
# Activer venv
source .venv/bin/activate

# Lancer test MCP (pas besoin de backend)
python3 scripts/test_mcp_compliance.py
```

**Résultat attendu :**
```
✅ TOUS LES TESTS PASSÉS
📊 RÉSUMÉ:
  ✅ JSON-RPC 2.0 format
  ✅ Capabilities declaration
  ✅ Tools list/call endpoints
  ✅ Input schemas (Pydantic)
  ✅ Error handling
  ✅ Annotations (audience, priority)

💡 CONFORMITÉ MCP: 100%
```

---

## 🔧 Tests avec backend (tests d'intégration)

### Étape 1 : Lancer le backend

**Terminal 1 :**
```bash
# Activer venv
source .venv/bin/activate

# Lancer backend FastAPI
python3 -m uvicorn backend.main:app --reload --port 8000
```

**Vérifier que ça tourne :**
```bash
curl http://localhost:8000/
# Doit retourner : {"message": "SKAPA Backend API", ...}
```

---

### Étape 2 : Tester les performances

**Terminal 2 :**
```bash
# Activer venv
source .venv/bin/activate

# Lancer test performance
python3 scripts/test_bot_performance.py
```

**Résultat attendu :**
```
🔬 TEST PERFORMANCE BOT TELEGRAM
================================================================================

📍 Test 1: Géocodage (Open-Meteo)
  Paris           → 0.234s | Paris, France
  Tokyo           → 0.312s | Tokyo, Japan
  New York        → 0.289s | New York, United States

🌤️  Test 2: API Météo (FastAPI → Open-Meteo)
  Paris           → 1.123s | 8°C
  Tokyo           → 1.234s | 15°C
  New York        → 1.189s | 5°C

🤖 Test 3: Agent LLM (question météo)
  Météo à Paris                  → 3.456s
    Answer: Actuellement à Paris : 8°C, ciel dégagé...
  
📊 ANALYSE:
  - Géocodage: ~0.2-0.5s (acceptable)
  - Météo API: ~0.5-1.5s (acceptable)
  - Agent LLM: ~1-5s (BOTTLENECK PRINCIPAL)

💡 RECOMMANDATIONS:
  1. Cache météo (10min) → évite appels inutiles
  2. Cache geocoding (24h) → évite résolutions répétées
  3. Streaming LLM → améliore perception UX
```

---

### Étape 3 : Vérifier le cache

**Après avoir lancé quelques requêtes :**

```bash
# Vérifier stats cache
curl http://localhost:8000/cache/stats

# Résultat attendu :
{
  "cache": {
    "hits": 15,
    "misses": 5,
    "total": 20,
    "hit_rate": 75.0,
    "size": 8
  },
  "interpretation": {
    "hit_rate": "75.0%",
    "efficiency": "excellent"
  }
}
```

**Interprétation :**
- **hit_rate > 70%** : Excellent (cache très efficace)
- **hit_rate 50-70%** : Bon (cache utile)
- **hit_rate < 50%** : Faible (requêtes trop variées)

---

## 🤖 Tester le bot Telegram

### Étape 1 : Vérifier le token

```bash
# Vérifier que TELEGRAM_BOT_TOKEN est défini
grep TELEGRAM_BOT_TOKEN .env
```

### Étape 2 : Lancer le bot

**Terminal 3 :**
```bash
# Activer venv
source .venv/bin/activate

# Lancer bot (avec logs timing)
python3 -m backend.services.bot.telegram_bot
```

**Logs attendus :**
```
INFO - 🤖 Bot Telegram démarré (polling mode)
INFO - ⏱️ [GEOCODING] 'Paris' took 0.234s
INFO - ⏱️ [WEATHER_FETCH] took 0.567s
INFO - ⏱️ [WEATHER_LOCATION] took 0.123s
INFO - ⏱️ [WEATHER_TOTAL] took 0.690s
INFO - ⏱️ [AGENT_LLM] question='Météo à Paris'... took 3.456s
INFO - ⏱️ [TOTAL_RESPONSE] user_message='Météo à Paris'... took 4.146s
```

### Étape 3 : Tester dans Telegram

1. Ouvrir Telegram
2. Chercher ton bot (nom dans `.env`)
3. Envoyer : `/start`
4. Envoyer : `Météo à Paris`
5. **Observer les logs** dans le terminal pour voir les timings

**Avec cache (2ème requête identique) :**
```
INFO - ⏱️ [GEOCODING] 'Paris' took 0.001s  ← Cache HIT !
INFO - ⏱️ [WEATHER_TOTAL] took 0.002s     ← Cache HIT !
INFO - ⏱️ [AGENT_LLM] question='Météo à Paris'... took 2.123s
INFO - ⏱️ [TOTAL_RESPONSE] took 2.126s    ← Gain -50% !
```

---

## 🔌 Tester le MCP Server

### Mode 1 : stdio (Claude Desktop)

**Configuration Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "skapa": {
      "command": "python3",
      "args": [
        "-m",
        "backend.services.mcp.server"
      ],
      "cwd": "/Users/chabanis/Documents/code dev/SKAPA/IA_engineer_entretien_SKAPA",
      "env": {
        "PYTHONPATH": "/Users/chabanis/Documents/code dev/SKAPA/IA_engineer_entretien_SKAPA"
      }
    }
  }
}
```

**Tester :**
1. Redémarrer Claude Desktop
2. Ouvrir une conversation
3. Les tools SKAPA devraient apparaître
4. Tester : "Quelle est la météo à Paris ?" (utilise `get_weather`)

### Mode 2 : HTTP (local)

**Terminal 4 :**
```bash
# Activer venv
source .venv/bin/activate

# Lancer MCP en HTTP
python3 backend/services/mcp/run_http.py
```

**Tester :**
```bash
# Lister les tools
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Appeler get_weather
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {
        "latitude": 48.8566,
        "longitude": 2.3522
      }
    }
  }'
```

---

## 🐛 Troubleshooting

### Erreur : "command not found: python"

**Solution :** Utiliser `python3` au lieu de `python` sur macOS.

```bash
# Vérifier version Python
python3 --version  # Doit afficher Python 3.x
```

### Erreur : "ModuleNotFoundError: No module named 'requests'"

**Solution :** Activer le venv.

```bash
source .venv/bin/activate
# Le prompt doit afficher (.venv)
```

### Erreur : "Connection refused" (test_bot_performance.py)

**Solution :** Lancer le backend d'abord.

```bash
# Terminal 1
python3 -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 (après que le backend soit lancé)
python3 scripts/test_bot_performance.py
```

### Backend ne démarre pas : "ModuleNotFoundError: No module named 'backend'"

**Solution :** Lancer depuis la racine du projet.

```bash
cd "/Users/chabanis/Documents/code dev/SKAPA/IA_engineer_entretien_SKAPA"
python3 -m uvicorn backend.main:app --reload --port 8000
```

---

## 📊 Checklist validation améliorations

### ✅ Performance

- [ ] Backend lancé (`curl http://localhost:8000/`)
- [ ] Test performance exécuté (`python3 scripts/test_bot_performance.py`)
- [ ] Logs timing visibles (⏱️ [OPERATION] took X.XXs)
- [ ] Cache stats vérifiées (`curl http://localhost:8000/cache/stats`)
- [ ] Hit rate > 50% après plusieurs requêtes

### ✅ MCP

- [ ] Test conformité passé (`python3 scripts/test_mcp_compliance.py`)
- [ ] MCP HTTP lancé (`python3 backend/services/mcp/run_http.py`)
- [ ] Tools listés (`curl -X POST http://localhost:8001/mcp ...`)
- [ ] Claude Desktop configuré (optionnel)

### ✅ Bot Telegram

- [ ] Bot lancé (`python3 -m backend.services.bot.telegram_bot`)
- [ ] Logs timing visibles
- [ ] Requête test dans Telegram
- [ ] Cache observé (2ème requête plus rapide)

---

## 🎯 Démonstration pour le senior

**Scénario recommandé :**

1. **Montrer les commits** : `git log --oneline --graph -5`
2. **Lancer backend** : Terminal 1
3. **Montrer cache vide** : `curl http://localhost:8000/cache/stats` → 0 hits
4. **Lancer test performance** : Terminal 2 → Observer timings
5. **Montrer cache rempli** : `curl http://localhost:8000/cache/stats` → hit_rate > 60%
6. **Lancer test MCP** : `python3 scripts/test_mcp_compliance.py` → 100% conforme
7. **Montrer documentation** : Ouvrir `docs/ARCHITECTURE.md`, `docs/PERFORMANCE_ANALYSIS.md`

**Phrase clé :** "J'ai mesuré avant d'optimiser. Le bottleneck principal est le LLM (70-90% du temps). Le cache réduit le temps de réponse de 40-50% sur les requêtes répétées."

---

**Bon courage pour le debrief ! 🚀**
