"""Bot Telegram SKAPA : météo et agent IA.

Lancement : python -m app.bot.telegram_bot (depuis la racine, venv activé)
"""
import asyncio
import logging
import os
import re

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")

# Mapping WMO weather code → libellé français (aligné avec weather.py)
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
    """Convertit un code WMO en libellé français."""
    if code is None:
        return "conditions variables"
    return WMO_WEATHER_LABELS.get(code, "conditions variables")


async def start(update: Update, context) -> None:
    """Handler /start - message de bienvenue."""
    welcome = """
🌤️ Bot Météo SKAPA

Commandes :
• Envoyez des coordonnées (ex: 48.8, 2.3) pour la météo
• Posez une question générale et je consulterai l'agent IA
• /help pour plus d'infos
"""
    await update.message.reply_text(welcome)


async def help_command(update: Update, context) -> None:
    """Handler /help."""
    help_text = """
📖 Aide

• Météo : envoyez lat,lon (ex: 48.8566, 2.3522 pour Paris)
• Questions : posez une question sur la météo ou les villes — l'agent IA répond avec la base de connaissances
• L'API backend (FastAPI) doit tourner sur 127.0.0.1:8000 pour les questions IA
"""
    await update.message.reply_text(help_text)


def is_coordinates(text: str) -> tuple[float, float] | None:
    """Détecte si le texte contient des coordonnées lat,lon valides."""
    pattern = r"(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)"
    match = re.search(pattern, text)
    if match:
        try:
            lat, lon = float(match.group(1)), float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        except ValueError:
            pass
    return None


def _fetch_weather_sync(lat: float, lon: float) -> dict:
    """Appelle Open-Meteo (synchrone, exécutée dans un thread)."""
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code"
        "&hourly=temperature_2m&forecast_days=1"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


async def fetch_weather_api(lat: float, lon: float) -> dict:
    """Appelle Open-Meteo (non bloquant via thread pool)."""
    return await asyncio.to_thread(_fetch_weather_sync, lat, lon)


def _ask_agent_sync(question: str) -> str:
    """Appelle l'agent via API backend (synchrone)."""
    url = f"{API_BASE_URL.rstrip('/')}/agent/ask"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(
        url, json={"question": question}, headers=headers, timeout=15
    )
    response.raise_for_status()
    data = response.json()
    return data.get("answer", "Pas de réponse")


async def ask_agent_api(question: str) -> str:
    """Appelle l'agent via API backend (non bloquant)."""
    return await asyncio.to_thread(_ask_agent_sync, question)


async def handle_message(update: Update, context) -> None:
    """Handler pour messages texte : coordonnées → météo, sinon → agent IA."""
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Envoie des coordonnées (ex: 48.8, 2.3) ou une question.")
        return

    coords = is_coordinates(text)
    if coords:
        lat, lon = coords
        try:
            weather = await fetch_weather_api(lat, lon)
            current = weather.get("current") or {}
            temp = current.get("temperature_2m")
            code = current.get("weather_code")
            label = _wmo_to_label(code)
            temp_str = f"{temp}°C" if temp is not None else "—"
            msg = f"🌡️ Météo pour {lat}, {lon} : {temp_str}, {label}"
            await update.message.reply_text(msg)
        except requests.RequestException as e:
            logger.exception("Erreur Open-Meteo")
            await update.message.reply_text(f"❌ Erreur météo : {e}")
        except Exception as e:
            logger.exception("Erreur inattendue météo")
            await update.message.reply_text(f"❌ Erreur : {e}")
    else:
        try:
            answer = await ask_agent_api(text)
            await update.message.reply_text(f"🤖 {answer}")
        except requests.RequestException as e:
            logger.warning("Erreur API agent: %s", e)
            await update.message.reply_text(
                f"❌ Erreur agent : {e}. Vérifie que l'API tourne sur {API_BASE_URL}"
            )
        except Exception as e:
            logger.exception("Erreur inattendue agent")
            await update.message.reply_text(f"❌ Erreur : {e}")


def main() -> None:
    """Lance le bot en mode polling."""
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN manquant dans .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot Telegram démarré (polling mode)")
    app.run_polling()


if __name__ == "__main__":
    main()
