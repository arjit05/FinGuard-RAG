@echo off
REM One-shot setup for FinGuard RAG: venv, deps, .env, synthetic PDFs, ingestion.
setlocal
cd /d "%~dp0"

echo ==^> FinGuard RAG setup

REM Pick a working Python interpreter (avoid Windows Store stub).
where py >nul 2>nul && set "PY=py -3" || set "PY=python"

cd backend
if not exist .venv (
  echo ==^> Creating Python venv at backend\.venv
  %PY% -m venv .venv
  if errorlevel 1 goto :err
)
call .venv\Scripts\activate.bat

echo ==^> Installing Python dependencies
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if errorlevel 1 goto :err

if not exist .env (
  copy .env.example .env >nul
  echo.
  echo     !!  Created backend\.env from template.
  echo     !!  Edit it and set GOOGLE_API_KEY=^<your key^>
  echo     !!  Get a free key at https://aistudio.google.com/app/apikey
  echo.
)

if not exist data\raw\*.pdf (
  echo ==^> Generating synthetic PDFs
  python scripts\make_synthetic_pdfs.py
  if errorlevel 1 goto :err
)

if not exist bm25_index\bm25.pkl (
  echo ==^> Ingesting documents ^(first run downloads embedding model, may take a few minutes^)
  python -c "from pipeline.ingestion import ingest_all; print(ingest_all('data/raw/'))"
  if errorlevel 1 goto :err
)

cd ..

if not exist frontend\node_modules (
  echo ==^> Installing frontend dependencies
  pushd frontend
  call npm install
  popd
  if errorlevel 1 goto :err
)

echo.
echo ==^> Setup complete.
echo ==^> Make sure backend\.env has a valid GOOGLE_API_KEY, then run:
echo     start.bat
exit /b 0

:err
echo.
echo ==^> Setup failed. See messages above.
exit /b 1
