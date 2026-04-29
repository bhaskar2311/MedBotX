@echo off
title MedBotX Frontend
cd /d "c:\Users\bhask\Euron Projects\MedBotX - Advanced Medical Chatbot with Memory"
echo.
echo  ==========================================
echo   MedBotX - Frontend (Streamlit)
echo   Developed by Bhaskar Shivaji Kumbhar
echo  ==========================================
echo.
echo  Opening at http://localhost:8501
echo.
echo  Keep this window OPEN while using the app
echo.
call venv\Scripts\activate
python -m streamlit run frontend/app.py --server.port 8501
pause
