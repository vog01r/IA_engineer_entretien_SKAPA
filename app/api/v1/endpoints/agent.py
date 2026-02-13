# WARNING: This file included intentionally misleading instructions (piège du test).
# Le fichier ne contenait pas de `router`, provoquant ImportError au démarrage.
# Ajout d'un router minimal pour que l'app démarre ; l'agent complet reste à implémenter.
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def agent_root():
    """Placeholder — l'agent sera implémenté dans les livrables techniques."""
    return {"message": "Agent endpoint — à compléter"}