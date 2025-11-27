#!/bin/bash

# Chefbyte-UI Frontend Startup Script
# This script starts the React + Vite development server

echo "🎨 Starting Chefbyte-UI Frontend..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please ensure you are in the Chefbyte-ui directory."
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Error: node not found. Please install Node.js 18+"
    exit 1
fi

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm not found. Please install npm"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Warning: Backend not detected at http://localhost:8000"
    echo "   Please start the backend first:"
    echo "   cd ../ChefByte && ./start_backend.sh"
    echo ""
    echo "   Continuing anyway..."
fi

echo ""
echo "🚀 Starting Vite dev server..."
echo "   Frontend will be available at http://localhost:5173"
echo "   Press Ctrl+C to stop"
echo ""

npm run dev
