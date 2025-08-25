from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..domain.schemas import ChatRequest, ChatResponse
from ..services.chat_service import ChatService

router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True}

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        return ChatService.handle(req)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Algo deu errado, tente novamente.")
