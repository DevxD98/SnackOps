#!/bin/bash
set -euo pipefail

# ChefByte Backend Startup Script (hardened)
# Safely starts FastAPI backend with port + env checks

echo "🍳 Starting ChefByte Backend (safe mode)..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if we're in the right directory (double check)
if [ ! -f "api.py" ]; then
    echo "❌ Error: api.py not found. Please ensure you are in the ChefByte directory."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Load .env if present (without overriding already exported vars)
if [ -f .env ]; then
    echo "🌱 Loading .env variables..."
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs -I {} sh -c 'echo {}' | awk -F= '{print $1}') >/dev/null 2>&1 || true
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

PORT="${PORT:-8000}"

# Check for GOOGLE_API_KEY
if [ -z "${GOOGLE_API_KEY:-}" ] && [ -z "${GEMINI_API_KEY:-}" ]; then
        echo ""
        echo "⚠️  Warning: GOOGLE_API_KEY or GEMINI_API_KEY not set!"
        echo "   Set it before running for agent tools to work:"
        echo "   export GOOGLE_API_KEY='your-api-key-here'"
        echo ""
fi

# Detect existing process on port
if lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "⛔ Port $PORT already in use. Showing processes:";
    lsof -i :"$PORT" -sTCP:LISTEN
    echo ""
    read -r -p "Kill existing process and restart? (y/N): " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        existing_pid=$(lsof -ti :"$PORT" -sTCP:LISTEN | head -1)
        if [ -n "$existing_pid" ]; then
            echo "🔪 Killing PID $existing_pid"
            kill "$existing_pid" || true
            sleep 2
        fi
    else
        echo "🚪 Aborting start. Use a different port: PORT=8001 ./start_backend.sh"
        exit 1
    fi
fi

# Start the server (use uvicorn for better reload behavior)
echo ""
echo "🚀 Starting FastAPI server on http://localhost:$PORT" 
echo "   Press Ctrl+C to stop"
echo ""

exec uvicorn api:app --host 0.0.0.0 --port "$PORT" --workers 1
