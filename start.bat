@echo off
title Anshita Makeover — India's Premier Bridal Studio
color 0E

echo.
echo ====================================================================
echo             ANSHITA MAKEOVER — BRIDAL STUDIO PLATFORM
echo ====================================================================
echo.

:: Ensure execution from django directory where manage.py resides
cd /d "%~dp0django"

:: Check if Python is available
set "PYTHON_EXE="
if exist "C:\Users\Aksha\anaconda3\python.exe" (
    set "PYTHON_EXE=C:\Users\Aksha\anaconda3\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [ERROR] Python was not found in your system PATH or standard Anaconda path.
        echo Please ensure Python is installed and accessible.
        echo.
        pause
        exit /b 1
    )
)

echo [1/4] Checking Python environment...
"%PYTHON_EXE%" -c "import django; print('      [OK] Django ' + django.__version__ + ' detected.')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Django is not found in the current Python environment.
    echo Attempting to install requirements...
    "%PYTHON_EXE%" -m pip install -r "%~dp0django\requirements.txt" 2>nul
)

echo.
echo [2/4] Applying database migrations...
"%PYTHON_EXE%" manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database migration check finished with notice.
)

echo.
echo [3/4] Launching Anshita Makeover in your browser...
start http://127.0.0.1:8000/

echo.
echo [4/4] Starting Django Studio Server...
echo.
echo ====================================================================
echo   ✦ Live Website:        http://127.0.0.1:8000/
echo   ✦ Services Catalogue:  http://127.0.0.1:8000/services/
echo   ✦ Packages Catalogue:  http://127.0.0.1:8000/packages/
echo   ✦ Dedicated Gallery:   http://127.0.0.1:8000/gallery/
echo   ✦ Academy Masterclass: http://127.0.0.1:8000/academy/
echo   ✦ Django Admin Portal: http://127.0.0.1:8000/admin-portal/
echo.
echo   ✦ Admin Credentials:
echo     Username: akshat (or regadmin)
echo     Password: Anshita@2026 (or RegTest@2026)
echo.
echo   To stop the server at any time, press CTRL + C in this window.
echo ====================================================================
echo.

"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000

pause
