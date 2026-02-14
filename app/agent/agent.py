"""Agent IA avec RAG — injection contexte depuis base de connaissances."""

from openai import OpenAI

from app.db.crud import search_chunks


class Agent:
    """Agent conversationnel météo utilisant RAG pour enrichir les réponses."""

    def __init__(self, model: str, api_key: str, provider: str = "openai"):
        self.model = model
        self.api_key = api_key
        self.provider = provider

        if provider == "openai":
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Provider non supporté: {provider}. Utiliser 'openai'.")

        # System prompt structuré (commit 2/4)
        self.system_prompt = """Tu es un assistant de question-réponse basé sur une base de connaissances météo.

RÈGLES STRICTES :
1. Utilise UNIQUEMENT les informations présentes dans le contexte fourni
2. Si l'information n'est pas dans le contexte, réponds : "Je ne dispose pas de cette information dans ma base de connaissances"
3. Cite toujours le document source quand tu utilises une information
4. Ne fais pas d'hypothèses ou d'extrapolations au-delà du contexte

FORMAT DE RÉPONSE :
- Réponds de manière concise et factuelle
- Structure : réponse directe + source si applicable
- Exemple : "D'après le guide météo, la température moyenne en hiver est de 5°C."
"""

    def ask(self, question: str) -> str:
        """Pose une question à l'agent avec injection du contexte RAG."""
        try:
            # Récupérer le contexte depuis la base
            context_chunks = search_chunks(question)

            # Gérer le cas où aucun contexte n'est trouvé
            if not context_chunks:
                return "Aucun contexte pertinent trouvé pour répondre à cette question."

            context = "\n---\n".join([c["content"] for c in context_chunks])

            # Injecter le contexte dans les messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Contexte:\n{context}\n\nQuestion: {question}"},
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Bas pour Q&A factuel (cohérence, précision)
            )

            return response.choices[0].message.content or "Pas de réponse générée."

        except Exception as e:
            return f"Erreur lors du traitement de la question : {str(e)}"
