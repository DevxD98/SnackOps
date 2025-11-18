#!/bin/bash

# ChefByte UI Launcher Script
# This script activates the virtual environment and launches the Gradio UI

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================"
echo "  🍳 ChefByte - AI Meal Planning Agent"
echo "============================================"
echo -e "${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Please create .env file with your GOOGLE_API_KEY"
    echo "Example:"
    echo "  GOOGLE_API_KEY=your_key_here"
    exit 1
fi

# Activate venv and launch UI
echo -e "${GREEN}Starting ChefByte UI...${NC}"
echo ""

source venv/bin/activate
python ui/gradio_adk_ui.py
