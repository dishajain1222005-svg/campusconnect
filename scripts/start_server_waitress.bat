@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  CampusConnect – Start Server with Waitress (more stable for demos)
REM ═══════════════════════════════════════════════════════════════════════

cd /d "%~dp0.."
call venv\Scripts\activate.bat

echo.
echo Starting CampusConnect (Waitress WSGI server)...
echo.
python run.py --waitress

pause
