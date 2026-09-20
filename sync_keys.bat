@echo off
setlocal
echo =======================================================
echo        Universal AI Key Synchronizer (Akshat)
echo =======================================================
python "%~dp0scripts\sync_keys.py" %*
pause
