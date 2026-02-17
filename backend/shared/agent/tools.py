"""Tools pour l'agent météo : géocodage, météo, tendances, alertes.

Architecture : l'agent passe par l'API FastAPI pour la météo (/weather/fetch, /location, /range).
Géocodage reste direct (Open-Meteo Geocoding) — non exposé par l'API.
"""

import json
from datetime import datetime, timedelta
from urllib.parse import quote

import requests

from backend.shared.config import API_BASE_URL, API_KEY
from backend.shared.db.crud import get_alert, get_preferences, upsert_alert, upsert_preferences

OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

_STOPWORDS = {"météo", "temps", "quel", "quelle", "quelles", "à", "dans", "pour", "fait", "il", "et", "le", "la", "les", "des", "un", "une", "de", "du"}
_NON_PLACE = {"hello", "salut", "coucou", "ok", "oui", "non", "merci", "bonjour", "aurevoir", "hi", "hey"}


def _call_weather_api(path: str, params: dict) -> dict | None:
    """Appelle l'API FastAPI weather. Retourne le JSON ou None en cas d'erreur."""
    if not API_KEY:
        return {"error": "API_KEY non configurée — impossible d'appeler l'API météo"}
    url = f"{API_BASE_URL}/weather{path}"
    headers = {"X-API-Key": API_KEY}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"Erreur API météo: {e}"}


def _extract_place_query(text: str) -> str:
    """Extrait une chaîne searchable pour le géocodage."""
    text = text.strip()
    if len(text) < 2:
        return ""
    words = [w.strip("?,.") for w in text.lower().split() if w.strip("?,.")]
    for w in reversed(words):
        if w not in _STOPWORDS and len(w) >= 2:
            return w.capitalize()
    return text


def geocode(place: str) -> dict:
    """Géocode un lieu via Open-Meteo. Retourne lat, lon, label ou erreur."""
    place = place.strip()
    if len(place) < 2:
        return {"error": "Lieu trop court"}
    if place.lower() in _NON_PLACE:
        return {"error": "Ce n'est pas un nom de lieu"}

    queries = []
    if len(place) <= 35 and "?" not in place:
        queries.append(place)
    place_query = _extract_place_query(place)
    if place_query and place_query not in queries and place_query.lower() not in _NON_PLACE:
        queries.append(place_query)

    for q in queries:
        if len(q) < 2:
            continue
        url = f"{OPEN_METEO_GEOCODING}?name={quote(q)}&count=1&language=fr"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            return {"error": f"Erreur géocodage: {e}"}

        results = data.get("results") or []
        if not results:
            continue

        r = results[0]
        lat = r.get("latitude")
        lon = r.get("longitude")
        name = r.get("name", q)
        country = r.get("country", "")
        label = f"{name}, {country}" if country else name
        if lat is not None and lon is not None:
            return {"latitude": float(lat), "longitude": float(lon), "label": label}

    return {"error": f"Lieu « {place} » introuvable"}


def get_weather(place: str | None = None, latitude: float | None = None, longitude: float | None = None) -> dict:
    """Récupère la météo actuelle et les prévisions via l'API FastAPI (/weather/fetch, /location)."""
    lat, lon, label = None, None, None

    if place:
        geo = geocode(place)
        if "error" in geo:
            return geo
        lat, lon, label = geo["latitude"], geo["longitude"], geo["label"]
    elif latitude is not None and longitude is not None:
        lat, lon = latitude, longitude
        label = f"{lat}, {lon}"
    else:
        return {"error": "Indiquez un lieu (place) ou des coordonnées (latitude, longitude)"}

    fetch_res = _call_weather_api("/fetch", {"latitude": lat, "longitude": lon, "forecast_days": 1})
    if "error" in fetch_res:
        return fetch_res

    loc_res = _call_weather_api("/location", {"latitude": lat, "longitude": lon})
    if "error" in loc_res:
        return loc_res

    summary = fetch_res.get("summary") or {}
    weather_rows = loc_res.get("weather") or []
    # Garder uniquement les heures >= maintenant (évite 00:00-05:00 quand il est 19h)
    now_utc = datetime.utcnow()
    threshold = now_utc.strftime("%Y-%m-%dT%H")
    forecast_hours = []
    for row in weather_rows:
        if len(forecast_hours) >= 6:
            break
        time_str = row.get("time", "")
        if time_str < threshold:
            continue
        t = row.get("temperature_2m")
        if t is not None:
            t_str = time_str[11:16] if len(time_str) >= 16 else time_str
            forecast_hours.append({"time": t_str, "temp": t})

    return {
        "location": label,
        "current_temp": summary.get("current_temp"),
        "weather_label": summary.get("weather_label", "conditions variables"),
        "forecast_next_hours": forecast_hours,
    }


def get_weather_trend(place: str, days: int = 7) -> dict:
    """Récupère la tendance des températures sur N jours via l'API FastAPI (/weather/fetch, /location)."""
    if days < 1 or days > 16:
        days = 7

    geo = geocode(place)
    if "error" in geo:
        return geo

    lat, lon, label = geo["latitude"], geo["longitude"], geo["label"]

    fetch_res = _call_weather_api("/fetch", {"latitude": lat, "longitude": lon, "forecast_days": days})
    if "error" in fetch_res:
        return fetch_res

    loc_res = _call_weather_api("/location", {"latitude": lat, "longitude": lon})
    if "error" in loc_res:
        return loc_res

    weather_rows = loc_res.get("weather") or []
    today = datetime.utcnow().strftime("%Y-%m-%d")
    end_date = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
    daily_data = {}
    for row in weather_rows:
        time_str = row.get("time", "")
        date_part = time_str[:10] if len(time_str) >= 10 else time_str
        if today <= date_part <= end_date:
            t = row.get("temperature_2m")
            if t is not None:
                daily_data.setdefault(date_part, []).append(t)

    daily_summary = []
    for date_key in sorted(daily_data.keys()):
        vals = daily_data[date_key]
        if vals:
            daily_summary.append({
                "date": date_key,
                "min": round(min(vals), 1),
                "max": round(max(vals), 1),
                "avg": round(sum(vals) / len(vals), 1),
            })

    if len(daily_summary) >= 2:
        first_avg = daily_summary[0]["avg"]
        last_avg = daily_summary[-1]["avg"]
        trend = "hausse" if last_avg > first_avg else "baisse" if last_avg < first_avg else "stable"
    else:
        trend = "insuffisant"

    return {
        "location": label,
        "days": days,
        "daily_summary": daily_summary,
        "trend": trend,
    }


def set_alert(
    chat_id: int,
    place: str,
    temp_min: float | None = None,
    temp_max: float | None = None,
) -> dict:
    """Configure une alerte météo pour un lieu avec seuils optionnels."""
    geo = geocode(place)
    if "error" in geo:
        return geo

    lat, lon, label = geo["latitude"], geo["longitude"], geo["label"]
    upsert_alert(chat_id, lat, lon, label, temp_min=temp_min, temp_max=temp_max)
    return {
        "success": True,
        "location": label,
        "temp_min": temp_min,
        "temp_max": temp_max,
    }


def get_my_alerts(chat_id: int) -> dict:
    """Liste les alertes configurées pour l'utilisateur."""
    alert = get_alert(chat_id)
    if not alert:
        return {"alerts": [], "message": "Aucune alerte configurée"}
    return {
        "alerts": [{
            "location": alert["label"],
            "latitude": alert["latitude"],
            "longitude": alert["longitude"],
            "temp_min": alert.get("temp_min"),
            "temp_max": alert.get("temp_max"),
        }],
    }


def get_my_preferences(chat_id: int) -> dict:
    """Récupère les préférences utilisateur (ville préférée, unités)."""
    prefs = get_preferences(chat_id)
    if not prefs:
        return {"preferred_city": None, "units": "celsius", "message": "Aucune préférence configurée"}
    return {
        "preferred_city": prefs.get("preferred_city"),
        "units": prefs.get("units", "celsius"),
    }


def set_my_preferences(
    chat_id: int,
    preferred_city: str | None = None,
    units: str | None = None,
) -> dict:
    """Configure les préférences utilisateur (ville préférée, unités)."""
    upsert_preferences(chat_id, preferred_city=preferred_city, units=units)
    prefs = get_preferences(chat_id) or {}
    return {
        "success": True,
        "preferred_city": prefs.get("preferred_city"),
        "units": prefs.get("units", "celsius"),
    }


OPENAI_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "geocode",
            "description": "Géocode un lieu (ville, pays) et retourne latitude, longitude et nom d'affichage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "place": {"type": "string", "description": "Nom du lieu (ex: Paris, Tokyo, New York)"},
                },
                "required": ["place"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Récupère la météo actuelle et les prévisions des prochaines heures pour un lieu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "place": {"type": "string", "description": "Nom du lieu (ex: Paris, Lyon)"},
                    "latitude": {"type": "number", "description": "Latitude (si déjà géocodé)"},
                    "longitude": {"type": "number", "description": "Longitude (si déjà géocodé)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_trend",
            "description": "Récupère la tendance des températures sur plusieurs jours pour un lieu (évolution, min/max par jour).",
            "parameters": {
                "type": "object",
                "properties": {
                    "place": {"type": "string", "description": "Nom du lieu"},
                    "days": {"type": "integer", "description": "Nombre de jours (défaut 7, max 16)"},
                },
                "required": ["place"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_alert",
            "description": "Configure une alerte météo pour un lieu. Préviens si temp < temp_min ou temp > temp_max.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "integer", "description": "ID du chat Telegram"},
                    "place": {"type": "string", "description": "Nom du lieu"},
                    "temp_min": {"type": "number", "description": "Alerte si température descend sous cette valeur (°C)"},
                    "temp_max": {"type": "number", "description": "Alerte si température dépasse cette valeur (°C)"},
                },
                "required": ["chat_id", "place"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_alerts",
            "description": "Liste les alertes météo configurées par l'utilisateur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "integer", "description": "ID du chat Telegram"},
                },
                "required": ["chat_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_preferences",
            "description": "Récupère les préférences utilisateur (ville préférée, unités celsius/fahrenheit).",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "integer", "description": "ID du chat Telegram"},
                },
                "required": ["chat_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_my_preferences",
            "description": "Configure les préférences utilisateur (ville préférée, unités).",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "integer", "description": "ID du chat Telegram"},
                    "preferred_city": {"type": "string", "description": "Ville préférée par défaut"},
                    "units": {"type": "string", "description": "Unités : celsius ou fahrenheit"},
                },
                "required": ["chat_id"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict, chat_id: int | None = None) -> str:
    """Exécute un tool par son nom et retourne le résultat en JSON string."""
    try:
        if name == "geocode":
            result = geocode(arguments.get("place", ""))
        elif name == "get_weather":
            result = get_weather(
                place=arguments.get("place"),
                latitude=arguments.get("latitude"),
                longitude=arguments.get("longitude"),
            )
        elif name == "get_weather_trend":
            result = get_weather_trend(
                place=arguments.get("place", ""),
                days=arguments.get("days", 7),
            )
        elif name == "set_alert":
            if chat_id is None:
                result = {"error": "chat_id requis pour set_alert (contexte Telegram)"}
            else:
                result = set_alert(
                    chat_id=chat_id,
                    place=arguments.get("place", ""),
                    temp_min=arguments.get("temp_min"),
                    temp_max=arguments.get("temp_max"),
                )
        elif name == "get_my_alerts":
            if chat_id is None:
                result = {"error": "chat_id requis pour get_my_alerts (contexte Telegram)"}
            else:
                result = get_my_alerts(chat_id=chat_id)
        elif name == "get_my_preferences":
            if chat_id is None:
                result = {"error": "chat_id requis pour get_my_preferences (contexte Telegram)"}
            else:
                result = get_my_preferences(chat_id=chat_id)
        elif name == "set_my_preferences":
            if chat_id is None:
                result = {"error": "chat_id requis pour set_my_preferences (contexte Telegram)"}
            else:
                result = set_my_preferences(
                    chat_id=chat_id,
                    preferred_city=arguments.get("preferred_city"),
                    units=arguments.get("units"),
                )
        else:
            result = {"error": f"Tool inconnu: {name}"}
    except Exception as e:
        result = {"error": str(e)}
    return json.dumps(result, ensure_ascii=False)
