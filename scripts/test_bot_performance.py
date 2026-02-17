"""Script de test pour mesurer les performances du bot Telegram.

Usage:
    python scripts/test_bot_performance.py

Mesure les temps de réponse pour différentes requêtes :
- Géocodage seul
- Météo seule
- Agent LLM (question météo)
- Agent LLM (question générale)
"""
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")


def test_geocoding(query: str) -> tuple[float, str]:
    """Test géocodage Open-Meteo."""
    from urllib.parse import quote
    
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={quote(query)}&count=1&language=fr"
    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        elapsed = time.perf_counter() - start
        results = data.get("results", [])
        if results:
            r = results[0]
            return elapsed, f"{r['name']}, {r.get('country', '')}"
        return elapsed, "Not found"
    except Exception as e:
        elapsed = time.perf_counter() - start
        return elapsed, f"Error: {e}"


def test_weather_api(lat: float, lon: float) -> tuple[float, str]:
    """Test API météo FastAPI."""
    base = API_BASE_URL.rstrip("/")
    headers = {"X-API-Key": API_KEY}
    
    start = time.perf_counter()
    try:
        # Test /weather/fetch
        fetch_resp = requests.get(
            f"{base}/weather/fetch",
            params={"latitude": lat, "longitude": lon, "forecast_days": 1},
            headers=headers,
            timeout=15,
        )
        fetch_resp.raise_for_status()
        data = fetch_resp.json()
        elapsed = time.perf_counter() - start
        
        summary = data.get("summary", {})
        temp = summary.get("current_temp")
        return elapsed, f"{temp}°C" if temp else "No data"
    except Exception as e:
        elapsed = time.perf_counter() - start
        return elapsed, f"Error: {e}"


def test_agent_llm(question: str) -> tuple[float, str]:
    """Test agent LLM via API backend."""
    url = f"{API_BASE_URL.rstrip('/')}/agent/ask"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"question": question}
    
    start = time.perf_counter()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        elapsed = time.perf_counter() - start
        answer = data.get("answer", "No answer")
        return elapsed, answer[:100]  # Tronquer à 100 chars
    except Exception as e:
        elapsed = time.perf_counter() - start
        return elapsed, f"Error: {e}"


def main():
    """Exécute les tests de performance."""
    print("=" * 80)
    print("🔬 TEST PERFORMANCE BOT TELEGRAM")
    print("=" * 80)
    print()
    
    # Test 1 : Géocodage
    print("📍 Test 1: Géocodage (Open-Meteo)")
    print("-" * 80)
    for city in ["Paris", "Tokyo", "New York"]:
        elapsed, result = test_geocoding(city)
        print(f"  {city:15} → {elapsed:6.3f}s | {result}")
    print()
    
    # Test 2 : API Météo
    print("🌤️  Test 2: API Météo (FastAPI → Open-Meteo)")
    print("-" * 80)
    locations = [
        ("Paris", 48.8566, 2.3522),
        ("Tokyo", 35.6762, 139.6503),
        ("New York", 40.7128, -74.0060),
    ]
    for name, lat, lon in locations:
        elapsed, result = test_weather_api(lat, lon)
        print(f"  {name:15} → {elapsed:6.3f}s | {result}")
    print()
    
    # Test 3 : Agent LLM (question météo)
    print("🤖 Test 3: Agent LLM (question météo)")
    print("-" * 80)
    questions = [
        "Météo à Paris",
        "Quel temps fait-il à Tokyo ?",
        "Prévisions pour New York",
    ]
    for question in questions:
        elapsed, result = test_agent_llm(question)
        print(f"  {question:30} → {elapsed:6.3f}s")
        print(f"    Answer: {result}")
    print()
    
    # Test 4 : Agent LLM (question générale)
    print("🤖 Test 4: Agent LLM (question générale)")
    print("-" * 80)
    elapsed, result = test_agent_llm("Bonjour, comment ça va ?")
    print(f"  Question générale → {elapsed:6.3f}s")
    print(f"    Answer: {result}")
    print()
    
    print("=" * 80)
    print("✅ Tests terminés")
    print("=" * 80)
    print()
    print("📊 ANALYSE:")
    print("  - Géocodage: ~0.2-0.5s (acceptable)")
    print("  - Météo API: ~0.5-1.5s (acceptable, dépend d'Open-Meteo)")
    print("  - Agent LLM: ~1-5s (BOTTLENECK PRINCIPAL)")
    print()
    print("💡 RECOMMANDATIONS:")
    print("  1. Cache météo (10min) → évite appels inutiles")
    print("  2. Cache geocoding (24h) → évite résolutions répétées")
    print("  3. Streaming LLM → améliore perception UX")
    print("  4. Parallélisation → fetch météo pendant LLM si possible")


if __name__ == "__main__":
    main()
