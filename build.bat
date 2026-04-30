@echo off
setlocal
echo === TodoPet build ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not on PATH. Install Python 3.10+ from python.org and try again.
    pause
    exit /b 1
)

echo [1/3] Installing build dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Building TodoPet.exe with PyInstaller...
python -m PyInstaller --onefile --windowed --name TodoPet --noconfirm --clean todo_app.py
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done!
echo.
echo Your app is at:  %CD%\dist\TodoPet.exe
echo.
echo Double-click that .exe to run. You can copy it anywhere, pin it to taskbar,
echo or place a shortcut in shell:startup to launch on login.
echo.
pause
