@echo off
REM The AI Dollar - Quick Setup for Windows

echo.
echo ====================================
echo The AI Dollar - Setup Script
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo OK: Python found
echo.

REM Create directories
echo Creating directories...
if not exist "videos" mkdir videos
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo OK: Directories created
echo.

REM Install dependencies
echo Installing Python packages (this may take 2-3 minutes)...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo OK: All packages installed
echo.

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Get YouTube API key from: https://console.cloud.google.com/
echo 3. Run: python video_generator.py
echo.
echo Read THE_AI_DOLLAR_SETUP.md for detailed instructions
echo.
pause
