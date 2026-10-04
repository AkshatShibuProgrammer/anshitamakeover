@echo off
title Anshita Makeover — Git Fetch & Rerun Server
color 0E

echo.
echo ====================================================================
echo          ANSHITA MAKEOVER — GIT FETCH ^& RERUN STUDIO
echo ====================================================================
echo.

:: Root directory of repository
set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

:: [1/5] Git Fetch from remote
echo [1/5] Fetching latest changes from Git remote...
git fetch --all --prune
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Git fetch encountered an issue. Continuing with local codebase...
) else (
    echo       [OK] Git fetch completed.
)

:: Show current branch & latest commit info
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set "GIT_BRANCH=%%i"
echo       [Branch] %GIT_BRANCH%
for /f "tokens=*" %%i in ('git log -1 --format="%%h (%%ar) : %%s" 2^>nul') do (
    echo       [Latest Commit] %%i
)
echo.

:: [2/5] Stop existing Django runserver processes on port 8000
echo [2/5] Cleaning up existing Django server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo       Stopping process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo       [OK] Port 8000 is ready.
echo.

:: [3/5] Detect Python executable
echo [3/5] Detecting Python environment...
set "PYTHON_EXE="
if exist "C:\Users\Aksha\anaconda3\python.exe" (
    set "PYTHON_EXE=C:\Users\Aksha\anaconda3\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [ERROR] Python not found in system PATH or standard Anaconda path.
        pause
        exit /b 1
    )
)
echo       [OK] Using Python: %PYTHON_EXE%
echo.

:: [4/5] Check migrations inside django directory
echo [4/5] Checking Django migrations...
cd /d "%REPO_ROOT%django"
"%PYTHON_EXE%" manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Migration check completed with notices.
) else (
    echo       [OK] Database up to date.
)
echo.

:: [5/5] Launch browser & run server
echo [5/5] Launching browser and starting server...
start http://127.0.0.1:8000/

echo.
echo ====================================================================
echo   ✦ Website URL:         http://127.0.0.1:8000/
echo   ✦ Academy Masterclass: http://127.0.0.1:8000/academy/
echo   ✦ Gameplay Masterclass:http://127.0.0.1:8000/gameplay/
echo   ✦ Django Admin Portal: http://127.0.0.1:8000/admin-portal/
echo.
echo   Press CTRL + C in this terminal window to stop the server.
echo ====================================================================
echo.

"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000

pause
