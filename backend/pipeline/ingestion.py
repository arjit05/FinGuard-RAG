import json
import pickle
import re
import time
from pathlib import Path

import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, EMBED_MODEL,
    VECTORSTORE_DIR, BM25_INDEX_DIR, BM25_PICKLE, BM25_IDS_PICKLE,
    CHUNKS_JSONL, DATA_PROCESSED_DIR,
)

_SECTION_RE = re.compile(r"(Section\s+\d+(?:\.\d+)?[^\n]*)", re.I)

_embed_model: SentenceTransformer | None = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL)
    return _embed_model


def _get_chroma_collection():
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    return client.get_or_create_collection("finguard")


def _tokenise(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z\u0900-\u097F]+", text.lower())


def _extract_section(text: str) -> str:
    match = _SECTION_RE.search(text)
    return match.group(1).strip()[:80] if match else ""


def _sliding_window_chunks(words: list[str], source: str, page: int, section: str) -> list[dict]:
    chunks = []
    i = 0
    idx = 0
    while i < len(words):
        chunk_words = words[i: i + CHUNK_SIZE]
        chunks.append({
            "text": " ".join(chunk_words),
            "source": source,
            "page": page,
            "section": section,
            "chunk_idx": idx,
        })
        idx += 1
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _parse_pdf(pdf_path: Path) -> list[dict]:
    doc = fitz.open(str(pdf_path))
    all_chunks = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if not text.strip():
            continue
        section = _extract_section(text)
        words = text.split()
        if not words:
            continue
        chunks = _sliding_window_chunks(words, pdf_path.name, page_num, section)
        all_chunks.extend(chunks)
    doc.close()
    return all_chunks


def _build_chunk_id(chunk: dict) -> str:
    return f"{chunk['source']}::p{chunk['page']}::c{chunk['chunk_idx']}"


def _ingest_chunks(chunks: list[dict], collection) -> int:
    model = _get_embed_model()
    existing_ids = set(collection.get(include=[])["ids"])

    new_chunks = [c for c in chunks if _build_chunk_id(c) not in existing_ids]
    if not new_chunks:
        return 0

    texts = [c["text"] for c in new_chunks]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=False).tolist()
    ids = [_build_chunk_id(c) for c in new_chunks]
    metadatas = [
        {"source": c["source"], "page": c["page"], "section": c["section"], "chunk_idx": c["chunk_idx"]}
        for c in new_chunks
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(new_chunks)


def _rebuild_bm25(collection) -> None:
    BM25_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    result = collection.get(include=["documents"])
    ids = result["ids"]
    docs = result["documents"]
    tokenised = [_tokenise(d) for d in docs]
    bm25 = BM25Okapi(tokenised)
    with open(BM25_PICKLE, "wb") as f:
        pickle.dump(bm25, f)
    with open(BM25_IDS_PICKLE, "wb") as f:
        pickle.dump(ids, f)


def _save_chunks_jsonl(chunks: list[dict]) -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_JSONL, "a", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")


def ingest_single(pdf_path: str) -> dict:
    path = Path(pdf_path)
    chunks = _parse_pdf(path)
    collection = _get_chroma_collection()
    added = _ingest_chunks(chunks, collection)
    _save_chunks_jsonl(chunks)
    _rebuild_bm25(collection)
    return {"file": path.name, "chunks_parsed": len(chunks), "chunks_added": added}


def ingest_all(raw_dir: str) -> dict:
    raw_path = Path(raw_dir)
    pdfs = sorted(raw_path.glob("*.pdf"))
    start = time.time()
    collection = _get_chroma_collection()

    # Clear existing JSONL to avoid duplicates on full re-ingest
    if CHUNKS_JSONL.exists():
        CHUNKS_JSONL.unlink()

    total_chunks = 0
    for pdf in pdfs:
        chunks = _parse_pdf(pdf)
        _ingest_chunks(chunks, collection)
        _save_chunks_jsonl(chunks)
        total_chunks += len(chunks)

    _rebuild_bm25(collection)
    elapsed = round(time.time() - start, 2)
    return {"docs": len(pdfs), "chunks": total_chunks, "elapsed_s": elapsed}
