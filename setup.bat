@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Timestamp Script Analyzer - Windows Setup
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10-3.12 from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% found

:: Create virtual environment
if not exist "venv" (
    echo.
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

:: Activate venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo [SETUP] Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install requirements
echo.
echo [SETUP] Installing dependencies (this may take a few minutes)...
echo         - Flask
echo         - Kokoro TTS
echo         - Faster-Whisper
echo         - soundfile, torch, numpy
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed. Check the error above.
    pause
    exit /b 1
)

echo.
echo [OK] All Python dependencies installed

:: Check espeak-ng
echo.
echo [CHECK] Checking for espeak-ng...
espeak-ng --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] espeak-ng not found in PATH
    echo.
    echo   Kokoro TTS requires espeak-ng for phoneme processing.
    echo   Please install it manually:
    echo.
    echo   1. Open this URL in your browser:
    echo      https://github.com/espeak-ng/espeak-ng/releases
    echo.
    echo   2. Download the latest .msi file  e.g. espeak-ng-2.x-x64.msi
    echo.
    echo   3. Run the installer
    echo      IMPORTANT: Check the box "Add to PATH" during installation
    echo.
    echo   4. Restart this setup script after installation
    echo.
    pause
    exit /b 1
) else (
    echo [OK] espeak-ng found
)

:: Create output directory
if not exist "output" mkdir output
echo [OK] Output directory ready

echo.
echo ============================================================
echo  Setup Complete!
echo ============================================================
echo.
echo  To start the application:
echo.
echo    setup.bat
echo    python src\main.py
echo.
echo  First run will download model weights automatically:
echo    - Kokoro TTS model   (~350 MB from HuggingFace)
echo    - Faster-Whisper base model  (~140 MB)
echo.
pause
