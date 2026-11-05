@echo off
setlocal
title cOCR Workbench

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
)

%PYTHON_CMD% main.py %*
if errorlevel 1 pause
