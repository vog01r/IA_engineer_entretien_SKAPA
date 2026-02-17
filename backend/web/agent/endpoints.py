import os

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.shared.agent import Agent
from backend.web.auth.dependencies import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

limiter = Limiter(key_func=get_remote_address)

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
@limiter.limit("30/minute")
def ask_agent(http_request: Request, request: QuestionRequest):
    """Pose une question à l'agent avec tools météo (chat_id optionnel pour alertes)."""
    answer = agent.ask(request.question, chat_id=request.chat_id)
    return {"answer": answer}
