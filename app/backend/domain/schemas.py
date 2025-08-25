from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from ..core.security import sanitize_minimal

class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    user_id: str = Field(..., description="Identificador do usuário")
    conversation_id: str = Field(..., description="Identificador da conversa")

    @validator("message", pre=True)
    def _sanitize(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("message must be a string")
        return sanitize_minimal(v)

class AgentStep(BaseModel):
    agent: str
    decision: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    source_agent_response: str
    agent_workflow: List[AgentStep]
