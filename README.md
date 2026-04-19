# FinGuard RAG

Production-grade Retrieval-Augmented Generation pipeline over Indian financial regulatory documents (RBI, IRDAI, SEBI) and sample loan/insurance policies.

**Contract:** every answer either cites a source or admits uncertainty. No hallucinations, no ungrounded financial advice.

## Quick Start

### 1. Generate Synthetic PDFs

```bash
cd finguard-rag/backend
pip install -r requirements.txt
python scripts/make_synthetic_pdfs.py
```

### 2. Ingest Documents

```bash
python -c "from pipeline.ingestion import ingest_all; print(ingest_all('data/raw/'))"
```

### 3. Start Backend

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn main:app --port 8000 --reload
```

### 4. Start Frontend

```bash
cd ../frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Architecture

- **Retrieval**: BM25 + ChromaDB semantic search, merged hybrid
- **Reranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Generation**: Claude Sonnet via Anthropic SDK with prompt caching
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
