import pickle
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    EMBED_MODEL, RETRIEVAL_TOP_K, VECTORSTORE_DIR,
    BM25_PICKLE, BM25_IDS_PICKLE,
)

_embed_model: SentenceTransformer | None = None
_bm25 = None
_bm25_ids: list[str] | None = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL)
    return _embed_model


def _get_bm25():
    global _bm25, _bm25_ids
    if _bm25 is None:
        with open(BM25_PICKLE, "rb") as f:
            _bm25 = pickle.load(f)
        with open(BM25_IDS_PICKLE, "rb") as f:
            _bm25_ids = pickle.load(f)
    return _bm25, _bm25_ids


def _get_chroma_collection():
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    return client.get_or_create_collection("finguard")


def _tokenise(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z\u0900-\u097F]+", text.lower())


def _bm25_retrieve(query: str, top_k: int) -> list[dict]:
    try:
        bm25, ids = _get_bm25()
    except FileNotFoundError:
        return []
    tokens = _tokenise(query)
    scores = bm25.get_scores(tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    collection = _get_chroma_collection()
    result_ids = [ids[i] for i in top_indices if scores[i] > 0]
    if not result_ids:
        return []

    hydrated = collection.get(ids=result_ids, include=["documents", "metadatas"])
    chunks = []
    for i, chunk_id in enumerate(hydrated["ids"]):
        chunks.append({
            "id": chunk_id,
            "text": hydrated["documents"][i],
            "metadata": hydrated["metadatas"][i],
            "retrieval_sources": ["bm25"],
        })
    return chunks


def _semantic_retrieve(query: str, query_embedding: list[float], top_k: int) -> list[dict]:
    collection = _get_chroma_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for i, chunk_id in enumerate(results["ids"][0]):
        chunks.append({
            "id": chunk_id,
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "retrieval_sources": ["semantic"],
        })
    return chunks


def hybrid_retrieve(query: str, top_k: int = RETRIEVAL_TOP_K) -> list[dict]:
    model = _get_embed_model()
    query_embedding = model.encode([query])[0].tolist()

    bm25_chunks = _bm25_retrieve(query, top_k)
    semantic_chunks = _semantic_retrieve(query, query_embedding, top_k)

    merged: dict[str, dict] = {}
    for chunk in bm25_chunks:
        merged[chunk["id"]] = chunk
    for chunk in semantic_chunks:
        if chunk["id"] in merged:
            merged[chunk["id"]]["retrieval_sources"] = list(
                set(merged[chunk["id"]]["retrieval_sources"] + ["semantic"])
            )
        else:
            merged[chunk["id"]] = chunk

    return list(merged.values())[: 2 * top_k]


def invalidate_bm25_cache() -> None:
    global _bm25, _bm25_ids
    _bm25 = None
    _bm25_ids = None
