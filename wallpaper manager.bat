@echo off
chcp 65001 > nul
title Wallpaper Engine Web Manager
echo 🚀 Starting Wallpaper Engine Web Manager...
echo.

REM 获取当前脚本所在目录
cd /d "%~dp0"

REM 检查Python是否可用
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found in PATH
    echo Please make sure Python is installed and added to PATH
    echo.
    pause
    exit /b 1
)

REM 检查是否在项目目录中
if not exist "app.py" (
    echo ❌ Error: app.py not found
    echo Please make sure you are in the correct project directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM 检查依赖包
echo 📦 Checking dependencies...
python -c "import flask" > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Flask not installed, installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Environment check passed
echo 🌐 Starting Flask server with auto-browser...
echo ℹ️  Press Ctrl+C to stop the server
echo.

REM 创建一个临时的Python脚本来同时启动服务器和浏览器
echo import subprocess, time, webbrowser, os, sys > temp_launcher.py
echo. >> temp_launcher.py
echo # 启动Flask服务器 >> temp_launcher.py
echo flask_process = subprocess.Popen([sys.executable, 'app.py']) >> temp_launcher.py
echo. >> temp_launcher.py
echo # 等待服务器启动 >> temp_launcher.py
echo time.sleep(3) >> temp_launcher.py
echo. >> temp_launcher.py
echo # 打开浏览器 >> temp_launcher.py
echo webbrowser.open('http://127.0.0.1:5000') >> temp_launcher.py
echo. >> temp_launcher.py
echo # 等待Flask进程结束 >> temp_launcher.py
echo try: >> temp_launcher.py
echo     flask_process.wait() >> temp_launcher.py
echo except KeyboardInterrupt: >> temp_launcher.py
echo     flask_process.terminate() >> temp_launcher.py
echo     flask_process.wait() >> temp_launcher.py
echo. >> temp_launcher.py
echo # 清理临时文件 >> temp_launcher.py
echo if os.path.exists('temp_launcher.py'): >> temp_launcher.py
echo     os.remove('temp_launcher.py') >> temp_launcher.py

REM 运行临时启动脚本
python temp_launcher.py

echo.
echo 👋 Server stopped
pause
