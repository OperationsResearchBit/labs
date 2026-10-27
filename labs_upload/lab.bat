@echo off
setlocal
title bgtools lab
rem Double-click for the lab menu, or:  lab.bat check my_idea
cd /d "%~dp0..\.." || (echo Could not find the repo root. & pause & exit /b 1)
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY (
    echo Python was not found. Install Python 3 from python.org and tick "Add Python to PATH".
    pause
    exit /b 1
)
%PY% build_and_test\lab\lab.py %*
set "RC=%ERRORLEVEL%"
if "%~1"=="" exit /b 0
if defined LAB_NOPAUSE exit /b %RC%
pause
exit /b %RC%
