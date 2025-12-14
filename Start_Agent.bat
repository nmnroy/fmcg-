@echo off
echo Starting FMCG Agent...
taskkill /F /IM python.exe >nul 2>&1
cd /d "%~dp0"
streamlit run streamlit_app.py
pause
