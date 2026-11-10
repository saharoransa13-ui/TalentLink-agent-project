@echo off
cd /d "%~dp0"
echo API: http://127.0.0.1:8000/docs
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
