@echo off
title MedBotX API Server
cd /d "c:\Users\bhask\Euron Projects\MedBotX - Advanced Medical Chatbot with Memory"
echo.
echo  ==========================================
echo   MedBotX - API Server
echo   Developed by Bhaskar Shivaji Kumbhar
echo  ==========================================
echo.
echo  Starting API at http://localhost:8000
echo  API Docs at   http://localhost:8000/docs
echo.
echo  Keep this window OPEN while using the app
echo.
call venv\Scripts\activate
python -m uvicorn app.main:app --port 8000 --reload
pause
