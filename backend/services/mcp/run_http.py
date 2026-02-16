"""
Point d'entrée pour lancer le serveur MCP en mode Streamable HTTP.

Utilisé pour le déploiement Railway (service MCP séparé).
En local, utiliser python -m app.mcp.server pour stdio (Claude Desktop).

Référence : https://modelcontextprotocol.github.io/python-sdk/
Transport : streamable-http (réseau, cloud, conteneurs)
"""
import os

from app.mcp.server import mcp

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    # Retirer 'host' - FastMCP le gère automatiquement
    mcp.run(transport="streamable-http", port=port)
