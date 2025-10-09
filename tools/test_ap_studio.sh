#!/bin/bash
# test_ap_studio.sh - Test AP Studio Setup
#
# AP Studio Quick Guide:
# =====================
# 
# What is AP Studio?
# - Web-based IDE for Analytic Programming
# - Brainstorming-first workflow (AI creates PRD.md)
# - Multi-agent orchestration (Claude, GPT-4, Codex)
# - Real-time WebSocket updates
# - Dark Forest theme with animations
#
# Quick Start (5 minutes):
# 1. Install: pip install -r requirements.txt
# 2. Set API key: export OPENAI_API_KEY='sk-...'
# 3. Start backend: python ap_studio_backend.py
# 4. Open UI: open ap_studio.html (or http://localhost:8000)
#
# Workflow:
# 1. Brainstorm with AI → Creates PRD.md in real-time
# 2. Click "🚀 Spustiť Orchestráciu" → Multi-agent execution
# 3. Results saved in projects/<name>/v0.01/ (separate Git repo)
#
# Architecture:
# - Frontend: ap_studio.html (WebSocket client)
# - Backend: ap_studio_backend.py (FastAPI + WebSocket)
# - Agents: brainstorm_agent_mcp.py (MCP-enhanced)
# - Database: ap_studio_db.py (SQLite)
# - Version: version_manager.py (Git operations)
#
# Troubleshooting:
# - WebSocket fails → Check backend running on port 8000
# - AI not responding → Check OPENAI_API_KEY set
# - Git errors → Check git config (user.name, user.email)
#
# Run from project root: ./tools/test_ap_studio.sh
# =====================

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
    echo -e "${RED}✗${NC} Missing - Run: pip install fastapi"
fi

echo -n "4. OpenAI... "
if python -c "from openai import OpenAI" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed (v1.0+)"
else
    echo -e "${RED}✗${NC} Missing - Run: pip install openai"
fi

echo -n "5. GitPython... "
if python -c "import git" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${RED}✗${NC} Missing - Run: pip install gitpython"
fi

echo -n "6. MCP-Use... "
if python -c "import mcp_use" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC}  Missing - Run: pip install mcp-use"
fi

echo -n "7. LangChain... "
if python -c "import langchain" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installed"
else
    echo -e "${YELLOW}⚠${NC}  Missing - Run: pip install langchain langchain-openai"
fi

# Test 4: Environment variables
echo ""
echo -n "8. OPENAI_API_KEY... "
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC}  Not set"
    echo "   Set it: export OPENAI_API_KEY='sk-...'"
else
    echo -e "${GREEN}✓${NC} Set"
fi

# Test 5: Files
echo ""
echo -n "9. Database module... "
if [ -f "ap_studio_db.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "10. Backend module... "
if [ -f "ap_studio_backend.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

echo -n "11. MCP Brainstorm agent... "
if [ -f "brainstorm_agent_mcp.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC}  Missing (fallback: brainstorm_agent.py)"
fi

echo -n "12. Project workspace... "
if [ -f "project_workspace.py" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC}  Missing"
fi

echo -n "13. UI file... "
if [ -f "ap_studio.html" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${RED}✗${NC} Missing"
fi

# Test 6: Database initialization
echo ""
echo -n "14. Database init... "
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
echo "✅ Setup test complete!"
echo ""
echo "📋 Quick Start:"
echo "  1. Set API key:"
echo "     export OPENAI_API_KEY='sk-...'"
echo ""
echo "  2. Start backend:"
echo "     python ap_studio_backend.py"
echo ""
echo "  3. Open UI (choose one):"
echo "     - Direct: open ap_studio.html"
echo "     - HTTP: http://localhost:8000"
echo ""
echo "🎯 Workflow:"
echo "  Brainstorm → PRD.md → Orchestration → Implementation"
echo ""
echo "📚 More info in script header (line 4-37)"
echo ""

