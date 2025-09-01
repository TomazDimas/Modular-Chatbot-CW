from __future__ import annotations
import os, time, glob, re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import redis
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

DATA_DIR = Path("app/backend/data/knowledge")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
INDEX_NAME = os.getenv("KB_INDEX", "kb_idx")
DOC_PREFIX = os.getenv("KB_PREFIX", "kb:doc:")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

client = OpenAI()
r = redis.from_url(REDIS_URL)

def _split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks, i, step = [], 0, max(1, size - overlap)
    while i < len(text):
        chunks.append(text[i:i+size])
        i += step
    return chunks

def _load_md_docs() -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            continue
        lines = raw.splitlines()
        source = lines[0].strip() if lines else "unknown"
        body = "\n".join(lines[2:]) if len(lines) > 2 else "\n".join(lines[1:])
        for ch in _split_text(body):
            ch = re.sub(r"\s+\n", "\n", ch).strip()
            if ch:
                docs.append({"source": source, "text": ch})
    return docs

def _embed_texts(texts: List[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    arr = np.array([d.embedding for d in resp.data], dtype="float32")
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    arr = arr / np.clip(norms, 1e-12, None)
    return arr

def _ensure_index(vector_dim: int):
    from redis.commands.search.field import VectorField, TextField, TagField
    from redis.commands.search.index_definition import IndexDefinition, IndexType
    from redis.commands.search import Search

    try:
        r.ft(INDEX_NAME).info()
        return
    except Exception:
        pass

    schema = (
        TextField("text"),
        TextField("source"),
        VectorField(
            "embedding",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": vector_dim,
                "DISTANCE_METRIC": "COSINE",
                "M": 16,
                "EF_CONSTRUCTION": 200,
            },
        ),
    )
    definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)
    r.ft(INDEX_NAME).create_index(schema, definition=definition)

def _upsert_docs(docs: List[Dict[str, Any]]):
    texts = [d["text"] for d in docs]
    vecs = _embed_texts(texts)  
    _ensure_index(vecs.shape[1])

    pipe = r.pipeline(transaction=False)
    for i, (doc, vec) in enumerate(zip(docs, vecs)):
        key = f"{DOC_PREFIX}{i}"
        pipe.hset(
            key,
            mapping={
                "source": doc["source"],
                "text": doc["text"],
                "embedding": vec.tobytes(),
            },
        )
    pipe.execute()

def main():
    t0 = time.time()
    docs = _load_md_docs()
    if not docs:
        print("No .md files found in app/backend/data/knowledge")
        return
    _upsert_docs(docs)
    ms = int((time.time() - t0) * 1000)
    print(f"Indexed {len(docs)} chunks in {ms} ms into Redis index '{INDEX_NAME}'")

if __name__ == "__main__":
    main()