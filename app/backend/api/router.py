from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..domain.schemas import ChatRequest, ChatResponse
from ..services.chat_service import ChatService
from ..infra.redis_client import redis_client as r

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

@router.get("/chat/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        key = f"conversation:{conversation_id}"
        items = r.lrange(key, 0, -1)
        return [json.loads(x) for x in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load conversation")

@router.get("conversations")
def list_conversations(limit: int = 20):
    keys = r.keys("conversation:*")
    latest = sorted(keys, key=lambda x: r.llen(x), reverse=True)[:limit]
    return [k.decode().split(":",1)[1] if isinstance(k, bytes) else str(k) for k in latest]