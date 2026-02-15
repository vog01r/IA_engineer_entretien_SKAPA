"""Agent IA avec tools météo — géocodage, météo temps réel, tendances, alertes."""

import json

from openai import OpenAI

from app.agent.tools import OPENAI_TOOLS_DEFINITION, execute_tool


class Agent:
    """Agent conversationnel météo avec function calling (geocode, météo, tendances, alertes)."""

    def __init__(self, model: str, api_key: str, provider: str = "openai"):
        self.model = model
        self.api_key = api_key
        self.provider = provider

        if provider == "openai":
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Provider non supporté: {provider}. Utiliser 'openai'.")

        self.system_prompt = """Tu es un assistant météo conversationnel connecté à Telegram. Tu disposes d'outils pour :
- géocoder un lieu (ville, pays dans le monde)
- obtenir la météo actuelle et les prévisions
- afficher la tendance des températures sur plusieurs jours
- configurer des alertes personnalisées (seuils temp_min, temp_max)
- lister les alertes de l'utilisateur
- gérer les préférences (ville préférée, unités celsius/fahrenheit)

RÈGLES :
1. Dès qu'un lieu est mentionné, appelle get_weather ou get_weather_trend immédiatement. Ne demande jamais de confirmation.
2. Utilise les outils pour répondre (ex: "Quel temps à Tokyo ?" → get_weather directement)
3. Si l'utilisateur demande la météo sans préciser de lieu, demande-le ou utilise get_my_preferences (Telegram)
4. Pour les tendances : "Montre-moi la tendance sur 7 jours à Lyon" → get_weather_trend
5. Pour les alertes : "Préviens-moi si < 0°C à Paris" → set_alert avec temp_min=0
6. Réponds en langage naturel, de façon concise et utile
7. Si un lieu est introuvable, dis-le clairement
"""

    def ask(self, question: str, chat_id: int | None = None) -> str:
        """Pose une question à l'agent avec boucle tool calling."""
        user_content = question
        if chat_id is None:
            user_content = (
                "[Contexte web, pas de chat_id. N'utilise QUE get_weather et get_weather_trend.]\n"
                "IMPORTANT: Dès qu'un lieu est mentionné (Paris, Lyon, Tokyo...), appelle get_weather ou get_weather_trend IMMÉDIATEMENT. "
                "Ne demande JAMAIS de confirmation du lieu. Ne demande le lieu que s'il est vraiment absent (ex: 'quel temps fait-il ?').\n\n"
                + question
            )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        max_iterations = 5

        try:
            for _ in range(max_iterations):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=OPENAI_TOOLS_DEFINITION,
                    tool_choice="auto",
                    temperature=0.1,
                )

                choice = response.choices[0]
                message = choice.message

                if choice.finish_reason == "stop":
                    return message.content or "Pas de réponse générée."

                if choice.finish_reason == "tool_calls" and message.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                            }
                            for tc in message.tool_calls
                        ],
                    })

                    for tc in message.tool_calls:
                        name = tc.function.name
                        try:
                            args = json.loads(tc.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                        result = execute_tool(name, args, chat_id=chat_id)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })

                    continue

                return message.content or "Pas de réponse générée."

            return "Limite d'itérations atteinte. Réessaie avec une question plus simple."

        except Exception as e:
            return f"Erreur lors du traitement : {str(e)}"
