#!/bin/bash
# test_ap_studio.sh - Test AP Studio Setup

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            🌲 AP Studio Setup Test 🌲                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Python version
echo -n "1. Python version... "
python_version=$(python --version 2>&1)
if [[ $python_version == *"Python 3."* ]]; then
    echo -e "${GREEN}✓${NC} $python_version"
else
    echo -e "${RED}✗${NC} Python 3 required"
    exit 1
fi

# Test 2: Virtual environment
echo -n "2. Virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC}  Creating venv..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate

# Test 3: Dependencies
echo -n "3. FastAPI... "
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "4. OpenAI... "
if python -c "from openai import OpenAI" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed (v1.0+)"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "5. GitPython... "
if python -c "import git" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${RED}✗${NC} Missing"
fi

# Test 4: Environment variables
echo ""
echo -n "6. OPENAI_API_KEY... "
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC}  Not set"
    echo "   Set it: export OPENAI_API_KEY='sk-...'"
else
    echo -e "${GREEN}✓${NC} Set"
fi

# Test 5: Files
echo ""
echo -n "7. Database module... "
if [ -f "ap_studio_db.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "8. Backend module... "
if [ -f "ap_studio_backend.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "9. Brainstorm agent... "
if [ -f "brainstorm_agent.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "10. UI file... "
if [ -f "ap_studio.html" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

# Test 6: Database initialization
echo ""
echo -n "11. Database init... "
python ap_studio_db.py > /dev/null 2>&1
if [ -f "test_ap_studio.db" ]; then
    echo -e "${GREEN}✓${NC} Working"
    rm test_ap_studio.db
else
    echo -e "${RED}✗${NC} Failed"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Set OPENAI_API_KEY: export OPENAI_API_KEY='sk-...'"
echo "  2. Start backend: python ap_studio_backend.py"
echo "  3. Open UI: open ap_studio.html"
echo ""
echo "📖 Documentation: AP_STUDIO_QUICKSTART.md"
echo ""

