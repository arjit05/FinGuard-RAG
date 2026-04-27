#!/usr/bin/env bash
# Launch backend (FastAPI) + frontend (Vite) together.
set -e
cd "$(dirname "$0")"

if [ -f backend/.venv/Scripts/activate ]; then
  # shellcheck disable=SC1091
  source backend/.venv/Scripts/activate
elif [ -f backend/.venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source backend/.venv/bin/activate
else
  echo "No venv found at backend/.venv. Run ./setup.sh first."
  exit 1
fi

if [ -f backend/.env ]; then
  # shellcheck disable=SC1091
  set -a; source backend/.env; set +a
fi

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "AIza..." ]; then
  echo "==> WARNING: GOOGLE_API_KEY is not set in backend/.env."
  echo "    The app will start but /query will fail until you add a real key."
fi

echo "==> Starting backend on http://localhost:8000"
( cd backend && python -m uvicorn main:app --port 8000 --reload ) &
BACKEND_PID=$!

cleanup() { kill "$BACKEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo "==> Starting frontend on http://localhost:5173"
( cd frontend && npm run dev )
