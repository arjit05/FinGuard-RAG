#!/usr/bin/env bash
# One-shot setup for FinGuard RAG: venv, deps, .env, synthetic PDFs, ingestion.
set -e
cd "$(dirname "$0")"

echo "==> FinGuard RAG setup"

# Pick a working Python interpreter (avoids the Windows Store stub).
if command -v py >/dev/null 2>&1; then
  PY="py -3"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python is not installed. Get it from https://www.python.org/downloads/"
  exit 1
fi

cd backend

if [ ! -d .venv ]; then
  echo "==> Creating Python venv at backend/.venv"
  $PY -m venv .venv
fi

if [ -f .venv/Scripts/activate ]; then
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Installing Python dependencies"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "    !!  Created backend/.env from template."
  echo "    !!  Edit it and set GOOGLE_API_KEY=<your key>"
  echo "    !!  Get a free key at https://aistudio.google.com/app/apikey"
  echo ""
fi

if [ ! -d data/raw ] || [ -z "$(ls -A data/raw/*.pdf 2>/dev/null)" ]; then
  echo "==> Generating synthetic PDFs"
  python scripts/make_synthetic_pdfs.py
fi

if [ ! -d vectorstore ] || [ ! -f bm25_index/bm25.pkl ]; then
  echo "==> Ingesting documents (first run downloads embedding model, may take a few minutes)"
  python -c "from pipeline.ingestion import ingest_all; print(ingest_all('data/raw/'))"
fi

cd ..

if [ ! -d frontend/node_modules ]; then
  echo "==> Installing frontend dependencies"
  (cd frontend && npm install)
fi

echo ""
echo "==> Setup complete."
echo "==> Make sure backend/.env has a valid GOOGLE_API_KEY, then run:"
echo "    ./start.sh"
