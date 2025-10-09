# 🚀 START AP STUDIO - Quick Start Guide

**Date**: October 9, 2025  
**Version**: 1.0.0  
**Time to start**: < 2 minutes

## ⚡ Fastest Way to Start

```bash
cd /home/agile/analytic_programming

# 1. Set OpenAI API key
export OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE

# 2. Start backend
python ap_studio_backend.py

# 3. Open browser → http://localhost:8000
```

**That's it!** 🎉

## 📋 Full Instructions

### Prerequisites
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Dependencies:
# - fastapi>=0.104.0
# - uvicorn>=0.24.0
# - openai>=1.3.0
# - GitPython>=3.1.40
# - websockets>=12.0
# - aiofiles>=24.1.0
```

### Step 1: Set OpenAI API Key
```bash
export OPENAI_API_KEY=sk-proj-...

# Or add to ~/.bashrc or ~/.zshrc:
echo 'export OPENAI_API_KEY=sk-proj-...' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Start Backend
```bash
cd /home/agile/analytic_programming
python ap_studio_backend.py
```

**Expected output**:
```
🚀 AP Studio Backend starting...
✓ Database initialized: ap_studio.db
✓ Version manager initialized: projects/
✓ Brainstorm agent initialized
✓ WebSocket manager initialized
✓ Orchestration launcher initialized

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 3: Open Web UI
Open browser:
```
http://localhost:8000
```

Or from terminal:
```bash
firefox http://localhost:8000
# or
google-chrome http://localhost:8000
# or
xdg-open http://localhost:8000
```

## 🎨 Using AP Studio

### Tab 1: Brainstorming (Phase 0) 🧠

**Purpose**: Interactively create PRD.md with AI assistant

**Workflow**:
1. Type your project idea: "Chcem vytvoriť REST API pre blog..."
2. Assistant asks clarifying questions
3. Watch PRD.md build in real-time (right panel)
4. When satisfied, click **"Spustiť Orchestráciu"** button

**Example conversation**:
```
You: Chcem vytvoriť REST API pre blog s autentifikáciou

AI: Skvelé! Aké hlavné funkcie by mal blog obsahovať? (napr. články, komentáre, kategórie...)

You: Články s markdown, kategórie, tagy, vyhľadávanie

AI: Rozumiem. Aká databáza? (SQLite, PostgreSQL...)

You: SQLite pre jednoduchosť

AI: Perfektne! A backend framework? (FastAPI, Flask...)

You: FastAPI

[PRD.md sa buduje v reálnom čase v pravom paneli]
```

**Features**:
- ✅ Real-time PRD.md preview (markdown rendering)
- ✅ Chat history saved to database
- ✅ Can resume brainstorming later
- ✅ OpenAI GPT-4 powered
- ✅ Slovak/English bilingual support

### Tab 2: Workers 🤖

**Purpose**: Manage MCP workers (AI coding agents)

**Actions**:
- **Add Worker**: Click "Add Worker" button
  - Worker ID: `claude-main`
  - Agent Type: `claude`
  - Command: `claude-mcp-server`
  - Args: `--stdio`
  - Max Concurrent: `3`
  
- **Discover Capabilities**: Click "Discover" on worker card
  - Queries worker for available tools
  - Uses OpenAI to analyze capabilities
  - Auto-generates capability tags: `["python", "refactoring", "testing"]`

- **Toggle Enable/Disable**: Click to enable/disable worker

- **Remove Worker**: Click "Remove" to delete worker

**Status Indicators**:
- 🟢 **Enabled** - Ready for tasks
- ⚫ **Disabled** - Inactive
- 🔵 **Running** - Currently executing task

### Tab 3: Orchestration 🎭

**Purpose**: Monitor multi-agent orchestration in real-time

**Three Phases**:

1. **🔍 ANALYTIC** (Analysis Phase)
   - Analyze PRD.md
   - Determine task type (FEATURE, BUG, REFACTOR, RESET)
   - Identify coordination points
   - Develop scope allocation strategy
   - Generate Analysis Report

2. **📋 PLANNING** (Planning Phase)
   - Decompose into objectives
   - Assign to waves (Wave 1, Wave 2, ...)
   - Validate scope exclusivity (zero conflicts guaranteed!)
   - Define integration contracts
   - Generate Coordination Plan

3. **⚡ EXECUTION** (Execution Phase)
   - Workers execute tasks in parallel
   - Wave-based execution (all tasks in same wave run simultaneously)
   - Real-time progress updates
   - Generate Accomplishment Report

**UI Elements**:
- **Phase Progress Bars**: Animated 0% → 100%
- **Activity Log**: Timestamped events (last 50 entries)
- **Wave Info**: "Wave 1/3" during execution
- **Success Notification**: Alert when complete

## 🔥 Advanced Features

### Version Management
Each orchestration creates a new version:
```
projects/
└── my-blog-api/
    ├── v0.01/
    │   ├── .git/          # Separate Git repo
    │   ├── PRD.md
    │   ├── issues.json
    │   └── features.json
    ├── v0.02/
    │   └── ...
    └── v0.03/
        └── ...
```

**Benefits**:
- Independent Git history per version
- Can continue brainstorming from any version
- Easy rollback to previous versions
- Clear evolution tracking

### Real-Time WebSocket Streaming
Three WebSocket channels:
1. `/ws/brainstorm` - Chat messages + PRD.md updates
2. `/ws/workers` - Worker status, tool usage, progress
3. `/ws/orchestration` - Phase progress, wave execution, logs

**Latency**: <10ms per message

### Dark Forest Theme
- **Dark mode** (default): Forest green accents (#4ade80)
- **Light mode**: Toggle in header
- **Animations**: OpenAI-inspired typewriter, pulse, slideIn
- **Responsive**: Mobile-friendly

## 🐛 Troubleshooting

### Issue: "WebSocket connection failed"
**Solution**: Check backend is running:
```bash
python ap_studio_backend.py
```

### Issue: "LLM API error"
**Solution**: Verify OpenAI API key:
```bash
echo $OPENAI_API_KEY
# Should output: sk-proj-...
```

### Issue: "No workers available"
**Solution**: Add workers in Workers tab or seed database:
```bash
python seed_workers.py
```

### Issue: "Orchestration failed"
**Solution**: Check logs in Activity Log (Orchestration tab)
- Look for error messages
- Verify workers are enabled
- Check team.json configuration

## 📊 Project Structure

```
analytic_programming/
├── ap_studio.html              # Web UI (1500+ lines)
├── ap_studio_backend.py        # FastAPI backend (500+ lines)
├── ap_studio_db.py             # Database layer (300+ lines)
├── brainstorm_agent.py         # LLM agent (250+ lines)
├── version_manager.py          # Git + versions (150+ lines)
├── orchestration_launcher.py   # Orchestration bridge (350+ lines)
├── orchestrator_enhanced.py    # Main orchestrator (900+ lines)
├── orchestrator.py             # Data structures (900+ lines)
├── mcp_server_stdio.py         # MCP worker communication (650+ lines)
├── team.json                   # Worker configuration
├── ap_studio.db                # SQLite database
└── projects/                   # Version directories
    └── {project-name}/
        └── v{version}/
            └── .git/
```

## 🎓 Learning Resources

**For Users**:
- `START_AP_STUDIO.md` - This file (quick start)
- `AP_STUDIO_QUICKSTART.md` - Detailed setup guide
- `AP_STUDIO_COMPLETE.md` - Complete feature list

**For Developers**:
- `AP_STUDIO_ARCHITECTURE.md` - System architecture
- `ORCHESTRATION_INTEGRATION.md` - Orchestration details
- `WORKERS_UI_COMPLETE.md` - Worker management guide
- `ORCHESTRATION_TESTED.md` - Test results

**Protocol Docs**:
- `AP.md` - Full AP 2.0 protocol (660 lines)
- `AP_continue.md` - Quick-start variant (345 lines)
- `AGENTS.md` - Guide for AI agents
- `PRD.md` - Product requirements

## 🚀 What's Next?

### After First Launch
1. **Seed test workers**: `python seed_workers.py`
2. **Start brainstorming**: Enter project idea
3. **Launch orchestration**: Click "Spustiť Orchestráciu"
4. **Watch magic happen**: Real-time progress in Orchestration tab

### Configure Real Workers
Edit `team.json`:
```json
{
  "workers": [
    {
      "id": "claude-main",
      "agent_type": "claude",
      "mcp_config": {
        "command": "claude-mcp-server",
        "args": ["--stdio"],
        "env": {
          "ANTHROPIC_API_KEY": "sk-ant-..."
        }
      },
      "max_concurrent_tasks": 3,
      "enabled": true
    }
  ],
  "global_forbid": [
    "venv/**",
    "node_modules/**",
    ".git/**"
  ]
}
```

### Production Deployment
1. Security audit (API keys, CORS, XSS)
2. User authentication
3. Multi-project support
4. Performance tuning
5. Load testing

## 💡 Tips & Tricks

### Tip 1: Clear PRD.md Preview
If PRD.md preview doesn't update, refresh browser (F5)

### Tip 2: Resume Brainstorming
Database saves all brainstorming sessions. Just open and continue!

### Tip 3: Monitor Worker Activity
Keep Workers tab open in second browser window for real-time monitoring

### Tip 4: Orchestration Logs
Activity log is limited to 50 entries. Check full logs in:
- `docs/analyses/ANALYSIS_*.md`
- `docs/plans/PLAN_*.md`
- `docs/accomplishments/ACCOMPLISHMENT_*.md`

### Tip 5: Dark Mode Toggle
Click theme toggle (🌙) in header to switch dark/light modes

## 🎉 Success!

If you see this in your browser:

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║           🎭 AP STUDIO v1.0.0                   ║
║                                                  ║
║        Multi-Agent Orchestration IDE             ║
║                                                  ║
╚══════════════════════════════════════════════════╝

[Brainstorming] [Workers] [Orchestration]

💬 Start brainstorming your project...
```

**Congratulations! AP Studio is running!** 🎉

## 📞 Support

Questions? Check documentation:
- `README.md` - Project overview
- `AGENTS.md` - For AI agents working on this project
- `CURRENT_IMPLEMENTATION.md` - Implementation status

---

**🚀 Ready to build something amazing? Let's go!** 🚀

**Start command**:
```bash
export OPENAI_API_KEY=sk-proj-...
python ap_studio_backend.py
# Open http://localhost:8000
```

**Build date**: October 9, 2025  
**Version**: 1.0.0  
**Status**: PRODUCTION READY ✅
