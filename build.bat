@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Timestamp Script Analyzer - Windows Build
echo ============================================================
echo.

:: Verify we're in the right directory
if not exist "src\main.py" (
    echo [ERROR] Run this script from the project root directory.
    echo         Expected: d:\Youtube\Timestamp Script Analyzer\
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10-3.12 from https://python.org
    pause
    exit /b 1
)

:: Activate venv if present
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated.
) else (
    echo [WARN] No virtual environment found. Using system Python.
    echo        Recommend running setup.bat first.
)

:: Check espeak-ng
espeak-ng --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] espeak-ng not found in PATH — runtime auto-detection will locate standard install paths.
)

:: Install / update dependencies
echo [SETUP] Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies ready.

:: Clean previous build
echo.
echo [BUILD] Cleaning previous build artifacts...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Run PyInstaller
echo [BUILD] Running PyInstaller...
echo         This may take 5-15 minutes for the first build.
echo.

pyinstaller -y "Timestamp Script Analyzer.spec"

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Build Complete!
echo ============================================================
echo.
echo  Executable location:
echo    dist\Timestamp Script Analyzer\Timestamp Script Analyzer.exe
echo.
echo  To distribute:
echo    1. Zip the entire  dist\Timestamp Script Analyzer\  folder
echo    2. Or use Inno Setup to create a proper installer
echo       (see https://jrsoftware.org/isinfo.php)
echo.
pause
