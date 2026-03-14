@echo off
title SafeDrive.ai Launcher
color 0C
cls
echo.
echo  =============================================
echo    SafeDrive.ai - Driver Safety System
echo  =============================================
echo.
echo  [1]  Open Dashboard in Chrome  (No install needed)
echo  [2]  Run Flask Server          (pip install first)
echo  [3]  Run Python Detector       (all modules, OpenCV)
echo  [4]  Install Python packages
echo  [5]  Test Drowsiness only
echo  [6]  Test Emotion only
echo  [7]  Test Visibility only
echo.
set /p choice=" Enter choice (1-7): "

if "%choice%"=="1" (
    echo Opening frontend\index.html in Chrome...
    start "" "frontend\index.html"
    echo Done! Use Chrome or Edge.
    pause & exit
)
if "%choice%"=="2" (
    echo Starting Flask at http://localhost:5000
    cd backend & python app.py
    pause & exit
)
if "%choice%"=="3" (
    echo Running all modules (E=engine, Q=quit)...
    cd backend & python run_all.py
    pause & exit
)
if "%choice%"=="4" (
    echo Installing packages...
    pip install -r requirements.txt
    echo Done!
    pause & exit
)
if "%choice%"=="5" (
    cd backend & python drowsiness_detection.py
    pause & exit
)
if "%choice%"=="6" (
    cd backend & python emotion_detection.py
    pause & exit
)
if "%choice%"=="7" (
    cd backend & python visibility_detection.py
    pause & exit
)
echo Invalid choice.
pause
