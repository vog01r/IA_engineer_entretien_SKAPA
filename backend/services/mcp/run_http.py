"""
Point d'entrée pour lancer le serveur MCP en mode Streamable HTTP.

Utilisé pour le déploiement Railway (service MCP séparé).
En local stdio : python -m backend.services.mcp.server

Variables d'environnement : PORT (défaut 8000), HOST (défaut 0.0.0.0).
Référence : https://modelcontextprotocol.github.io/python-sdk/
"""
from backend.services.mcp.server import mcp

if __name__ == "__main__":
    # Port/host lus depuis env dans backend.services.mcp.server (FastMCP constructor)
    mcp.run(transport="streamable-http")
