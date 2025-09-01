# app/backend/agents/knowledge_rag.py
from __future__ import annotations
import os, time, glob, json
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from pathlib import Path

import numpy as np
import structlog

from ..llm.client import OpenAILLMClient

log = structlog.get_logger()

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHUNK_SIZE = 600         # caracteres por chunk
CHUNK_OVERLAP = 80       # sobreposição para contexto
TOP_K = 3                # quantos chunks trazer para o contexto

def _split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split simples por número de caracteres, com overlap."""
    chunks = []
    i = 0
    n = max(1, size - overlap)
    while i < len(text):
        chunks.append(text[i:i+size])
        i += n
    return chunks

def _load_md_docs() -> List[Dict[str, Any]]:
    """Lê todos .md do DATA_DIR. Primeira linha = URL (source)."""
    docs: List[Dict[str, Any]] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            continue
        lines = raw.splitlines()
        source = lines[0].strip() if lines else "unknown"
        body = "\n".join(lines[2:]) if len(lines) > 2 else "\n".join(lines[1:])
        for ch in _split_text(body):
            docs.append({"source": source, "text": ch})
    return docs

def _normalize_rows(arr: np.ndarray) -> np.ndarray:
    """Normaliza linha a linha para que dot product = cosine similarity."""
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return arr / norms

class Embedder:
    """Wrapper simples para embeddings OpenAI v1."""
    def __init__(self, model: str = EMBED_MODEL):
        self.model = model

    def embed(self, texts: List[str]) -> np.ndarray:
        from openai import OpenAI
        client = OpenAI()  # usa OPENAI_API_KEY do ambiente
        resp = client.embeddings.create(model=self.model, input=texts)
        vecs = np.array([d.embedding for d in resp.data], dtype="float32")
        return _normalize_rows(vecs)

@dataclass
class KnowledgeIndex:
    vectors: np.ndarray                # shape (N, D)
    metadatas: List[Dict[str, Any]]    # len N, cada item tem {"source","text"}

def _build_index(embedder: Embedder, docs: List[Dict[str, Any]]) -> KnowledgeIndex:
    vecs = embedder.embed([d["text"] for d in docs])  # (N, D) normalizado
    return KnowledgeIndex(vectors=vecs, metadatas=docs)

def _retrieve(index: KnowledgeIndex, query_vec: np.ndarray, k: int = TOP_K) -> List[Dict[str, Any]]:
    """Como vetores estão normalizados, dot = cosine similarity."""
    sims = index.vectors @ query_vec.T  # (N,1)
    sims = sims.ravel()
    top = sims.argsort()[-k:][::-1]
    return [index.metadatas[i] | {"score": float(sims[i])} for i in top]

RAG_SYSTEM = (
    "You are a support assistant for InfinitePay. Answer ONLY using the provided context. "
    "If the answer is not in the context, say you don't know and suggest contacting support. "
    "Be concise, accurate, and reply in the same language as the question."
)

def _build_prompt(context_docs: List[Dict[str, Any]], question: str) -> Tuple[str, str]:
    """Monta o prompt do usuário e retorna também as fontes unificadas (string)."""
    ctx_blocks = []
    sources: List[str] = []
    for d in context_docs:
        ctx_blocks.append(d["text"])
        sources.append(d["source"])
    context = "\n\n---\n\n".join(ctx_blocks)
    user = f"Question:\n{question}\n\nContext:\n{context}\n\nAnswer strictly from the context."
    unique_sources = "; ".join(sorted(set(sources))[:3]) if sources else "unknown"
    return user, unique_sources

@dataclass
class KnowledgeAgent:
    llm: OpenAILLMClient | None = None
    _embedder: Embedder | None = None
    _index: KnowledgeIndex | None = None

    def __post_init__(self):
        if self.llm is None:
            self.llm = OpenAILLMClient()
        if self._embedder is None:
            self._embedder = Embedder()
        if self._index is None:
            t0 = time.time()
            docs = _load_md_docs()
            if not docs:
                log.bind(level="WARNING", agent="KnowledgeAgent").msg("kb_empty")
            self._index = _build_index(self._embedder, docs)
            build_ms = int((time.time() - t0) * 1000)
            log.bind(level="INFO", agent="KnowledgeAgent", docs=len(docs), build_ms=build_ms).msg("kb_built")

    def run(self, message: str) -> Dict[str, Any]:
        t0 = time.time()
        # 1) embed query
        qv = self._embedder.embed([message])  # (1, D) normalizado
        # 2) retrieve top-k
        hits = _retrieve(self._index, qv[0:1, :], k=TOP_K)
        # 3) prompt LLM with context
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
        ).msg("knowledge_ok")

        return {
            "text": answer,
            "meta": {
                "sources": sources,
                "llm_ms": llm_ms,
                "retrieved": [h["source"] for h in hits],
            },
        }
