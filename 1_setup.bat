@echo off
cd /d "%~dp0"
echo === Creating virtual environment (.venv) ===
where py >nul 2>nul && (py -3.11 -m venv .venv || py -m venv .venv) || python -m venv .venv
if not exist .venv\Scripts\python.exe (echo [X] Python not found. Install Python 3.11 & pause & exit /b 1)
echo === Installing requirements ===
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if not exist .env copy env_template.txt .env >nul
echo.
echo Done. Opening .env - paste your key, save, close, then run 2_check_key.bat
notepad .env
pause
