import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.db.crud import (
    get_all_weather,
    get_weather_by_date_range,
    get_weather_by_location,
    insert_weather,
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_BASE = OPEN_METEO_URL

router = APIRouter()

# Mapping WMO weather code → libellé français
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


def _wmo_to_label(code: int | None) -> str:
    if code is None:
        return "—"
    return WMO_WEATHER_LABELS.get(code, "conditions variables")


class WeatherParams(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude entre -90 et 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude entre -180 et 180")


@router.get("/fetch")
def fetch_weather(
    params: WeatherParams = Depends(),
    forecast_days: int = 1,
):
    latitude, longitude = params.latitude, params.longitude
    forecast_days = max(1, min(16, forecast_days))
    api_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "current": "temperature_2m,weather_code",
        "forecast_days": forecast_days,
    }
    try:
        r = requests.get(_BASE, params=api_params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []

    stored = 0
    for i, time_str in enumerate(times):
        temp = temps[i] if i < len(temps) else None
        insert_weather(latitude, longitude, time_str, temp)
        stored += 1

    current = data.get("current") or {}
    current_temp = current.get("temperature_2m")
    weather_code = current.get("weather_code")
    summary = {
        "current_temp": current_temp,
        "weather_label": _wmo_to_label(weather_code),
    }

    return {
        "message": "Data stored successfully",
        "latitude": latitude,
        "longitude": longitude,
        "stored": stored,
        "summary": summary,
    }


@router.get("/")
def list_weather():
    return {"weather": get_all_weather()}


@router.get("/location")
def list_weather_by_location(params: WeatherParams = Depends()):
    return {"weather": get_weather_by_location(params.latitude, params.longitude)}


@router.get("/range")
def list_weather_by_range(start_date: str, end_date: str):
    return {"weather": get_weather_by_date_range(start_date, end_date)}
