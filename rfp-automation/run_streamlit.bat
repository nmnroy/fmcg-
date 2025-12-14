@echo off
echo ========================================
echo   ASIAN PAINTS RFP WEB INTERFACE
echo ========================================
echo.

REM Activate virtual environment
call rfp_env\Scripts\activate.bat

REM Start Streamlit app
echo Starting web interface...
streamlit run streamlit_app.py

pause
