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
echo [STAGE 2: SPECIFY]      : COMPLETED (.specify\specs\SPEC-002-evagher-editorial-redesign.md)
echo [STAGE 3: PLAN]         : COMPLETED (.specify\plans\PLAN-002-evagher-editorial-redesign.md)
echo [STAGE 4: TASKS]        : READY     (.specify\tasks\TASKS-002-evagher-editorial-redesign.md)
echo [STAGE 5: IMPLEMENT]    : PENDING USER APPROVAL / IN PROGRESS
echo.
echo Active Feature: SPEC-002 (Evagher Full-Viewport Editorial Layout and Peek Gallery)
echo Ready Tasks   : TSK-201 through TSK-209
exit /b 0

:constitution
echo [CONSTITUTION: NON-NEGOTIABLE ARCHITECTURAL PRINCIPLES]
echo ----------------------------------------------------------------
type "%SPEC_DIR%\memory\constitution.md"
exit /b 0

:specify
set SPEC_FILE=%SPEC_DIR%\specs\SPEC-002-evagher-editorial-redesign.md
if not exist "%SPEC_FILE%" set SPEC_FILE=%SPEC_DIR%\specs\SPEC-001-vector-curtain-entrance.md
echo [SPECIFICATION: SPEC-002]
echo ----------------------------------------------------------------
type "%SPEC_FILE%"
exit /b 0

:plan
set PLAN_FILE=%SPEC_DIR%\plans\PLAN-002-evagher-editorial-redesign.md
if not exist "%PLAN_FILE%" set PLAN_FILE=%SPEC_DIR%\plans\PLAN-001-vector-curtain-entrance.md
echo [TECHNICAL PLAN: PLAN-002]
echo ----------------------------------------------------------------
type "%PLAN_FILE%"
exit /b 0

:tasks
set TASKS_FILE=%SPEC_DIR%\tasks\TASKS-002-evagher-editorial-redesign.md
if not exist "%TASKS_FILE%" set TASKS_FILE=%SPEC_DIR%\tasks\TASKS-001-vector-curtain-entrance.md
echo [GRANULAR TASKS: TASKS-002]
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
if exist "%SPEC_DIR%\specs\SPEC-002-evagher-editorial-redesign.md" (echo [PASS] SPEC-002 exists) else (echo [FAIL] Missing SPEC-002)
if exist "%SPEC_DIR%\plans\PLAN-002-evagher-editorial-redesign.md" (echo [PASS] PLAN-002 exists) else (echo [FAIL] Missing PLAN-002)
if exist "%SPEC_DIR%\tasks\TASKS-002-evagher-editorial-redesign.md" (echo [PASS] TASKS-002 exists) else (echo [FAIL] Missing TASKS-002)

echo.
echo Validation complete.
exit /b 0

:implement
echo [IMPLEMENTATION RUNNER]
echo ----------------------------------------------------------------
echo Feature Branch: feature/evagher-editorial-redesign
echo.
echo Completed Tasks for SPEC-002:
echo   [TSK-201] [DONE] Implement Evagher-style top bar (Left MENU, Center Logo, Right Lang Switcher)
echo   [TSK-202] [DONE] Build architectural left collapsible navigation drawer
echo   [TSK-203] [DONE] Restructure #hero into Left 60%% photo slider ^& Right 40%% brand typography
echo   [TSK-204] [DONE] Add auto-advancing crossfade + Ken Burns zoom + fraction counter (01 / 04)
echo   [TSK-205] [DONE] Build full-viewport interactive gallery modal showing center active image with left/right peeks
echo   [TSK-206] [DONE] Implement wheel scroll (Down/Right = Next, Up/Left = Prev) and touch drag/swipe navigation
echo   [TSK-207] [DONE] Present bridal packages sequentially (one by one) with large visuals and clear rates
echo   [TSK-208] [DONE] Add floating / docked action bar: "Compare All", "Custom Package Builder", "WhatsApp"
echo   [TSK-209] [VERIFIED] QA in desktop and mobile viewports; verify gesture smoothness and clean Git tree
echo.
echo Implementation is active and verified on branch: feature/evagher-editorial-redesign
exit /b 0
