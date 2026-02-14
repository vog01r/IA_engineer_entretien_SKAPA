"""
Serveur MCP (Model Context Protocol) — SKAPA

Expose 3 tools connectables depuis Claude Desktop ou un client MCP :
- get_weather : prévisions météo via Open-Meteo
- search_knowledge : recherche dans la base de connaissances
- conversation_history : historique des conversations agent

Transport : stdio (Claude Desktop)
Référence : https://modelcontextprotocol.io/docs
SDK : https://github.com/modelcontextprotocol/python-sdk
"""

import requests
from pydantic import BaseModel, Field
from requests.exceptions import RequestException
from mcp.server.fastmcp import FastMCP

from app.db.crud import get_conversations, search_chunks


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
    instructions="Serveur MCP pour l'application SKAPA : météo, base de connaissances et historique des conversations.",
)


@mcp.tool()
def get_weather(latitude: float, longitude: float) -> WeatherResponse | dict:
    """Récupère les prévisions météo pour des coordonnées GPS.

    Args:
        latitude: Latitude (-90 à 90)
        longitude: Longitude (-180 à 180)

    Returns:
        WeatherResponse ou dict avec error=True en cas d'échec
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


@mcp.tool()
def search_knowledge(query: str, limit: int = 5) -> list[dict]:
    """Recherche dans la base de connaissances de l'agent.

    Args:
        query: Requête de recherche (mots-clés ou phrase)
        limit: Nombre maximal de chunks à retourner (défaut: 5)

    Returns:
        Liste de chunks pertinents (source_file, content, chunk_index)
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


@mcp.tool()
def conversation_history(limit: int = 10) -> list[dict]:
    """Récupère l'historique des conversations avec l'agent.

    Args:
        limit: Nombre maximal de conversations à retourner (défaut: 10)

    Returns:
        Liste des dernières conversations (question, answer, created_at)
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


def main() -> None:
    """Point d'entrée : lance le serveur MCP en transport stdio (Claude Desktop)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
