from __future__ import annotations
from fastapi import APIRouter, HTTPException
from ..domain.schemas import ChatRequest, ChatResponse
from ..services.chat_service import ChatService
from ..infra.redis_client import redis_client as r
from ..core.sanitize import clean_text
import structlog
import json
import time

router = APIRouter()
log = structlog.get_logger()

@router.get("/health")
async def health():
    return {"ok": True}

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        req.message = clean_text(req.message)
        return ChatService.handle(req)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Algo deu errado, tente novamente.")

@router.get("/chat/{conversation_id}")
def get_conversation(conversation_id: str):
    key = f"conversation:{conversation_id}"
    try:
        items = r.lrange(key, 0, -1)  
        messages = []
        for raw in items:
            s = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)

            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                obj = {"role": "unknown", "content": s}

            messages.append(obj)

        log.bind(level="INFO", agent="API", conversation_id=conversation_id, items=len(messages)).msg("conversation_loaded")
        return messages

    except Exception as e:
        log.bind(level="ERROR", agent="API", conversation_id=conversation_id, error=str(e)).msg("conversation_load_failed")
        raise HTTPException(status_code=500, detail="Failed to load conversation")

@router.get("conversations")
def list_conversations(limit: int = 20):
    keys = r.keys("conversation:*")
    latest = sorted(keys, key=lambda x: r.llen(x), reverse=True)[:limit]
    return [k.decode().split(":",1)[1] if isinstance(k, bytes) else str(k) for k in latest]

@router.get("/users/{user_id}/conversations")
def list_conversations(user_id: str, limit: int = 50):
    try:
        ids = r.smembers(f"user:{user_id}:conversations")
        conv_ids = [i.decode() if isinstance(i, bytes) else str(i) for i in ids]

        metas = []
        for cid in conv_ids:
            raw = r.hgetall(f"conversation_meta:{cid}")
            meta = {
                (k.decode() if isinstance(k, bytes) else k):
                (v.decode() if isinstance(v, bytes) else v)
                for k, v in raw.items()
            }
            meta.setdefault("conversation_id", cid)
            metas.append(meta)

        metas.sort(key=lambda x: int(x.get("updated_at", "0")), reverse=True)
        return metas[:limit]
    except Exception as e:
        log.bind(level="ERROR", agent="API", user_id=user_id, error=str(e)).msg("list_conversations_failed")
        raise HTTPException(status_code=500, detail="Failed to list conversations")

@router.post("/users/{user_id}/conversations")
def create_conversation(user_id: str):
    import uuid
    cid = f"conv-{uuid.uuid4()}"
    try:
        r.sadd(f"user:{user_id}:conversations", cid)
        r.hset(f"conversation_meta:{cid}", mapping={
            "user_id": user_id,
            "title": "New conversation",
            "last_message_preview": "",
            "updated_at": str(int(time.time() * 1000)),
        })
        return {"conversation_id": cid}
    except Exception as e:
        log.bind(level="ERROR", agent="API", user_id=user_id, error=str(e)).msg("create_conversation_failed")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.delete("/users/{user_id}/conversations/{conversation_id}")
def delete_conversation(user_id: str, conversation_id: str):
    try:
        r.srem(f"user:{user_id}:conversations", conversation_id)
        r.delete(f"conversation:{conversation_id}")
        r.delete(f"conversation_meta:{conversation_id}")
        return {"ok": True}
    except Exception as e:
        log.bind(level="ERROR", agent="API", user_id=user_id, conversation_id=conversation_id, error=str(e)).msg("delete_conversation_failed")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")