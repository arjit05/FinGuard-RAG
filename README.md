# FinGuard RAG

Production-grade Retrieval-Augmented Generation pipeline over Indian financial regulatory documents (RBI, IRDAI, SEBI) and sample loan/insurance policies.

**Contract:** every answer either cites a source or admits uncertainty. No hallucinations, no ungrounded financial advice.

## Quick Start

**Prerequisites:** Python 3.10+, Node 18+, and a free Google AI Studio API key
(grab one at https://aistudio.google.com/app/apikey).

### One-shot setup

```bash
# Windows
setup.bat

# macOS / Linux / Git Bash
./setup.sh
```

This creates `backend/.venv`, installs Python + npm dependencies, generates the
7 synthetic PDFs, and ingests them into ChromaDB + BM25. The first run downloads
the embedding and cross-encoder models (~200 MB) and takes a few minutes.

### Add your API key

Open `backend/.env` and set:

```
GOOGLE_API_KEY=<your key>
```

### Launch

```bash
# Windows  (opens backend + frontend in two new terminal windows)
start.bat

# macOS / Linux / Git Bash  (runs both in the foreground; Ctrl+C stops both)
./start.sh
```

Then open http://localhost:5173.

### Manual steps (if you'd rather)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env                                  # add GOOGLE_API_KEY
python scripts/make_synthetic_pdfs.py
python -c "from pipeline.ingestion import ingest_all; print(ingest_all('data/raw/'))"
uvicorn main:app --port 8000 --reload

# in a second terminal:
cd frontend && npm install && npm run dev
```

## Architecture

- **Retrieval**: BM25 + ChromaDB semantic search, merged hybrid
- **Reranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Generation**: Google Gemini 2.5 Flash via the `google-genai` SDK
- **Guardrails**: 10-rule validator (PII redaction, hallucination guard, source citation enforcement, etc.)
- **Injection defence**: 3-layer sanitiser (pattern match + length cap + system prompt hardening)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/query` | Main QA endpoint |
| POST | `/ingest` | Upload a PDF |
| GET | `/documents` | List indexed documents |
| GET | `/health` | System health |
| GET | `/evaluate` | Run 50-QA benchmark |

## Corpus

7 synthetic PDFs covering:
- RBI Loans and Advances (foreclosure rules, LTV, priority sector)
- RBI KYC Master Directions
- IRDAI Health Insurance Guidelines (portability, waiting periods)
- SEBI Mutual Fund Regulations (categorisation, TER, redemption)
- RBI UPI Guidelines (limits, fraud liability)
- Sample Home Loan Agreement
- Sample Term Insurance Policy

## Evaluation Targets

| Metric | Target |
|--------|--------|
| Exact-match accuracy | ≥ 60% |
| Semantic accuracy (>0.8 sim) | ≥ 80% |
| Guardrail pass rate | 100% |
| Hallucination rate | < 10% |
| Refusal rate | 5–15% |

Run: `curl http://localhost:8000/evaluate` or `python backend/evaluation/eval_runner.py`
