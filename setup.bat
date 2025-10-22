@echo off
echo ========================================
echo MCP Multi-Agent Orchestration Setup
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error creating virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo Step 4: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo [OK] .env file created
) else (
    echo [SKIP] .env file already exists
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run: python main.py
echo.
echo Or simply run: run.bat
echo.
pause
