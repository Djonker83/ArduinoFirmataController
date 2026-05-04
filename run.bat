@echo off
echo Starting Arduino Firmata Controller...
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in your PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
pip show pyserial >nul 2>&1
if errorlevel 1 (
    echo Installing pyserial...
    pip install pyserial
)

pip show pyfirmata >nul 2>&1
if errorlevel 1 (
    echo Installing pyfirmata...
    pip install pyfirmata
)

pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo Installing PyQt6...
    pip install PyQt6
)

echo.
echo Starting GUI application...
python src\main.py

if errorlevel 1 (
    echo.
    echo The application encountered an error and closed.
    echo Make sure your Arduino is connected and running the StandardFirmata sketch.
    pause
)