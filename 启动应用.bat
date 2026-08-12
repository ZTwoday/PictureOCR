@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 启动前检查：模块能否正常导入（双击后毫无反应时，这里会显示原因）
".venv\Scripts\python.exe" -c "import main" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 启动检查失败，错误信息如下：
    ".venv\Scripts\python.exe" -c "import main"
    echo.
    echo 可能原因：.venv 被重建过，或 PySide6 的 ICU 修复丢失。
    echo 请把上面的错误信息发给开发者。
    echo.
    pause
    exit /b 1
)

REM 正常启动（无控制台窗口，应用驻留托盘）
start "" ".venv\Scripts\pythonw.exe" "main.py"
