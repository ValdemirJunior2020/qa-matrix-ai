@echo off
setlocal
cd /d "%~dp0"
echo ==============================================================
echo               QA MATRIX AI - BACKEND INSTALLER
echo ==============================================================
where py >nul 2>&1 || (echo Python 3 is required. Install Python 3.11 or 3.12 and re-run.& pause & exit /b 1)
if not exist .venv (
  py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv 2>nul || py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt || (echo Dependency installation failed.& pause & exit /b 1)
where ollama >nul 2>&1
if errorlevel 1 (
  echo Ollama not found. Attempting install with winget...
  where winget >nul 2>&1 && winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
)
where ollama >nul 2>&1 && (
  echo Pulling fast QA model...
  ollama pull qwen3:4b-instruct
  echo Pulling local embedding model...
  ollama pull embeddinggemma
)
if not exist .env copy .env.example .env >nul
if not exist data\database\qa_matrix.db (
  echo.
  echo Create the initial admin login.
  python bootstrap_admin.py --email infojr.83@gmail.com
) else (
  echo Existing database found. Admin credentials were not overwritten.
)
echo.
echo Install complete. Use run-server.bat to start the private backend.
pause
