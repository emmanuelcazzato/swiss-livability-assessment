@echo off
REM Swiss Livability Assessment - Web Application Launcher
REM Quick start script for Windows users

echo ================================================================================
echo SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT
echo Web Application Launcher
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.9 or higher.
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo √ Python found
echo.

REM Check if required packages are installed
echo Checking required packages...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ! Flask not installed. Installing required packages...
    pip install flask pandas numpy scikit-fuzzy scipy networkx matplotlib seaborn
    if errorlevel 1 (
        echo X Failed to install packages. Please run manually:
        echo   pip install flask pandas numpy scikit-fuzzy scipy networkx
        pause
        exit /b 1
    )
)

echo √ All packages installed
echo.

REM Check if data file exists
if not exist "data\processed\dwellings_sample.csv" (
    echo ! Sample data not found. Creating sample dataset...
    python create_sample_data.py
    if errorlevel 1 (
        echo X Failed to create sample data
        pause
        exit /b 1
    )
    echo √ Sample data created
    echo.
)

REM Start the web application
echo ================================================================================
echo Starting web server...
echo.
echo   Open your browser and go to: http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo ================================================================================
echo.

python web_app.py

pause

