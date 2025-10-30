#!/bin/bash

# Swiss Livability Assessment - Web Application Launcher
# Quick start script for Mac/Linux users

echo "================================================================================"
echo "SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT"
echo "Web Application Launcher"
echo "================================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if required packages are installed
echo "Checking required packages..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask not installed. Installing required packages..."
    pip3 install flask pandas numpy scikit-fuzzy scipy networkx matplotlib seaborn
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages. Please run manually:"
        echo "   pip3 install flask pandas numpy scikit-fuzzy scipy networkx"
        exit 1
    fi
fi

echo "✅ All packages installed"
echo ""

# Check if data file exists
if [ ! -f "data/processed/dwellings_sample.csv" ]; then
    echo "⚠️  Sample data not found. Creating sample dataset..."
    python3 create_sample_data.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create sample data"
        exit 1
    fi
    echo "✅ Sample data created"
    echo ""
fi

# Start the web application
echo "================================================================================"
echo "🚀 Starting web server..."
echo ""
echo "   Open your browser and go to: http://localhost:5000"
echo ""
echo "   Press Ctrl+C to stop the server"
echo "================================================================================"
echo ""

python3 web_app.py

