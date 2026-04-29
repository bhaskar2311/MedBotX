@echo off
title MedBotX - API Server
cd /d "%~dp0"
echo.
echo  ==========================================
echo   MedBotX API Server Starting...
echo   Developed by Bhaskar Shivaji Kumbhar
echo  ==========================================
echo.
echo  API will be available at: http://localhost:8000
echo  API Docs at:              http://localhost:8000/docs
echo.
echo  >>> Keep this window OPEN <<<
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
echo.
echo  Server stopped. Press any key to close.
pause
