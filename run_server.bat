@echo off
title Anshita Makeover - Local Server
color 0D

echo ========================================================
echo         ANSHITA MAKEOVER - STARTING SERVER
echo ========================================================
echo.

:: Navigate to anshita_project directory relative to this bat file
cd /d "%~dp0anshita_project"

:: Check if python is accessible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python or add it to system PATH.
    pause
    exit /b 1
)

echo [1/3] Checking database migrations...
python manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Migration check encountered an issue. Continuing...
)

echo.
echo [2/3] Verifying initial seed data and superusers...
python seed_data.py
echo.

echo [3/3] Opening browser at http://127.0.0.1:8000/ ...
start http://127.0.0.1:8000/

echo ========================================================
echo Server running at: http://127.0.0.1:8000/
echo Admin portal at:   http://127.0.0.1:8000/admin/
echo Studio portal at:  http://127.0.0.1:8000/studio-admin/
echo.
echo Credentials:
echo   Username: akshat (or admin)
echo   Password: Anshita@2026
echo.
echo Press CTRL+C in this terminal window to stop the server.
echo ========================================================
echo.

python manage.py runserver 127.0.0.1:8000

pause
