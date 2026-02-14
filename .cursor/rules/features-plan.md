---
description: Plan pour les features (frontend, MCP, bot)
globs:
  - "frontend/**/*"
  - "app/mcp/**/*"
  - "app/bot/**/*"
---

# Features à développer

## Frontend

**Stack : React + Vite + TailwindCSS**

React pour la structure composant, Vite pour la rapidité, Tailwind pour ne pas écrire de CSS.

**Fonctionnalités :**
- Affichage données météo stockées
- Form pour fetch météo (lat/lon)
- Interface chat avec l'agent
- Gestion header X-API-Key

**Structure :**
```
frontend/
├── src/
│   ├── components/
│   │   ├── WeatherDashboard.jsx
│   │   ├── ChatInterface.jsx
│   │   └── LocationSearch.jsx
│   ├── services/
│   │   └── api.js
│   └── App.jsx
```

Service API centralisé :
```javascript
const headers = {
  'X-API-Key': import.meta.env.VITE_API_KEY
};

export const weatherAPI = {
  async getAll() {
    const res = await fetch(`${BASE_URL}/weather/`, { headers });
    return res.json();
  },
  // ...
};
```

## Serveur MCP

**Transport : stdio** (pour Claude Desktop)

3 tools minimum :
1. `get_weather(lat, lon)` → récupère prévisions
2. `search_knowledge(query)` → cherche dans la base
3. `conversation_history(limit)` → historique chat

Structure :
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("skapa-weather")

@app.tool()
async def get_weather(latitude: float, longitude: float) -> dict:
    """Récupère météo pour coordonnées GPS"""
    # Appel API interne ou Open-Meteo
    ...

@app.tool()
async def search_knowledge(query: str, limit: int = 5) -> list:
    """Cherche dans base de connaissances"""
    # Appel search_chunks
    ...
```

Config Claude Desktop :
```json
{
  "mcpServers": {
    "skapa-weather": {
      "command": "python",
      "args": ["/path/to/app/mcp/server.py"]
    }
  }
}
```

## Bot Telegram

**Bibliothèque : python-telegram-bot**
**Mode : polling** (plus simple que webhook pour ce scope)

Fonctionnalités :
- Commande `/start`
- Détection coordonnées dans messages
- Fetch météo
- Intégration agent pour questions générales

Structure :
```python
from telegram.ext import Application, CommandHandler, MessageHandler

async def start(update, context):
    await update.message.reply_text("Bot météo SKAPA...")

async def handle_message(update, context):
    text = update.message.text
    if is_coordinates(text):
        # Fetch météo
    else:
        # Question à l'agent
```

Lancement :
```bash
python app/bot/telegram_bot.py
```

Variable env : `TELEGRAM_BOT_TOKEN`
