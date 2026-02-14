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

        # System prompt basique (à améliorer au commit 2)
        self.system_prompt = (
            "Tu es un assistant météo. "
            "Réponds aux questions en te basant sur le contexte fourni par l'utilisateur."
        )

    def ask(self, question: str) -> str:
        """Pose une question à l'agent avec injection du contexte RAG."""
        # Récupérer le contexte depuis la base
        context_chunks = search_chunks(question)
        context = "\n---\n".join([c["content"] for c in context_chunks])

        # Injecter le contexte dans les messages (fix QCM Q3.1)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Contexte:\n{context}\n\nQuestion: {question}"},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,  # À modifier à 0.1 au commit 3
        )

        return response.choices[0].message.content or ""
