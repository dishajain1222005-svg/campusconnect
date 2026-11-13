@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  CampusConnect – Start Server
REM  Run this file by double-clicking or from the command prompt.
REM  It activates the virtual environment and starts the Flask app.
REM ═══════════════════════════════════════════════════════════════════════

cd /d "%~dp0.."
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting CampusConnect...
echo Press CTRL+C to stop.
echo.
python run.py

pause
