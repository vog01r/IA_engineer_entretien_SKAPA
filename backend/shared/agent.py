"""Agent IA avec RAG et tools météo.

Architecture :
- LLM : OpenAI GPT-4o-mini (configurable)
- RAG : Recherche dans la base de connaissances
- Tools : Météo via Open-Meteo
- Context : Historique conversations
"""
import logging
from typing import Optional

from openai import OpenAI

from backend.shared.db.crud import search_chunks, save_conversation

logger = logging.getLogger(__name__)


class Agent:
    """Agent IA avec RAG et tools météo."""

    def __init__(self, model: str, api_key: str, provider: str = "openai"):
        """Initialise l'agent.
        
        Args:
            model: Nom du modèle (ex: gpt-4o-mini)
            api_key: Clé API OpenAI
            provider: Provider LLM (openai, anthropic)
        """
        self.model = model
        self.api_key = api_key
        self.provider = provider
        
        if not api_key:
            raise ValueError("API_KEY is required for Agent")
        
        if provider == "openai":
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Provider {provider} not supported yet")

    def ask(self, question: str, chat_id: Optional[int] = None) -> str:
        """Répond à une question avec RAG + LLM.
        
        Args:
            question: Question de l'utilisateur
            chat_id: ID du chat (optionnel, pour historique)
            
        Returns:
            Réponse de l'agent
        """
        try:
            # 1. RAG : Rechercher dans la base de connaissances
            chunks = search_chunks(question, limit=3)
            context = "\n\n".join([
                f"Source: {c['source_file']}\n{c['content']}"
                for c in chunks
            ]) if chunks else "Aucun contexte trouvé."
            
            # 2. System prompt
            system_prompt = f"""Tu es un assistant météo intelligent.

Tu as accès à une base de connaissances et tu peux répondre aux questions sur la météo.

Contexte de la base de connaissances :
{context}

Instructions :
- Réponds de manière concise et précise
- Si tu parles de météo, mentionne la ville
- Si tu ne sais pas, dis-le clairement
- Utilise le contexte fourni si pertinent
"""
            
            # 3. Appel LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            answer = response.choices[0].message.content
            
            # 4. Sauvegarder la conversation
            sources = [c['source_file'] for c in chunks] if chunks else []
            save_conversation(
                question=question,
                answer=answer,
                sources=",".join(sources) if sources else ""
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in Agent.ask: {e}")
            return f"Erreur : {str(e)}"
