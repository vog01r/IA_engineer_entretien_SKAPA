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
from telegram.constants import ChatAction
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


# Villes connues : nom → (lat, lon) — aligné avec frontend
VILLES = {
    "paris": (48.8566, 2.3522),
    "lyon": (45.764, 4.8357),
    "marseille": (43.2965, 5.3698),
    "toulouse": (43.6047, 1.4442),
    "bordeaux": (44.8378, -0.5792),
}


def extract_city(text: str) -> tuple[float, float, str] | None:
    """Détecte un nom de ville dans le texte. Retourne (lat, lon, nom_ville) ou None."""
    text_lower = text.strip().lower()
    for nom, (lat, lon) in VILLES.items():
        if nom in text_lower:
            return (lat, lon, nom.capitalize())
    return None


async def start(update: Update, context) -> None:
    """Handler /start - message de bienvenue."""
    welcome = """
🌤️ Bot Météo SKAPA

• Météo : tapez une ville (Paris, Lyon, Marseille...) ou des coordonnées (48.8, 2.3)
• Questions : posez une question et j'interroge l'agent IA
• /help pour plus d'infos
"""
    await update.message.reply_text(welcome)


async def help_command(update: Update, context) -> None:
    """Handler /help."""
    help_text = """
📖 Aide

• Météo : nom de ville (Paris, Lyon, Marseille, Toulouse, Bordeaux) ou coordonnées lat,lon
• Questions : l'agent IA répond via la base de connaissances (API doit tourner)
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


def _format_weather_msg(weather: dict, location: str) -> str:
    """Formate la réponse météo avec température actuelle + prévisions prochaines heures."""
    current = weather.get("current") or {}
    temp = current.get("temperature_2m")
    code = current.get("weather_code")
    label = _wmo_to_label(code)
    temp_str = f"{temp}°C" if temp is not None else "—"
    lines = [f"🌡️ {location} : {temp_str}, {label}"]
    hourly = weather.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []
    if times and temps:
        # Prochaines 6 heures (ou moins)
        forecast_parts = []
        for i in range(min(6, len(times))):
            if i < len(temps) and temps[i] is not None:
                t = times[i][11:16] if len(times[i]) >= 16 else times[i]  # HH:MM
                forecast_parts.append(f"{t} → {temps[i]:.0f}°C")
        if forecast_parts:
            lines.append("📅 Prochaines h : " + " | ".join(forecast_parts[:4]))
    return "\n".join(lines)


async def handle_message(update: Update, context) -> None:
    """Handler : ville ou coordonnées → météo, sinon → agent IA."""
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Envoie une ville, des coordonnées (48.8, 2.3) ou une question.")
        return

    # 1) Ville connue → météo directe
    city_match = extract_city(text)
    if city_match:
        lat, lon, nom = city_match
        await update.effective_chat.send_chat_action(ChatAction.TYPING)
        try:
            weather = await fetch_weather_api(lat, lon)
            msg = _format_weather_msg(weather, nom)
            await update.message.reply_text(msg)
        except requests.RequestException as e:
            logger.exception("Erreur Open-Meteo")
            await update.message.reply_text(f"❌ Erreur météo : {e}")
        except Exception as e:
            logger.exception("Erreur inattendue météo")
            await update.message.reply_text(f"❌ Erreur : {e}")
        return

    # 2) Coordonnées → météo
    coords = is_coordinates(text)
    if coords:
        lat, lon = coords
        await update.effective_chat.send_chat_action(ChatAction.TYPING)
        try:
            weather = await fetch_weather_api(lat, lon)
            msg = _format_weather_msg(weather, f"{lat}, {lon}")
            await update.message.reply_text(msg)
        except requests.RequestException as e:
            logger.exception("Erreur Open-Meteo")
            await update.message.reply_text(f"❌ Erreur météo : {e}")
        except Exception as e:
            logger.exception("Erreur inattendue météo")
            await update.message.reply_text(f"❌ Erreur : {e}")
        return

    # 3) Question → agent IA
    await update.effective_chat.send_chat_action(ChatAction.TYPING)
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
