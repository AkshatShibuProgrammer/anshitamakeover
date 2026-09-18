@echo off
title Anshita Makeover — Local Server
color 0E

echo.
echo ====================================================================
echo             ANSHITA MAKEOVER — BRIDAL STUDIO SERVER
echo ====================================================================
echo.

:: Navigate to anshita_project directory relative to this bat file
cd /d "%~dp0anshita_project"

:: Check if Python is accessible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Users\Aksha\anaconda3\python.exe" (
        set "PYTHON_EXE=C:\Users\Aksha\anaconda3\python.exe"
    ) else (
        echo [ERROR] Python was not found in your system PATH.
        echo Please ensure Python is installed and accessible.
        pause
        exit /b 1
    )
) else (
    set "PYTHON_EXE=python"
)

echo [1/3] Checking database migrations...
"%PYTHON_EXE%" manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Migration check encountered an issue. Continuing...
)

echo.
echo [2/3] Launching browser at http://127.0.0.1:8000/ ...
start http://127.0.0.1:8000/

echo.
echo [3/3] Server details:
echo ====================================================================
echo   ✦ Website URL:         http://127.0.0.1:8000/
echo   ✦ Academy Portal:      http://127.0.0.1:8000/academy/
echo   ✦ Django Admin:        http://127.0.0.1:8000/django-admin/
echo.
echo   ✦ Credentials:
echo     Username: akshat (or admin)
echo     Password: Anshita@2026
echo.
echo   Press CTRL+C in this terminal window to stop the server.
echo ====================================================================
echo.

"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000

pause
