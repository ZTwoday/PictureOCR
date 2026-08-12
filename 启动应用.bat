@echo off
cd /d "%~dp0"

".venv\Scripts\python.exe" -c "import main" >nul 2>&1
if errorlevel 1 goto :err

start "" ".venv\Scripts\pythonw.exe" "main.py"
exit /b 0

:err
echo.
echo Startup check failed. Show the error below to the developer:
".venv\Scripts\python.exe" -c "import main"
echo.
pause
