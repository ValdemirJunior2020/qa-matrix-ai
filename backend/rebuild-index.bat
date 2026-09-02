@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -c "from app.database import init_db; init_db(); from app.services.matrix_service import bootstrap_existing_matrix,rebuild_active_index; bootstrap_existing_matrix(); print(rebuild_active_index())"
pause
