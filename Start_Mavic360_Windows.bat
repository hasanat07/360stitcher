@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    where python >nul 2>nul && set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo Python 3 is required for the first launch.
    echo Install it from https://www.python.org/downloads/windows/ and enable "Add python.exe to PATH".
    echo Then double-click this file again.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo Setting up the panorama app. Internet is needed on the first launch.
    %PYTHON_CMD% -m venv .venv || goto :error
)
".venv\Scripts\python.exe" -c "import cv2, PIL, numpy, scipy" >nul 2>nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto :error
exit /b 0
:error
echo The app could not start. See the error above.
pause
exit /b 1
