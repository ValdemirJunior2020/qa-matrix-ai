@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (echo Run install-backend.bat first.& pause & exit /b 1)
call .venv\Scripts\activate.bat
start "" /min cmd /c "ollama serve 1>nul 2>nul"
timeout /t 2 /nobreak >nul
python -c "from app.database import init_db; init_db(); from app.services.matrix_service import bootstrap_existing_matrix,matrix_status,rebuild_active_index; bootstrap_existing_matrix(); s=matrix_status(); (print(rebuild_active_index()) if s and not s.get('index_ready') else print('Matrix index already ready.'))" || echo Semantic index is not ready yet; server will still start with structured Matrix search.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
