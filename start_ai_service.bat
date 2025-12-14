@echo off
echo Starting NyxOS AI Engine Service...
echo.

cd /d %~dp0

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Set environment variables
set AI_MODEL_PATH=data\models\best_model.pt
set AI_TOKENIZER_PATH=data\models\tokenizer.json
set AI_API_PORT=8000
set USE_GPU=false

REM Start the service
echo.
echo Starting AI service on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python -m api.server

pause

