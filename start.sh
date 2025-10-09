#!/bin/bash
# AP Studio Launcher
# Quick start script for Analytic Programming Studio

echo "🎭 AP STUDIO v1.0.0"
echo "===================="
echo ""

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set!"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE"
    echo ""
    echo "Or add to ~/.bashrc:"
    echo "  echo 'export OPENAI_API_KEY=sk-proj-...' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
    exit 1
fi

echo "✓ OpenAI API key configured"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import fastapi, uvicorn, openai, git, websockets, aiofiles" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies! Installing..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ All dependencies installed"
echo ""

# Seed workers (if database empty)
if [ ! -f "ap_studio.db" ]; then
    echo "Seeding test workers..."
    python3 seed_workers.py
    echo "✓ Test workers added"
    echo ""
fi

# Start backend
echo "🚀 Starting AP Studio Backend..."
echo ""
echo "Access AP Studio at: http://localhost:8000"
echo ""
echo "Press CTRL+C to stop"
echo "===================="
echo ""

python3 ap_studio_backend.py

