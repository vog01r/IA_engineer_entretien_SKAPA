"""Tools pour l'agent météo : géocodage, météo, tendances, alertes."""

import json
from urllib.parse import quote

import requests

from app.db.crud import get_alert, insert_weather, upsert_alert

OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

_STOPWORDS = {"météo", "temps", "quel", "quelle", "quelles", "à", "dans", "pour", "fait", "il", "et", "le", "la", "les", "des", "un", "une", "de", "du"}
_NON_PLACE = {"hello", "salut", "coucou", "ok", "oui", "non", "merci", "bonjour", "aurevoir", "hi", "hey"}

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


def _wmo_to_label(code: int | None) -> str:
    if code is None:
        return "conditions variables"
    return WMO_WEATHER_LABELS.get(code, "conditions variables")


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
    """Récupère la météo actuelle et les prévisions pour un lieu ou des coordonnées."""
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

    url = (
        f"{OPEN_METEO_FORECAST}?"
        f"latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code"
        "&hourly=temperature_2m&forecast_days=1"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": f"Erreur météo: {e}"}

    current = data.get("current") or {}
    temp = current.get("temperature_2m")
    code = current.get("weather_code")
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []

    forecast_hours = []
    for i in range(min(6, len(times))):
        if i < len(temps) and temps[i] is not None:
            t_str = times[i][11:16] if len(times[i]) >= 16 else times[i]
            forecast_hours.append({"time": t_str, "temp": temps[i]})

    return {
        "location": label,
        "current_temp": temp,
        "weather_label": _wmo_to_label(code),
        "forecast_next_hours": forecast_hours,
    }


def get_weather_trend(place: str, days: int = 7) -> dict:
    """Récupère la tendance des températures sur N jours pour un lieu."""
    if days < 1 or days > 16:
        days = 7

    geo = geocode(place)
    if "error" in geo:
        return geo

    lat, lon, label = geo["latitude"], geo["longitude"], geo["label"]

    url = (
        f"{OPEN_METEO_FORECAST}?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m&forecast_days={days}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": f"Erreur météo: {e}"}

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []

    for i, time_str in enumerate(times):
        temp = temps[i] if i < len(temps) else None
        insert_weather(lat, lon, time_str, temp)

    daily_data = {}
    for i, time_str in enumerate(times):
        if i >= len(temps):
            break
        date_part = time_str[:10] if len(time_str) >= 10 else time_str
        if date_part not in daily_data:
            daily_data[date_part] = []
        if temps[i] is not None:
            daily_data[date_part].append(temps[i])

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
        else:
            result = {"error": f"Tool inconnu: {name}"}
    except Exception as e:
        result = {"error": str(e)}
    return json.dumps(result, ensure_ascii=False)
