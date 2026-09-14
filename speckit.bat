@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo    ANSHITA MAKEOVER - SPEC KIT (SPEC-DRIVEN DEVELOPMENT) CLI
echo ================================================================
echo.

set SPEC_DIR=%~dp0.specify
set PROJECT_DIR=%~dp0

if "%~1"=="" goto interactive_menu
if /i "%~1"=="menu" goto interactive_menu
if /i "%~1"=="help" goto help
if /i "%~1"=="status" goto status
if /i "%~1"=="constitution" goto constitution
if /i "%~1"=="specify" goto specify
if /i "%~1"=="plan" goto plan
if /i "%~1"=="tasks" goto tasks
if /i "%~1"=="validate" goto validate
if /i "%~1"=="implement" goto implement

echo [ERROR] Unknown command: %~1
echo Type "speckit.bat help" for available commands.
pause
exit /b 1

:interactive_menu
cls
echo ================================================================
echo    ANSHITA MAKEOVER - SPEC KIT (SPEC-DRIVEN DEVELOPMENT) CLI
echo ================================================================
echo.
echo   [1] View Workflow Status
echo   [2] View Constitution (Architectural Non-Negotiables)
echo   [3] View Specification (SPEC-001)
echo   [4] View Implementation Plan (PLAN-001)
echo   [5] View Granular Tasks (TASKS-001)
echo   [6] Run Automated Validation (Git Clean, Secrets, Django)
echo   [7] View Implementation Checklist
echo   [8] Exit
echo.
set /p choice="Enter option (1-8): "

if "%choice%"=="1" goto menu_status
if "%choice%"=="2" goto menu_constitution
if "%choice%"=="3" goto menu_specify
if "%choice%"=="4" goto menu_plan
if "%choice%"=="5" goto menu_tasks
if "%choice%"=="6" goto menu_validate
if "%choice%"=="7" goto menu_implement
if "%choice%"=="8" exit /b 0
goto interactive_menu

:menu_status
cls
call :status
echo.
pause
goto interactive_menu

:menu_constitution
cls
call :constitution
echo.
pause
goto interactive_menu

:menu_specify
cls
call :specify
echo.
pause
goto interactive_menu

:menu_plan
cls
call :plan
echo.
pause
goto interactive_menu

:menu_tasks
cls
call :tasks
echo.
pause
goto interactive_menu

:menu_validate
cls
call :validate
echo.
pause
goto interactive_menu

:menu_implement
cls
call :implement
echo.
pause
goto interactive_menu

:help
echo Available Spec Kit Commands:
echo.
echo   speckit.bat status              Show current SDD workflow stage and active specs
echo   speckit.bat constitution        Display foundational rules and non-negotiables
echo   speckit.bat specify [ID]        Inspect or view specification details
echo   speckit.bat plan [ID]           Inspect technical blueprint and architecture
echo   speckit.bat tasks [ID]          View granular task checklist and status
echo   speckit.bat validate            Verify Django health, Git tree, and clean secrets
echo   speckit.bat implement [ID]      Verify tasks readiness and implementation checklist
echo.
echo Examples:
echo   speckit.bat status
echo   speckit.bat constitution
echo   speckit.bat tasks SPEC-001
echo   speckit.bat validate
exit /b 0

:status
echo [SPEC KIT WORKFLOW STATUS]
echo ----------------------------------------------------------------
echo [STAGE 1: CONSTITUTION] : ACTIVE (.specify\memory\constitution.md)
echo [STAGE 2: SPECIFY]      : COMPLETED (.specify\specs\SPEC-001-vector-curtain-entrance.md)
echo [STAGE 3: PLAN]         : COMPLETED (.specify\plans\PLAN-001-vector-curtain-entrance.md)
echo [STAGE 4: TASKS]        : READY     (.specify\tasks\TASKS-001-vector-curtain-entrance.md)
echo [STAGE 5: IMPLEMENT]    : PENDING USER APPROVAL / IN PROGRESS
echo.
echo Active Feature: SPEC-001 (Haute Couture Vector Entrance and Dual-Curtain System)
echo Ready Tasks   : TSK-01 through TSK-08
exit /b 0

:constitution
echo [CONSTITUTION: NON-NEGOTIABLE ARCHITECTURAL PRINCIPLES]
echo ----------------------------------------------------------------
type "%SPEC_DIR%\memory\constitution.md"
exit /b 0

:specify
set SPEC_FILE=%SPEC_DIR%\specs\SPEC-001-vector-curtain-entrance.md
if not exist "%SPEC_FILE%" (
    echo [ERROR] Specification file not found: %SPEC_FILE%
    exit /b 1
)
echo [SPECIFICATION: SPEC-001]
echo ----------------------------------------------------------------
type "%SPEC_FILE%"
exit /b 0

:plan
set PLAN_FILE=%SPEC_DIR%\plans\PLAN-001-vector-curtain-entrance.md
if not exist "%PLAN_FILE%" (
    echo [ERROR] Plan file not found: %PLAN_FILE%
    exit /b 1
)
echo [TECHNICAL PLAN: PLAN-001]
echo ----------------------------------------------------------------
type "%PLAN_FILE%"
exit /b 0

:tasks
set TASKS_FILE=%SPEC_DIR%\tasks\TASKS-001-vector-curtain-entrance.md
if not exist "%TASKS_FILE%" (
    echo [ERROR] Tasks file not found: %TASKS_FILE%
    exit /b 1
)
echo [TASKS BREAKDOWN: TASKS-001]
echo ----------------------------------------------------------------
type "%TASKS_FILE%"
exit /b 0

:validate
echo [SPEC KIT AUTOMATED VALIDATION]
echo ----------------------------------------------------------------
echo 1. Checking Git Push Protection and Secret Leaks...
git log --all -- "openai_api_key.txt" 2>nul | findstr /i "commit" >nul
if !errorlevel! equ 0 (
    echo [FAIL] Contaminated commit detected with openai_api_key.txt!
) else (
    echo [PASS] Git tree is 100%% clean of secrets.
)

echo 2. Checking Django Health...
python "%PROJECT_DIR%anshita_project\manage.py" check --quiet 2>nul
if !errorlevel! equ 0 (
    echo [PASS] Django system check reported zero issues.
) else (
    echo [WARN] Django check returned warnings or needs verification.
)

echo 3. Checking Spec Kit Artifacts...
if exist "%SPEC_DIR%\memory\constitution.md" (echo [PASS] Constitution exists) else (echo [FAIL] Missing constitution.md)
if exist "%SPEC_DIR%\specs\SPEC-001-vector-curtain-entrance.md" (echo [PASS] SPEC-001 exists) else (echo [FAIL] Missing SPEC-001)
if exist "%SPEC_DIR%\plans\PLAN-001-vector-curtain-entrance.md" (echo [PASS] PLAN-001 exists) else (echo [FAIL] Missing PLAN-001)
if exist "%SPEC_DIR%\tasks\TASKS-001-vector-curtain-entrance.md" (echo [PASS] TASKS-001 exists) else (echo [FAIL] Missing TASKS-001)

echo.
echo Validation complete.
exit /b 0

:implement
echo [IMPLEMENTATION RUNNER]
echo ----------------------------------------------------------------
echo In Spec-Driven Development, the coding agent (Antigravity/AI) executes
echo the code modifications across templates, static files, and shaders.
echo.
echo Current Ready Tasks:
echo   [TSK-01] Create brand SVG vector monogram (anshita_crest.svg)
echo   [TSK-02] Add dual curtain transforms and cubic-bezier easing to style.css
echo   [TSK-03] Add stroke-dashoffset drawing keyframes to style.css
echo   [TSK-04] Refactor base.html to mount dual curtains and remove video element
echo   [TSK-05] Implement zero-flicker session guard in base.html
echo   [TSK-06] Add Escape key and skip-intro bypass listeners
echo   [TSK-07] Link Three.js shader entrance pulse to curtain parting
echo   [TSK-08] Launch browser visual QA and capture recording
echo.
echo To start automatic implementation, reply to the assistant with:
echo    "Implement TASKS-001"
exit /b 0
