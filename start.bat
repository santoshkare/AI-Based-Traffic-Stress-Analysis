@echo off
title SafeDrive.ai v3.0 Launcher
color 0B
cls
set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"
echo.
echo  ============================================
echo    SafeDrive.ai v3.0 - Driver Safety System
echo  ============================================
echo.
echo  [1]  Open Dashboard in Browser   (No install)
echo  [2]  Run Flask Server            (Full features)
echo  [3]  Run Python Detector         (OpenCV window)
echo  [4]  Install Python packages
echo  [5]  Test Drowsiness module
echo  [6]  Test Emotion module
echo  [7]  Test Visibility module
echo  [8]  Test Risk Engine
echo.
set /p choice=" Enter choice (1-8): "

if "%choice%"=="1" (
    echo Opening frontend\index.html in browser...
    start "" "frontend\index.html"
    echo Done! Use Chrome or Edge for best results.
    pause & exit
)
if "%choice%"=="2" (
    echo Starting Flask at http://localhost:5000
    echo Login: demo@test.com / demo1234
    cd backend & ..\%PYTHON% app.py
    pause & exit
)
if "%choice%"=="3" (
    echo Running all modules (E=engine, R=reset, Q=quit)...
    cd backend & ..\%PYTHON% run_all.py
    pause & exit
)
if "%choice%"=="4" (
    echo Installing packages from requirements.txt...
    %PYTHON% -m pip install -r requirements.txt
    echo.
    echo Done! You can now use options 2 or 3.
    pause & exit
)
if "%choice%"=="5" (
    cd backend & ..\%PYTHON% drowsiness_detection.py
    pause & exit
)
if "%choice%"=="6" (
    cd backend & ..\%PYTHON% emotion_detection.py
    pause & exit
)
if "%choice%"=="7" (
    cd backend & ..\%PYTHON% visibility_detection.py
    pause & exit
)
if "%choice%"=="8" (
    cd backend & ..\%PYTHON% risk_engine.py
    pause & exit
)
echo Invalid choice. Please enter 1-8.
pause
