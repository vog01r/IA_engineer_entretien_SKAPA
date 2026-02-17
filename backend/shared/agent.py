"""Agent IA simple pour répondre aux questions météo.

TODO: Implémenter l'agent complet avec RAG + LLM.
Pour l'instant, retourne un message mock pour les tests.
"""
import os
from typing import Optional


class Agent:
    """Agent IA simple (mock pour tests)."""

    def __init__(self, model: str, api_key: str, provider: str = "openai"):
        self.model = model
        self.api_key = api_key
        self.provider = provider

    def ask(self, question: str, chat_id: Optional[int] = None) -> str:
        """Répond à une question (mock pour tests).
        
        TODO: Implémenter avec OpenAI/Claude + RAG + tools météo.
        """
        # Mock response pour les tests
        if "météo" in question.lower() or "temps" in question.lower():
            return f"[MOCK] Réponse météo pour: {question}"
        return f"[MOCK] Réponse générale pour: {question}"
