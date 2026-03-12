@echo off
echo 🚦 Vietnamese Traffic Law QA System - Setup & Run
echo ================================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔄 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 🔄 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install basic requirements
    pause
    exit /b 1
)

pip install -r requirements-knowledge.txt
if errorlevel 1 (
    echo ❌ Failed to install knowledge graph requirements
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check if data exists
if not exist "data\processed\violations_100.json" (
    echo ⚠️  Warning: violations_100.json not found
    echo Please ensure data is properly processed
)

echo.
echo 🎯 Setup completed! Choose an option:
echo.
echo [1] Run Quick Demo
echo [2] Run Web Interface
echo [3] Run Tests
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🚀 Starting demo...
    python demo.py
) else if "%choice%"=="2" (
    echo 🚀 Starting web interface...
    echo Opening browser at http://localhost:8501
    cd src\traffic_law_qa\ui
    streamlit run streamlit_app.py
) else if "%choice%"=="3" (
    echo 🧪 Running tests...
    python test_knowledge_system.py
) else if "%choice%"=="4" (
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo ❌ Invalid choice
)

pause