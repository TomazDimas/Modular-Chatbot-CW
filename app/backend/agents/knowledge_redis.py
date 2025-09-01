from __future__ import annotations
import os, time
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

import numpy as np
import redis
import structlog
from openai import OpenAI

from ..llm.client import OpenAILLMClient

log = structlog.get_logger()

REDIS_URL   = os.getenv("REDIS_URL", "redis://localhost:6379/0")
INDEX_NAME  = os.getenv("KB_INDEX", "kb_idx")
TOP_K       = int(os.getenv("KB_TOP_K", "3"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

RAG_SYSTEM = (
    "You are a support assistant for InfinitePay. Answer ONLY using the provided context. "
    "If the answer is not in the context, say you don't know and suggest contacting support. "
    "Be concise, accurate, and reply in the same language as the question."
)

def _normalize_rows(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return arr / norms

def _embed_query(text: str) -> np.ndarray:
    api = OpenAI()
    resp = api.embeddings.create(model=EMBED_MODEL, input=[text])
    vec = np.array([resp.data[0].embedding], dtype="float32")
    return _normalize_rows(vec)

def _knn_search(r: redis.Redis, qvec: np.ndarray, k: int) -> List[Dict[str, Any]]:
    from redis.commands.search.query import Query

    qbytes = qvec.astype("float32").tobytes()
    q = (
        Query(f'*=>[KNN {k} @embedding $vec AS score]')
        .return_fields("source", "text", "score")
        .sort_by("score")
        .paging(0, k)
        .dialect(2)
    )
    res = r.ft(INDEX_NAME).search(q, query_params={"vec": qbytes})
    out: List[Dict[str, Any]] = []
    for doc in res.docs:
        out.append({"source": doc.source, "text": doc.text, "score": float(doc.score)})
    return out

def _build_prompt(hits: List[Dict[str, Any]], question: str) -> Tuple[str, str]:
    context = "\n\n---\n\n".join(h["text"] for h in hits)
    sources = "; ".join(sorted({h["source"] for h in hits})) if hits else "unknown"
    user = f"Question:\n{question}\n\nContext:\n{context}\n\nAnswer strictly from the context."
    return user, sources

@dataclass
class KnowledgeAgentRedis:
    llm: OpenAILLMClient | None = None
    r: redis.Redis | None = None

    def __post_init__(self):
        if self.llm is None:
            self.llm = OpenAILLMClient()
        if self.r is None:
            self.r = redis.from_url(REDIS_URL)

    def run(self, message: str) -> Dict[str, Any]:
        t0 = time.time()

        qv = _embed_query(message)
        hits = _knn_search(self.r, qv, TOP_K)

        user, sources = _build_prompt(hits, message)

        t_llm = time.time()
        answer = self.llm.generate(system=RAG_SYSTEM, user=user)
        llm_ms = int((time.time() - t_llm) * 1000)

        total_ms = int((time.time() - t0) * 1000)
        log.bind(
            level="INFO",
            agent="KnowledgeAgent",
            execution_time_ms=total_ms,
            llm_ms=llm_ms,
            sources=sources,
            retrieved=len(hits),
        ).msg("knowledge_ok")

        if not hits or not (answer and answer.strip()):
            answer = (
                "I couldn't find this in the help center context. "
                "Please check the support center or contact support."
            )

        return {
            "text": answer,
            "meta": {
                "sources": sources,
                "llm_ms": llm_ms,
                "retrieved": [h["source"] for h in hits],
            },
        }