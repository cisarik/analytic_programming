# AP Studio - Quick Start Guide

**Version:** 2.0.0  
**Date:** October 9, 2025  
**Status:** 🚀 Ready to Launch

---

## 🎯 What is AP Studio?

**AP Studio** is a web-based IDE for Analytic Programming with:
- **🌲 Dark Forest Theme** - Stunning UI with OpenAI-style animations
- **💬 Brainstorming-First Workflow** - AI helps create PRD.md
- **🎭 Multi-Agent Orchestration** - Parallel execution with Claude, GPT-4, Codex
- **📁 Version Management** - Each version = separate Git repo
- **⚡ Real-time Updates** - WebSocket streaming everywhere

---

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Navigate to project
cd /home/agile/analytic_programming

# Install requirements
pip install -r requirements.txt
```

**Required packages:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- OpenAI (LLM API)
- GitPython (version control)
- WebSockets (real-time communication)

### 2. Set Environment Variables

```bash
# OpenAI API Key (required for brainstorming)
export OPENAI_API_KEY="sk-your-key-here"

# Optional: Claude API Key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Initialize Database

```bash
# Test database initialization
python ap_studio_db.py

# Output:
# ✓ Database initialized
# ✓ Created project: 1
# ✓ Created version: 1
# ...
```

### 4. Start Backend

```bash
# Start FastAPI backend
python ap_studio_backend.py

# Output:
# ╔══════════════════════════════════════════════════════════════╗
# ║              🌲 AP Studio Backend 🌲                        ║
# ║  FastAPI + WebSocket + Brainstorm Agent                     ║
# ╚══════════════════════════════════════════════════════════════╝
# 
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Open AP Studio

```bash
# Option 1: Direct open
open ap_studio.html

# Option 2: Serve via HTTP
python -m http.server 8080
# Then open: http://localhost:8080/ap_studio.html
```

---

## 🎨 Using AP Studio

### Brainstorming Workflow

```
1. Open ap_studio.html
   ↓
2. System asks: "Názov projektu?"
   → Enter: "blog-api"
   ↓
3. AI: "Ahoj! Aký typ projektu chceš vytvoriť?"
   ↓
4. You: "REST API pre blog s postami"
   ↓
5. AI updates PRD.md in real-time →
   ↓
6. Continue conversation...
   ↓
7. When ready: Click "🚀 Spustiť Orchestráciu"
   ↓
8. System:
   - Creates projects/blog-api/v0.01/
   - Initializes Git repo
   - Saves PRD.md
   - Commits changes
   - Starts orchestration
```

### UI Features

**🌙 Dark/Light Theme Toggle**
- Click moon/sun icon in header
- Smooth theme switching
- Preference saved to localStorage

**💬 Chat Interface**
- Split pane: Chat left, PRD right
- Real-time PRD updates
- Markdown rendering
- OpenAI-style animations

**📝 PRD.md Preview**
- Live markdown rendering
- Syntax highlighting
- Manual edit option
- Auto-save on orchestration start

---

## 📁 Project Structure

### Created by AP Studio

```
projects/
  blog-api/              ← Project name
    v0.01/               ← Version (auto-incremented)
      .git/              ← Separate Git repo
      .gitignore
      PRD.md             ← Generated PRD
      issues.json        ← Issues list
      features.json      ← Features list
      docs/
        analyses/        ← Analysis reports
        plans/           ← Coordination plans
        accomplishments/ ← Accomplishment reports
    v0.02/               ← Next version (continued brainstorming)
      .git/              ← Another separate repo
      ...
```

### Version Management

**Each version = Independent Git repo**

```bash
# Navigate to version
cd projects/blog-api/v0.01

# View git history
git log

# Output:
# commit abc123...
# Author: AP Studio <apstudio@analytic-programming.local>
# Date:   Thu Oct 9 2025
# 
#     Initial commit: blog-api v0.01
```

---

## 🔌 API Endpoints

### REST API

**Projects:**
```
GET    /api/projects              # List all projects
POST   /api/projects              # Create new project
GET    /api/projects/{id}         # Get project details
```

**Versions:**
```
GET    /api/versions/{id}         # Get version
GET    /api/versions/{id}/prd     # Get PRD content
```

**Workers:**
```
GET    /api/workers               # List workers
POST   /api/workers               # Add worker
GET    /api/workers/{id}          # Get worker details
```

**Orchestrations:**
```
GET    /api/orchestrations/active # Active orchestrations
```

### WebSocket Endpoints

**Brainstorming:**
```
WS /ws/brainstorm

Messages:
- start: Start new session
- message: Send user message
- save_prd: Save PRD manually

Real-time responses:
- session_started
- response (with updated PRD)
- prd_saved
```

**Orchestration:**
```
WS /ws/orchestration

Messages:
- start: Start orchestration

Real-time updates:
- orchestration_started
- progress (phases, waves)
- orchestration_complete
```

**Workers:**
```
WS /ws/workers

Real-time updates:
- worker_list
- worker_activity
- worker_metrics
```

---

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ap_studio.html (Frontend)                                  │
│  - Dark Forest Theme with animations                        │
│  - 3 tabs: Brainstorming, Workers, Orchestration           │
│  - Real-time WebSocket updates                              │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket + REST
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  ap_studio_backend.py (FastAPI)                             │
│  - REST API endpoints                                       │
│  - WebSocket handlers                                       │
│  - Connection manager                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ brainstorm  │ │   version   │ │ ap_studio   │
│  _agent.py  │ │ _manager.py │ │   _db.py    │
│             │ │             │ │             │
│ - LLM API   │ │ - Git ops   │ │ - SQLite    │
│ - PRD gen   │ │ - Versions  │ │ - CRUD ops  │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🎨 UI Theming

### Dark Forest Theme (Default)

```css
--bg-primary: #0a0f0d      /* Deep forest */
--bg-elevated: #22322c     /* Elevated surface */
--accent-primary: #4ade80  /* Forest green */
--text-primary: #e8f2ed    /* Light text */
```

### Light Theme

```css
--bg-primary: #f8fdf9      /* Light background */
--bg-elevated: #ffffff     /* White surface */
--accent-primary: #22c55e  /* Bright green */
--text-primary: #0a0f0d    /* Dark text */
```

### Custom Animations

**Logo Glow:**
```css
@keyframes logoGlow {
    0%, 100% { filter: drop-shadow(0 0 8px var(--accent-glow)); }
    50% { filter: drop-shadow(0 0 16px var(--accent-glow)); }
}
```

**Tab Shimmer:**
```css
@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
```

**Message Slide-In:**
```css
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}
```

---

## 🧪 Testing

### Test Database

```bash
python ap_studio_db.py

# Creates test_ap_studio.db
# Tests: projects, versions, sessions, messages
```

### Test Brainstorm Agent

```bash
python brainstorm_agent.py

# Simulates conversation with AI
# Shows PRD generation
```

### Test Version Manager

```bash
python version_manager.py

# Creates test version
# Initializes Git repo
# Shows version info
```

### Test Backend

```bash
# Start backend
python ap_studio_backend.py

# In another terminal, test API
curl http://localhost:8000/

# Response:
# {"name": "AP Studio API", "version": "1.0.0", "status": "running"}
```

---

## 🐛 Troubleshooting

### WebSocket Connection Failed

**Symptom:** Status shows "Odpojené"

**Solution:**
```bash
# 1. Check if backend is running
ps aux | grep ap_studio_backend

# 2. Check port 8000 is available
netstat -an | grep 8000

# 3. Restart backend
python ap_studio_backend.py
```

### OpenAI API Error

**Symptom:** Brainstorm agent not responding

**Solution:**
```bash
# 1. Check API key is set
echo $OPENAI_API_KEY

# 2. Verify API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 3. Set key if missing
export OPENAI_API_KEY="sk-your-key-here"
```

### Git Operations Failed

**Symptom:** Version creation fails

**Solution:**
```bash
# 1. Check git is installed
git --version

# 2. Check git config
git config --global user.name
git config --global user.email

# 3. Set git config if missing
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## 📚 Next Steps

### Phase 1: Current (Working) ✅
- ✅ Database layer
- ✅ FastAPI backend
- ✅ Brainstorm Agent
- ✅ Version Manager
- ✅ Dark Forest UI

### Phase 2: Workers Management (Next)
- Worker cards with real-time status
- Add/Remove workers UI
- Auto-discovery integration
- Capability visualization

### Phase 3: Orchestration Monitor
- Live phase/wave progress
- Real-time activity feed
- Worker task assignment
- Integration with orchestrator_enhanced.py

### Phase 4: Advanced Features
- PRD templates
- Project history timeline
- Collaborative brainstorming
- Export/Import projects

---

## 🎓 Learn More

**Documentation:**
- `AP_STUDIO_ARCHITECTURE.md` - Complete system architecture
- `AP.md` - Analytic Programming Protocol
- `AGENTS.md` - Guide for AI agents

**Related Files:**
- `orchestrator_enhanced.py` - Orchestration engine
- `mcp_server_stdio.py` - Worker communication
- `team.json` - Worker configuration

---

## 💬 Support

**Issues:** Found a bug? Open an issue!

**Questions:** Need help? Check AGENTS.md

**Contributions:** PRs welcome! 🎉

---

**Status:** 🚀 **Production Ready**

**Next:** Start brainstorming your first project!

```bash
python ap_studio_backend.py
open ap_studio.html
```

**Welcome to AP Studio!** 🌲✨

