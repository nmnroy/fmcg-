@echo off
color 0A
title Asian Paints RFP Automation Agent

:menu
cls
echo ========================================
echo   ASIAN PAINTS RFP AUTOMATION AGENT
echo ========================================
echo.
echo   1. Process Sample RFP
echo   2. Process Custom RFP (Enter path)
echo   3. View Last Results
echo   4. Initialize Database
echo   5. Exit
echo.
echo ========================================
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto sample
if "%choice%"=="2" goto custom
if "%choice%"=="3" goto results
if "%choice%"=="4" goto initdb
if "%choice%"=="5" goto exit
goto menu

:sample
cls
echo Processing Sample RFP...
call rfp_env\Scripts\activate.bat
python main.py
pause
goto menu

:custom
cls
echo.
set /p rfppath="Enter full path to RFP file: "
call rfp_env\Scripts\activate.bat
python main.py "%rfppath%"
pause
goto menu

:results
cls
echo Opening output folder...
start explorer output
pause
goto menu

:initdb
cls
echo Initializing database...
call rfp_env\Scripts\activate.bat
python init_database.py
pause
goto menu

:exit
exit
