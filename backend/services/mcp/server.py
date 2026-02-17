"""
Serveur MCP (Model Context Protocol) — SKAPA

Expose 4 tools connectables depuis Claude Desktop ou un client MCP :
- get_weather : prévisions météo via Open-Meteo
- search_knowledge : recherche dans la base de connaissances
- conversation_history : historique des conversations agent
- get_weather_stats : statistiques sur les données météo en base

Transport : stdio (Claude Desktop)
Référence : https://modelcontextprotocol.io/docs
SDK : https://github.com/modelcontextprotocol/python-sdk
"""

import requests
from pydantic import BaseModel, Field
from requests.exceptions import RequestException
from mcp.server.fastmcp import FastMCP

from backend.shared.db.crud import get_all_weather, get_conversations, search_chunks


class WeatherForecastItem(BaseModel):
    """Prévision horaire."""

    time: str
    temperature_2m: float | None
    weather_label: str


class WeatherResponse(BaseModel):
    """Réponse structurée get_weather."""

    current_temp: float | None = Field(description="Température actuelle °C")
    current_weather: str = Field(description="Conditions (libellé WMO)")
    forecasts: list[WeatherForecastItem] = Field(description="Prévisions 24h")

# Mapping WMO weather code → libellé français (aligné avec app.api.v1.endpoints.weather)
WMO_WEATHER_LABELS = {
    0: "ciel dégagé",
    1: "principalement dégagé",
    2: "partiellement couvert",
    3: "couvert",
    45: "brouillard",
    48: "brouillard givrant",
    51: "bruine légère",
    53: "bruine modérée",
    55: "bruine dense",
    61: "pluie légère",
    63: "pluie modérée",
    65: "pluie forte",
    71: "neige légère",
    73: "neige modérée",
    75: "neige forte",
    80: "averses légères",
    81: "averses modérées",
    82: "averses violentes",
    95: "orage",
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _wmo_to_label(code: int | None) -> str:
    if code is None:
        return "—"
    return WMO_WEATHER_LABELS.get(code, "conditions variables")


def _fetch_weather_from_api(latitude: float, longitude: float) -> dict:
    """Appel direct à l'API Open-Meteo. Lève RequestException en cas d'erreur."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,weather_code",
        "current": "temperature_2m,weather_code",
    }
    r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


mcp = FastMCP(
    "SKAPA",
    instructions="Serveur MCP pour l'application SKAPA : météo, base de connaissances, historique des conversations et statistiques météo en base.",
)


@mcp.tool(
    description="Récupère les prévisions météo pour des coordonnées GPS. "
                "Retourne la température actuelle, les conditions météo et les prévisions 24h.",
    annotations={
        "audience": ["user", "assistant"],
        "priority": 0.9,
    }
)
def get_weather(
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 à 90)"),
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 à 180)")
) -> WeatherResponse | dict:
    """Récupère les prévisions météo pour des coordonnées GPS.

    Args:
        latitude: Latitude (-90 à 90)
        longitude: Longitude (-180 à 180)

    Returns:
        WeatherResponse avec current_temp, current_weather, forecasts
        Ou dict avec error=True en cas d'échec
    """
    try:
        data = _fetch_weather_from_api(latitude, longitude)
    except RequestException as e:
        return {"error": True, "message": f"API météo indisponible : {e}"}

    current = data.get("current") or {}
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []
    codes = hourly.get("weather_code") or []

    forecasts = [
        WeatherForecastItem(
            time=time_str,
            temperature_2m=temps[i] if i < len(temps) else None,
            weather_label=_wmo_to_label(codes[i] if i < len(codes) else None),
        )
        for i, time_str in enumerate(times[:24])
    ]

    return WeatherResponse(
        current_temp=current.get("temperature_2m"),
        current_weather=_wmo_to_label(current.get("weather_code")),
        forecasts=forecasts,
    )


@mcp.tool(
    description="Recherche dans la base de connaissances de l'agent SKAPA. "
                "Retourne les chunks les plus pertinents pour la requête.",
    annotations={
        "audience": ["assistant"],
        "priority": 0.7,
    }
)
def search_knowledge(
    query: str = Field(..., min_length=2, description="Requête de recherche (mots-clés ou phrase)"),
    limit: int = Field(5, ge=1, le=20, description="Nombre maximal de chunks à retourner")
) -> list[dict]:
    """Recherche dans la base de connaissances de l'agent.

    Args:
        query: Requête de recherche (mots-clés ou phrase)
        limit: Nombre maximal de chunks à retourner (défaut: 5, max: 20)

    Returns:
        Liste de chunks pertinents avec source_file, content, chunk_index
    """
    chunks = search_chunks(query, limit=limit)
    return [
        {
            "source_file": c.get("source_file"),
            "content": c.get("content"),
            "chunk_index": c.get("chunk_index"),
        }
        for c in chunks
    ]


@mcp.tool(
    description="Récupère l'historique des conversations avec l'agent SKAPA. "
                "Utile pour comprendre le contexte des interactions passées.",
    annotations={
        "audience": ["assistant"],
        "priority": 0.5,
    }
)
def conversation_history(
    limit: int = Field(10, ge=1, le=100, description="Nombre maximal de conversations à retourner")
) -> list[dict]:
    """Récupère l'historique des conversations avec l'agent.

    Args:
        limit: Nombre maximal de conversations à retourner (défaut: 10, max: 100)

    Returns:
        Liste des dernières conversations avec question, answer, sources, created_at
    """
    conversations = get_conversations(limit=limit)
    return [
        {
            "question": c.get("question"),
            "answer": c.get("answer"),
            "sources": c.get("sources"),
            "created_at": c.get("created_at"),
        }
        for c in conversations
    ]


@mcp.tool(
    description="Statistiques sur les données météo enregistrées en base SQLite. "
                "Retourne le nombre de prévisions, lieux distincts et température moyenne.",
    annotations={
        "audience": ["user", "assistant"],
        "priority": 0.3,
    }
)
def get_weather_stats() -> dict:
    """Statistiques sur les données météo enregistrées en base.

    Returns:
        Dict avec total_previsions, lieux_distincts, temperature_moyenne_c
    """
    rows = get_all_weather()
    if not rows:
        return {
            "total_previsions": 0,
            "lieux_distincts": 0,
            "temperature_moyenne_c": None,
            "message": "Aucune donnée météo en base.",
        }

    temps = [r["temperature_2m"] for r in rows if r.get("temperature_2m") is not None]
    lieux = {(r["latitude"], r["longitude"]) for r in rows}

    return {
        "total_previsions": len(rows),
        "lieux_distincts": len(lieux),
        "temperature_moyenne_c": round(sum(temps) / len(temps), 1) if temps else None,
    }


def main() -> None:
    """Point d'entrée : lance le serveur MCP en transport stdio (Claude Desktop)."""
    import sys
    print("Serveur MCP SKAPA démarré (stdio). En attente de connexion...", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # Lancer avec : python -m app.mcp.server (depuis la racine du projet)
    main()
