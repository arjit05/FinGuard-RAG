@echo off
REM Launch backend (FastAPI) + frontend (Vite) in two separate windows.
cd /d "%~dp0"

if not exist backend\.venv\Scripts\activate.bat (
  echo No venv found at backend\.venv. Run setup.bat first.
  exit /b 1
)

echo ==^> Starting backend in a new window  ^(http://localhost:8000^)
start "FinGuard Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && python -m uvicorn main:app --port 8000 --reload"

echo ==^> Starting frontend in a new window  ^(http://localhost:5173^)
start "FinGuard Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==^> Backend:  http://localhost:8000
echo ==^> Frontend: http://localhost:5173
echo.
echo Close those two windows to stop the servers.
