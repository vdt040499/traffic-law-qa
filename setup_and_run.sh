#!/bin/bash

echo "🚦 Vietnamese Traffic Law QA System - Setup & Run"
echo "================================================"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔄 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "🔄 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install basic requirements"
    exit 1
fi

pip install -r requirements-knowledge.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install knowledge graph requirements"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check if data exists
if [ ! -f "data/processed/violations_100.json" ]; then
    echo "⚠️  Warning: violations_100.json not found"
    echo "Please ensure data is properly processed"
fi

echo ""
echo "🎯 Setup completed! Choose an option:"
echo ""
echo "[1] Run Quick Demo"
echo "[2] Run Web Interface"
echo "[3] Run Tests"
echo "[4] Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting demo..."
        python demo.py
        ;;
    2)
        echo "🚀 Starting web interface..."
        echo "Opening browser at http://localhost:8501"
        cd src/traffic_law_qa/ui
        streamlit run streamlit_app.py
        ;;
    3)
        echo "🧪 Running tests..."
        python test_knowledge_system.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac