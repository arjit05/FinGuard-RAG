import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Chunking
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# Retrieval
RETRIEVAL_TOP_K = 10
RERANK_TOP_K = 5
# Tuned from 0.35 → -7.0: cross-encoder ms-marco scores range ~-10 to +10.
# Weather queries score ~-10.8 (blocked); domain queries score -6 to +5 (pass).
RETRIEVAL_SCORE_THRESHOLD = -7.0

# Models
EMBED_MODEL = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "gemini-2.5-flash"

# Paths
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
BM25_INDEX_DIR = BASE_DIR / "bm25_index"
BM25_PICKLE = BM25_INDEX_DIR / "bm25.pkl"
BM25_IDS_PICKLE = BM25_INDEX_DIR / "bm25_ids.pkl"
CHUNKS_JSONL = DATA_PROCESSED_DIR / "chunks.jsonl"

# Guardrail: max response word count
MAX_RESPONSE_WORDS = 500
MIN_RESPONSE_WORDS = 50

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
