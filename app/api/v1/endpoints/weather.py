import requests
from fastapi import APIRouter, HTTPException

from app.db.crud import (
    get_all_weather,
    get_weather_by_date_range,
    get_weather_by_location,
    insert_weather,
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_BASE = OPEN_METEO_URL

router = APIRouter()


@router.get("/fetch")
def fetch_weather(latitude: float = 43.6599, longitude: float = 1.3623):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
    }
    try:
        r = requests.get(_BASE, params=params, timeout=15)
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

    return {
        "message": "Data stored successfully",
        "latitude": latitude,
        "longitude": longitude,
        "stored": stored,
    }


@router.get("/")
def list_weather():
    return {"weather": get_all_weather()}


@router.get("/location")
def list_weather_by_location(latitude: float, longitude: float):
    return {"weather": get_weather_by_location(latitude, longitude)}


@router.get("/range")
def list_weather_by_range(start_date: str, end_date: str):
    return {"weather": get_weather_by_date_range(start_date, end_date)}
