"""Endpoint de documentation des tools MCP — liste pour intégration/clients."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/tools")
def list_mcp_tools():
    """Liste les tools MCP disponibles (pour documentation)."""
    return {
        "tools": [
            {
                "name": "get_weather",
                "description": "Récupère les prévisions météo pour des coordonnées GPS",
                "parameters": {
                    "latitude": "float (-90 à 90)",
                    "longitude": "float (-180 à 180)",
                },
            },
            {
                "name": "search_knowledge",
                "description": "Recherche dans la base de connaissances",
                "parameters": {
                    "query": "string",
                    "limit": "int (défaut: 5)",
                },
            },
            {
                "name": "conversation_history",
                "description": "Récupère l'historique des conversations",
                "parameters": {
                    "limit": "int (défaut: 10)",
                },
            },
            {
                "name": "get_weather_stats",
                "description": "Statistiques sur les données météo en base",
                "parameters": {},
            },
        ],
        "stdio_config": "Pour Claude Desktop, utiliser stdio local (config fournie dans README)",
    }
