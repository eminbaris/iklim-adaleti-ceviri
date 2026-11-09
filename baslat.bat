@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo COP31 Uluslararasi Iklim Adaleti Forumu Simultane Sistemi Baslatiliyor...
start "" "http://localhost:8000"
start "" "http://localhost:8000/ekran"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
pause
