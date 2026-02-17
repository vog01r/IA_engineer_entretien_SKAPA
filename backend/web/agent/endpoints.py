import os

from fastapi import APIRouter
from pydantic import BaseModel

from backend.shared.agent import Agent

router = APIRouter()

# Initialiser l'agent (clé depuis .env)
agent = Agent(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY", ""),
    provider="openai",
)


class QuestionRequest(BaseModel):
    question: str
    chat_id: int | None = None


@router.get("/")
async def agent_root():
    """Endpoint racine Agent."""
    return {"message": "Agent endpoint", "ask": "POST /agent/ask"}


@router.post("/ask")
def ask_agent(request: QuestionRequest):
    """Pose une question à l'agent avec tools météo (chat_id optionnel pour alertes)."""
    answer = agent.ask(request.question, chat_id=request.chat_id)
    return {"answer": answer}
