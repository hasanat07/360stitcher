@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Install Python 3 from python.org first. & pause & exit /b 1)
py -3 -m venv .buildenv || goto :error
".buildenv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller || goto :error
".buildenv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name 360Stitcher --icon assets\app.ico --add-data "assets;assets" app.py || goto :error
echo Ready: dist\360Stitcher.exe
pause
exit /b 0
:error
echo Build failed. Check the error above.
pause
exit /b 1
