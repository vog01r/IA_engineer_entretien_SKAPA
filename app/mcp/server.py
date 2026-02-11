# ═══════════════════════════════════════════════════════════════
# Serveur MCP — À compléter
# ═══════════════════════════════════════════════════════════════
#
# Objectif : créer un serveur MCP (Model Context Protocol) qui expose
# au moins 3 tools, connectable depuis Claude Desktop ou un client MCP.
#
# Tools attendus :
#
#   1. get_weather
#      - Description : Récupère les prévisions météo pour un lieu donné
#      - Input : latitude (float), longitude (float)
#      - Output : données météo (température, prévisions)
#      - Hint : appeler l'API interne /weather/fetch ou Open-Meteo directement
#
#   2. search_knowledge
#      - Description : Recherche dans la base de connaissances de l'agent
#      - Input : query (str), limit (int, optionnel, défaut 5)
#      - Output : liste des chunks pertinents trouvés
#
#   3. Un tool de votre choix (exemples) :
#      - ask_agent : poser une question à l'agent et obtenir une réponse
#      - get_weather_stats : statistiques sur les données météo en base
#      - get_history : historique des dernières conversations
#
# Ressources :
# - MCP Python SDK : https://github.com/modelcontextprotocol/python-sdk
# - Documentation MCP : https://modelcontextprotocol.io/docs
# - pip install mcp
#
# Le serveur peut être exposé via stdio (pour Claude Desktop)
# ou via HTTP (Streamable HTTP, pour les clients web).
#
# Pour tester avec Claude Desktop, ajoutez la config dans
# ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
# ou %APPDATA%\Claude\claude_desktop_config.json (Windows)
# ═══════════════════════════════════════════════════════════════
