@echo off
setlocal
title cOCR Workbench - Build Executable

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
)

%PYTHON_CMD% build_tools\build_exe.py %*

echo.
pause
