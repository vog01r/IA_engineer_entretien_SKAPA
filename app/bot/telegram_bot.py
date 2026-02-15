"""Bot Telegram SKAPA : météo et agent IA.

Lancement : python -m app.bot.telegram_bot (depuis la racine, venv activé)
"""
import asyncio
import logging
import os
import re
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.db.crud import create_tables, delete_alert, get_alert, get_all_alerts, upsert_alert

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")

# Seuils alerte : canicule >= 35°C, froid extrême <= -5°C (Météo France)
ALERT_TEMP_HIGH = 35
ALERT_TEMP_LOW = -5

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


# Mots à ignorer pour extraire un lieu (requêtes météo en français)
_STOPWORDS = {"météo", "temps", "quel", "quelle", "quelle", "à", "dans", "pour", "fait", "il", "et", "le", "la", "les", "des", "un", "une", "de", "du"}
# Mots qui ne sont jamais des lieux → pas de géocodage
_NON_PLACE = {"hello", "salut", "coucou", "ok", "oui", "non", "merci", "bonjour", "aurevoir", "hi", "hey"}


def _extract_place_query(text: str) -> str:
    """Extrait une chaîne searchable pour le géocodage (ex: 'météo Paris' → 'Paris')."""
    text = text.strip()
    if len(text) < 2:
        return ""
    words = [w.strip("?,.") for w in text.lower().split() if w.strip("?,.")]
    # Chercher le dernier mot significatif (probablement le lieu)
    for w in reversed(words):
        if w not in _STOPWORDS and len(w) >= 2:
            return w.capitalize()
    return text


def _geocode_sync(query: str) -> tuple[float, float, str] | None:
    """Géocode un lieu via Open-Meteo. Retourne (lat, lon, nom_affiché) ou None."""
    if len(query) < 2:
        return None
    url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        f"name={quote(query)}&count=1&language=fr"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return None
    results = data.get("results") or []
    if not results:
        return None
    r = results[0]
    lat = r.get("latitude")
    lon = r.get("longitude")
    name = r.get("name", query)
    country = r.get("country", "")
    label = f"{name}, {country}" if country else name
    if lat is not None and lon is not None:
        return (float(lat), float(lon), label)
    return None


async def geocode_place(text: str) -> tuple[float, float, str] | None:
    """Géocode un lieu (non bloquant). Toute ville ou pays au monde."""
    text = text.strip()
    if len(text) < 2:
        return None
    if text.lower() in _NON_PLACE:
        return None
    # Requêtes : texte complet d'abord (New York, Paris), puis extrait (météo Paris → Paris)
    place_query = _extract_place_query(text)
    queries = []
    if len(text) <= 35 and "?" not in text:
        queries.append(text)
    if place_query and place_query not in queries and place_query.lower() not in _NON_PLACE:
        queries.append(place_query)
    for q in queries:
        if len(q) >= 2:
            result = await asyncio.to_thread(_geocode_sync, q)
            if result:
                return result
    return None


async def start(update: Update, context) -> None:
    """Handler /start - message de bienvenue."""
    welcome = """
🌤️ Bot Météo SKAPA

• /meteo — Météo d'une ville.
• /alertes — Alertes (on [ville] | off | status).
• Pose une question — Météo, tendances, alertes personnalisées en langage naturel.
• /help — Aide.
"""
    await update.message.reply_text(welcome)


async def meteo_command(update: Update, context) -> None:
    """Handler /meteo [ville] — météo directe avec boutons."""
    args = context.args or []
    place = " ".join(args).strip()
    if not place:
        await update.message.reply_text("Écris la ville dont tu veux la météo.")
        return
    await update.effective_chat.send_chat_action(ChatAction.TYPING)
    geo = await geocode_place(place)
    if not geo:
        await update.message.reply_text(f"❌ Lieu « {place} » introuvable.")
        return
    lat, lon, label = geo
    try:
        weather = await fetch_weather_api(lat, lon)
        msg = _format_weather_msg(weather, label)
        await update.message.reply_text(msg, reply_markup=_weather_inline_keyboard())
    except requests.RequestException as e:
        logger.exception("Erreur Open-Meteo")
        await update.message.reply_text(f"❌ Erreur météo : {e}")


async def help_command(update: Update, context) -> None:
    """Handler /help."""
    help_text = """
📖 Aide

• Météo : /meteo [ville] ou "Quel temps à Paris ?"
• Tendances : "Montre-moi la tendance sur 7 jours à Lyon"
• Alertes : /alertes on [ville] ou "Préviens-moi si < 0°C à Paris"
• L'API doit tourner pour que l'agent réponde
"""
    await update.message.reply_text(help_text)


async def alertes_command(update: Update, context) -> None:
    """Handler /alertes on [lieu] | off | status."""
    chat_id = update.effective_chat.id
    args = (context.args or [])
    sub = " ".join(args).strip().lower() if args else ""

    if sub == "off":
        delete_alert(chat_id)
        await update.message.reply_text("🔕 Alertes désactivées.")
        return

    if sub in ("", "status"):
        alert = get_alert(chat_id)
        if alert:
            extra = []
            if alert.get("temp_min") is not None:
                extra.append(f"froid < {alert['temp_min']}°C")
            if alert.get("temp_max") is not None:
                extra.append(f"chaleur > {alert['temp_max']}°C")
            suffix = f" ({', '.join(extra)})" if extra else " (défaut 35°C/-5°C)"
            await update.message.reply_text(f"📍 Alerte active : {alert['label']}{suffix}")
        else:
            await update.message.reply_text("Aucune alerte. Tape /alertes on [ville] pour t'abonner.")
        return

    # /alertes on [ville] — toute ville du monde via géocodage
    if sub.startswith("on "):
        place = sub[3:].strip()
    elif sub != "on":
        place = sub
    else:
        place = ""
    if not place:
        await update.message.reply_text("Usage : /alertes on [ville] — ex: /alertes on Tokyo")
        return

    geo = await geocode_place(place)
    if not geo:
        await update.message.reply_text(f"❌ Lieu « {place} » introuvable.")
        return
    lat, lon, label = geo
    upsert_alert(chat_id, lat, lon, label)
    await update.message.reply_text(f"🔔 Alertes activées pour {label} (canicule >35°C, froid <-5°C)")

    # Vérification immédiate : envoie l'alerte si conditions extrêmes maintenant
    try:
        weather = await fetch_weather_api(lat, lon)
        temp = (weather.get("current") or {}).get("temperature_2m")
        if temp is not None:
            if temp >= ALERT_TEMP_HIGH:
                await update.message.reply_text(f"⚠️ Canicule à {label} : {temp:.0f}°C !")
            elif temp <= ALERT_TEMP_LOW:
                await update.message.reply_text(f"⚠️ Froid extrême à {label} : {temp:.0f}°C !")
    except Exception as e:
        logger.warning("Vérification immédiate alerte: %s", e)


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


def _ask_agent_sync(question: str, chat_id: int | None = None) -> str:
    """Appelle l'agent via API backend (synchrone)."""
    url = f"{API_BASE_URL.rstrip('/')}/agent/ask"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"question": question}
    if chat_id is not None:
        payload["chat_id"] = chat_id
    response = requests.post(
        url, json=payload, headers=headers, timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return data.get("answer", "Pas de réponse")


async def ask_agent_api(question: str, chat_id: int | None = None) -> str:
    """Appelle l'agent via API backend (non bloquant)."""
    return await asyncio.to_thread(_ask_agent_sync, question, chat_id)


def _weather_inline_keyboard() -> InlineKeyboardMarkup:
    """Boutons après une réponse météo."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📍 Autre ville", callback_data="autre_ville"),
            InlineKeyboardButton("🔔 Activer les alertes", callback_data="activer_alertes"),
        ],
    ])


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
    """Handler : tous les messages passent par l'agent IA avec tools météo."""
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Envoie une ville, une question météo ou une demande d'alerte.")
        return

    chat_id = update.effective_chat.id
    await update.effective_chat.send_chat_action(ChatAction.TYPING)
    try:
        answer = await ask_agent_api(text, chat_id=chat_id)
        await update.message.reply_text(f"🤖 {answer}")
    except requests.RequestException as e:
        logger.warning("Erreur API agent: %s", e)
        await update.message.reply_text(
            f"❌ Erreur agent : {e}. Vérifie que l'API tourne sur {API_BASE_URL}"
        )
    except Exception as e:
        logger.exception("Erreur inattendue agent")
        await update.message.reply_text(f"❌ Erreur : {e}")


async def callback_buttons(update: Update, context) -> None:
    """Handler pour boutons inline après météo."""
    query = update.callback_query
    await query.answer()
    if query.data == "autre_ville":
        await query.message.reply_text("Écris la ville dont tu veux la météo 😊")
    elif query.data == "activer_alertes":
        await query.message.reply_text("Pour activer : /alertes on [ville] — ex: /alertes on Paris")


async def _run_alert_checks(app: Application) -> None:
    """Vérifie les alertes toutes les heures. Seuils personnalisés ou par défaut."""
    interval = int(os.getenv("ALERT_CHECK_INTERVAL_SEC", "3600"))  # 1h par défaut
    while True:
        await asyncio.sleep(interval)
        alerts = get_all_alerts()
        for row in alerts:
            try:
                weather = await fetch_weather_api(row["latitude"], row["longitude"])
                temp = (weather.get("current") or {}).get("temperature_2m")
                if temp is None:
                    continue

                temp_max = row.get("temp_max")
                temp_min = row.get("temp_min")
                if temp_max is None:
                    temp_max = ALERT_TEMP_HIGH
                if temp_min is None:
                    temp_min = ALERT_TEMP_LOW

                if temp >= temp_max:
                    await app.bot.send_message(
                        row["chat_id"],
                        f"⚠️ Alerte chaleur à {row['label']} : {temp:.0f}°C (seuil {temp_max}°C) !",
                    )
                elif temp <= temp_min:
                    await app.bot.send_message(
                        row["chat_id"],
                        f"⚠️ Alerte froid à {row['label']} : {temp:.0f}°C (seuil {temp_min}°C) !",
                    )
            except Exception as e:
                logger.warning("Erreur alerte pour chat_id=%s: %s", row["chat_id"], e)


def main() -> None:
    """Lance le bot en mode polling."""
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN manquant dans .env")
    create_tables()

    async def post_init(app: Application):
        await app.bot.set_my_commands([
            BotCommand("start", "Démarrer le bot"),
            BotCommand("meteo", "Météo d'une ville"),
            BotCommand("help", "Aide"),
            BotCommand("alertes", "Alertes canicule/froid (on [ville] | off)"),
        ])
        asyncio.create_task(_run_alert_checks(app))

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("meteo", meteo_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("alertes", alertes_command))
    app.add_handler(CallbackQueryHandler(callback_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot Telegram démarré (polling mode)")
    app.run_polling()


if __name__ == "__main__":
    main()
