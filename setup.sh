#!/bin/bash

# PantryPilot Setup Script
# This script sets up the virtual environment and installs all dependencies

echo "🍳 PantryPilot Setup Script"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the Gradio UI:"
echo "  python ui/gradio_ui.py"
echo ""
echo "To run the Jupyter notebook:"
echo "  jupyter notebook notebook/PantryPilot_Demo.ipynb"
echo ""
echo "Don't forget to set your GEMINI_API_KEY in the .env file!"
