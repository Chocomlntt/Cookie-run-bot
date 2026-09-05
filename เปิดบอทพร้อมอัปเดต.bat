@echo off
title CookieRun AutoBot Launcher
cls
echo ==================================================
echo   CookieRun AutoBot Launcher ^& Auto-Updater
echo ==================================================
echo.
echo [1/3] Updating latest code from GitHub...
git pull
echo.
echo [2/3] Installing required Python libraries...
python -m pip install customtkinter opencv-python pillow numpy
echo.
echo [3/3] Starting CookieRun AutoBot GUI...
python gui_bot.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error launching gui_bot.py!
    pause
)
