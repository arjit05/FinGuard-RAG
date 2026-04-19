import os
import sys
from pathlib import Path

# Ensure backend/ is on sys.path so all relative imports work
_BACKEND_DIR = Path(__file__).parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(_BACKEND_DIR / ".env")

import shutil
import time

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from google.genai.errors import ClientError as GeminiClientError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import DATA_RAW_DIR, BM25_PICKLE, VECTORSTORE_DIR
from pipeline.sanitiser import sanitise
from pipeline.retrieval import hybrid_retrieve, invalidate_bm25_cache
from pipeline.reranker import rerank
from pipeline.generator import generate
from pipeline.guardrails import validate
from pipeline.ingestion import ingest_all, ingest_single

try:
    from langdetect import detect as langdetect_detect
except Exception:
    def langdetect_detect(text: str) -> str:
        return "en"

app = FastAPI(title="FinGuard RAG", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/app", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")


class QueryRequest(BaseModel):
    question: str
    language: str | None = None


@app.post("/query")
async def query_endpoint(req: QueryRequest):
    ok, cleaned, reason = sanitise(req.question)
    if not ok:
        raise HTTPException(status_code=400, detail={"error": "Query rejected by input filter", "reason": reason})

    try:
        detected_lang = langdetect_detect(cleaned)
    except Exception:
        detected_lang = "en"
    language = req.language or detected_lang

    candidates = hybrid_retrieve(cleaned)
    reranked, max_score = rerank(cleaned, candidates)
    try:
        answer_text = generate(cleaned, reranked, max_score, language=language)
    except GeminiClientError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return JSONResponse(status_code=429, content={"error": "Gemini free-tier rate limit reached. Please wait a minute and try again."})
        raise

    retrieved_texts = [c["text"] for c in reranked]
    gr = validate(answer_text, cleaned, max_score, retrieved_texts)
    final_answer = gr.sanitised_response

    import re as _re
    parsed = {"answer": "", "source": "", "confidence": "UNSURE"}
    # Match each field, allowing multi-line values up to the next field keyword
    ans_m = _re.search(r"Answer:\s*(.*?)(?=\nSource:|\nConfidence:|$)", final_answer, _re.S)
    src_m = _re.search(r"Source:\s*(.*?)(?=\nConfidence:|$)", final_answer, _re.S)
    con_m = _re.search(r"Confidence:\s*(\S+)", final_answer)
    if ans_m:
        parsed["answer"] = ans_m.group(1).strip()
    if src_m:
        parsed["source"] = src_m.group(1).strip()
    if con_m:
        parsed["confidence"] = con_m.group(1).strip()

    return {
        "answer": parsed["answer"],
        "source": parsed["source"],
        "confidence": parsed["confidence"],
        "retrieval_score": round(max_score, 4),
        "guardrails_passed": gr.passed,
        "failed_rules": gr.failed_rules,
    }


@app.post("/ingest")
async def ingest_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_RAW_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = ingest_single(str(dest))
    invalidate_bm25_cache()
    return result


@app.get("/documents")
async def documents_endpoint():
    import chromadb
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    try:
        collection = client.get_collection("finguard")
    except Exception:
        return []
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    docs: dict[str, dict] = {}
    for meta in all_meta:
        src = meta.get("source", "unknown")
        if src not in docs:
            docs[src] = {"filename": src, "chunk_count": 0, "pages": set()}
        docs[src]["chunk_count"] += 1
        docs[src]["pages"].add(meta.get("page", 0))
    return [
        {"filename": v["filename"], "chunk_count": v["chunk_count"], "total_pages": len(v["pages"])}
        for v in docs.values()
    ]


@app.get("/health")
async def health_endpoint():
    status: dict = {"status": "ok"}
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        collections = client.list_collections()
        status["chromadb"] = f"{len(collections)} collection(s)"
    except Exception as e:
        status["chromadb"] = f"error: {e}"
        status["status"] = "degraded"

    status["bm25_index"] = "present" if BM25_PICKLE.exists() else "missing"
    status["google_api_key"] = "set" if os.getenv("GOOGLE_API_KEY") else "missing"
    return status


@app.get("/evaluate")
async def evaluate_endpoint():
    import importlib.util, sys as _sys
    eval_path = Path(__file__).parent / "evaluation" / "eval_runner.py"
    spec = importlib.util.spec_from_file_location("eval_runner", eval_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_evaluation()
