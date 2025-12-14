@echo off
echo ========================================
echo   ASIAN PAINTS RFP AUTOMATION AGENT
echo ========================================
echo.

REM Activate virtual environment
call rfp_env\Scripts\activate.bat

REM Check if RFP file is provided
if "%~1"=="" (
    echo Usage: run_rfp_agent.bat "path\to\rfp_file.pdf"
    echo.
    echo Or simply run: run_rfp_agent.bat
    echo This will process the default sample RFP
    echo.
    
    echo Processing default sample RFP...
    python main.py
) else (
    echo Processing: %~1
    python main.py "%~1"
)

echo.
echo ========================================
echo   Processing Complete!
echo   Check the output folder for results
echo ========================================
pause
