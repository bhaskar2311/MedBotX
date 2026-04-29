@echo off
title MedBotX - Frontend
cd /d "%~dp0"
echo.
echo  ==========================================
echo   MedBotX Frontend Starting...
echo   Developed by Bhaskar Shivaji Kumbhar
echo  ==========================================
echo.
echo  Frontend will open at: http://localhost:8501
echo.
echo  >>> Keep this window OPEN <<<
echo.
venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501
echo.
echo  Frontend stopped. Press any key to close.
pause
