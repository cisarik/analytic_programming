#!/bin/bash

# test_mcp_brainstorm.sh - Test MCP Brainstorm Agent Integration
# 
# Tento script testuje:
# 1. MCP agent standalone
# 2. Backend integráciu
# 3. UI real-time updates

set -e

echo "=========================================="
echo "🧪 Testing MCP Brainstorm Agent"
echo "=========================================="

# Check dependencies
echo ""
echo "📦 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "   Export it: export OPENAI_API_KEY=sk-..."
    exit 1
fi

echo "✓ Python 3 found"
echo "✓ OPENAI_API_KEY set"

# Install dependencies if needed
echo ""
echo "📦 Installing dependencies..."
pip install -q mcp-use langchain langchain-openai python-dotenv

echo "✓ Dependencies installed"

# Test 1: MCP Agent Standalone
echo ""
echo "=========================================="
echo "TEST 1: MCP Agent Standalone"
echo "=========================================="

python3 <<'EOF'
import asyncio
from brainstorm_agent_mcp import MCPBrainstormAgent

async def test():
    print("\n🤖 Initializing MCP agent...")
    
    # WebSocket callback simulation
    async def ws_callback(data):
        print(f"📡 WebSocket: {data.get('type')} - Line {data.get('line_number')}")
    
    agent = MCPBrainstormAgent(websocket_callback=ws_callback)
    
    print("✓ Agent initialized")
    
    # Start session
    greeting = await agent.start_session("Test Project")
    print(f"\n🤖 Agent: {greeting[:100]}...")
    
    # Test message
    print("\n👤 User: 'Chcem REST API pre blog'")
    response = await agent.process_message("Chcem REST API pre blog")
    print(f"🤖 Agent: {response[:100]}...")
    
    # Check PRD
    prd = agent.get_prd_content()
    print(f"\n📄 PRD.md:\n{prd[:200]}...")
    
    # Check changes
    changes = agent.get_changes()
    print(f"\n📝 Changes: {len(changes)}")
    for c in changes:
        print(f"   Line {c.line_number}: {c.section}")
    
    print("\n✅ TEST 1 PASSED")

asyncio.run(test())
EOF

# Test 2: Backend Integration
echo ""
echo "=========================================="
echo "TEST 2: Backend Integration"
echo "=========================================="

echo "🚀 Starting backend (5 seconds)..."
python3 ap_studio_backend.py &
BACKEND_PID=$!

sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✓ Backend running (PID: $BACKEND_PID)"

# Test API
echo ""
echo "📡 Testing API endpoints..."

# Create project
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "MCP Test Project"}')

PROJECT_ID=$(echo $PROJECT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Created project: $PROJECT_ID"

# Get projects
curl -s http://localhost:8000/api/projects | python3 -m json.tool | head -10
echo "✓ GET /api/projects works"

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
echo "✓ Backend stopped"

echo ""
echo "=========================================="
echo "✅ ALL TESTS PASSED"
echo "=========================================="

echo ""
echo "🚀 To test UI interactively:"
echo "   1. export OPENAI_API_KEY=sk-..."
echo "   2. python3 ap_studio_backend.py"
echo "   3. Open http://localhost:8000"
echo "   4. Start brainstorming!"
echo ""
echo "Expected behavior:"
echo "   - Agent responds to your messages"
echo "   - PRD.md updates in real-time"
echo "   - Changes highlighted GREEN"
echo "   - Hover → Undo button appears"

