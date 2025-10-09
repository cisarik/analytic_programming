# AP Studio - Architecture Design

**Vision:** Web-based IDE pre Analytic Programming s Brainstorming-first workflow  
**Date:** October 9, 2025  
**Version:** 2.0.0 (Brainstorming Phase)

---

## 🎯 Core Concept

```
Phase 0: BRAINSTORMING    → PRD.md creation with Brainstorm Helper Agent
Phase 1: ANALYTIC         → Codebase analysis
Phase 2: PLANNING         → Task decomposition + wave allocation
Phase 3: EXECUTION        → Multi-agent parallel execution
```

**Key Innovation:** User brainstormuje s AI agentom, real-time vidí PRD.md, kedykoľvek môže spustiť orchestráciu.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AP Studio Web UI                         │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Brainstorm  │  │   Workers    │  │ Orchestration│      │
│  │    View     │  │  Management  │  │    Monitor   │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  • Chat-based brainstorming with AI                        │
│  • Real-time PRD.md preview (split pane)                   │
│  • Worker cards with status & metrics                      │
│  • Live orchestration progress                             │
│  • Version selector (dropdown)                             │
│  • "Spustiť Orchestráciu" button                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket (real-time)
                        │ REST API (actions)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (ap_studio_backend.py)         │
│                                                             │
│  Routes:                                                    │
│  • /api/brainstorm/start                                   │
│  • /api/brainstorm/message                                 │
│  • /api/brainstorm/save-prd                                │
│  • /api/workers/list                                       │
│  • /api/workers/add                                        │
│  • /api/workers/discover                                   │
│  • /api/orchestration/start                                │
│  • /api/orchestration/status                               │
│  • /api/versions/list                                      │
│  • /api/versions/create                                    │
│  • /ws/brainstorm (WebSocket)                              │
│  • /ws/orchestration (WebSocket)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   Core Components                           │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  BrainstormHelperAgent                        │          │
│  │  - Reads AP.md (understands orchestration)    │          │
│  │  - Conversational PRD builder                 │          │
│  │  - Asks smart questions                       │          │
│  │  - Streams PRD.md updates                     │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  VersionManager                               │          │
│  │  - Creates versioned directories (v0.01/)     │          │
│  │  - Initializes Git repo per version           │          │
│  │  - Stores PRD.md, issues, features            │          │
│  │  - Manages version metadata                   │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  EnhancedOrchestrator (existing)              │          │
│  │  - ANALYTIC phase                             │          │
│  │  - PLANNING phase                             │          │
│  │  - EXECUTION phase                            │          │
│  │  - Real-time WebSocket updates                │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │  WorkerManager (existing)                     │          │
│  │  - MCPServerStdio pool                        │          │
│  │  - Worker discovery                           │          │
│  │  - Status monitoring                          │          │
│  └──────────────────────────────────────────────┘          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Database                           │
│                                                             │
│  Tables:                                                    │
│  • projects (id, name, created_at)                         │
│  • versions (id, project_id, version, path, git_repo)      │
│  • brainstorm_sessions (id, version_id, started_at)        │
│  • brainstorm_messages (id, session_id, role, content)     │
│  • workers (id, worker_id, type, capabilities, status)     │
│  • orchestrations (id, version_id, status, started_at)     │
│  • issues (id, version_id, type, title, description)       │
│  • features (id, version_id, title, description, status)   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              File System (Version Storage)                  │
│                                                             │
│  projects/                                                  │
│    my-project/                                             │
│      v0.01/                                                │
│        .git/                    ← Git repo                 │
│        PRD.md                   ← Generated PRD            │
│        issues.json              ← Issues list              │
│        features.json            ← Features list            │
│        orchestration.log        ← Execution log            │
│      v0.02/                                                │
│        .git/                                               │
│        PRD.md                   ← Updated PRD              │
│        ...                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Web UI Design

### Main Layout

```
╔═══════════════════════════════════════════════════════════════╗
║  AP Studio                [v0.01 ▼]  [Workers: 3 ✓] [User ⚙]║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          ║
║  │ Brainstorm  │  │   Workers   │  │Orchestration│          ║
║  └─────────────┘  └─────────────┘  └─────────────┘          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Tab 1: Brainstorming View

```
╔═══════════════════════════════════════════════════════════════╗
║  💬 Brainstorming Session                         [New ⊕]    ║
╠═══════════════╦═══════════════════════════════════════════════╣
║               ║                                               ║
║  Chat Panel   ║            PRD.md Preview                     ║
║               ║                                               ║
║ ┌───────────┐ ║  # Product Requirements Document              ║
║ │ AI: Ahoj! │ ║                                               ║
║ │ Som Brainstorm │  **Project:** My Project                  ║
║ │ Helper. Aký │ ║  **Version:** 0.01                          ║
║ │ projekt   │ ║  **Created:** Oct 9, 2025                     ║
║ │ chceš?    │ ║                                               ║
║ └───────────┘ ║  ## Overview                                  ║
║               ║  [Real-time updates as you chat...]           ║
║ ┌───────────┐ ║                                               ║
║ │User: Chcem│ ║  ## Requirements                              ║
║ │ REST API  │ ║  - R1: User authentication                    ║
║ └───────────┘ ║  - R2: CRUD operations                        ║
║               ║                                               ║
║ ┌───────────┐ ║  ## Architecture                              ║
║ │ AI: Super!│ ║  - Backend: FastAPI                           ║
║ │ Aké       │ ║  - Database: PostgreSQL                       ║
║ │ features? │ ║  - Frontend: React                            ║
║ └───────────┘ ║                                               ║
║               ║                                               ║
║ [Type message...]║                                            ║
║               ║  [📝 Edit PRD Manually]                       ║
║ [Send 📤]    ║                                               ║
║               ║                                               ║
╠═══════════════╩═══════════════════════════════════════════════╣
║  [🚀 Spustiť Orchestráciu]  [💾 Save PRD]  [🔄 Continue]    ║
╚═══════════════════════════════════════════════════════════════╝
```

**Key Features:**
- **Split pane:** Chat vľavo, PRD.md preview vpravo
- **Real-time updates:** PRD.md sa aktualizuje počas konverzácie
- **Manual edit:** User môže PRD editovať priamo
- **Version dropdown:** Výber existujúcej verzie
- **"Continue":** Pokračovanie v brainstormingu s vybranou verziou
- **"Spustiť Orchestráciu":** Kedykoľvek počas brainstormingu

### Tab 2: Workers Management

```
╔═══════════════════════════════════════════════════════════════╗
║  👷 Workers                                    [+ Add Worker] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌────────────────────┐  ┌────────────────────┐              ║
║  │ claude-main     ✓  │  │ gpt4-main      ✓   │              ║
║  │ Type: Claude       │  │ Type: GPT-4        │              ║
║  │ Status: Ready      │  │ Status: Ready      │              ║
║  │ Tasks: 12 done     │  │ Tasks: 8 done      │              ║
║  │ Uptime: 2h 15m     │  │ Uptime: 1h 45m     │              ║
║  │                    │  │                    │              ║
║  │ Capabilities:      │  │ Capabilities:      │              ║
║  │ • complex_logic    │  │ • algorithms       │              ║
║  │ • architecture     │  │ • debugging        │              ║
║  │ • refactoring      │  │ • testing          │              ║
║  │                    │  │                    │              ║
║  │ [🔍 Discover]      │  │ [🔍 Discover]      │              ║
║  │ [⚙️ Configure]     │  │ [⚙️ Configure]     │              ║
║  │ [🗑️ Remove]        │  │ [🗑️ Remove]        │              ║
║  └────────────────────┘  └────────────────────┘              ║
║                                                               ║
║  ┌────────────────────┐  ┌────────────────────┐              ║
║  │ codex-fast     ✓   │  │ deepseek       ✗   │              ║
║  │ Type: Codex        │  │ Type: DeepSeek     │              ║
║  │ Status: Busy       │  │ Status: Offline    │              ║
║  │ Tasks: 45 done     │  │ Tasks: 0 done      │              ║
║  │ Current: T-042     │  │ Last seen: Never   │              ║
║  │ [⏸️ Pause]         │  │ [▶️ Start]         │              ║
║  └────────────────────┘  └────────────────────┘              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Features:**
- **Worker cards:** Visual status, metrics, capabilities
- **Add Worker:** Modal form pre pridanie nového workera
- **Discover:** Auto-discovery capabilities (integration s discover_worker.py)
- **Real-time status:** WebSocket updates

### Tab 3: Orchestration Monitor

```
╔═══════════════════════════════════════════════════════════════╗
║  🎭 Orchestration                          [History ▼]        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Current: v0.01 - "REST API Implementation"                   ║
║  Status: Wave 2 / 3                                           ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │ Phase 1: ANALYTIC ✅ (2m 15s)                       │     ║
║  │ Phase 2: PLANNING ✅ (1m 45s)                       │     ║
║  │ Phase 3: EXECUTION 🔄 (5m 30s)                      │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  Wave 1: ████████████████████ 100% ✅                        ║
║    ✅ T1: Core models (claude-main) - 3m 45s                 ║
║    ✅ T2: API routes (gpt4-main) - 4m 12s                    ║
║    ✅ T3: Tests (codex-fast) - 2m 30s                        ║
║                                                               ║
║  Wave 2: ███████████░░░░░░░░░ 60% 🔄                        ║
║    ✅ T4: Database migrations (claude-main) - 2m 15s         ║
║    🔄 T5: Authentication (gpt4-main) - 3m 20s / ~5m          ║
║    ⏸️  T6: Frontend components (pending)                     ║
║                                                               ║
║  Wave 3: ░░░░░░░░░░░░░░░░░░░░ 0% ⏸️                         ║
║    ⏸️  T7: Integration tests                                 ║
║    ⏸️  T8: Documentation                                     ║
║                                                               ║
║  ┌─────────────────────────────────────────────────────┐     ║
║  │ 📊 Activity Feed                                    │     ║
║  │ 14:32:45 gpt4-main: Using tool: search_files       │     ║
║  │ 14:32:43 gpt4-main: Analyzing auth patterns...     │     ║
║  │ 14:32:40 claude-main: ✅ T4 complete                │     ║
║  │ 14:32:12 claude-main: Writing migration...         │     ║
║  └─────────────────────────────────────────────────────┘     ║
║                                                               ║
║  [⏸️ Pause] [⏹️ Stop] [📄 View Logs] [💾 Save Report]       ║
╚═══════════════════════════════════════════════════════════════╝
```

**Features:**
- **Phase progress:** Visual progress bars
- **Wave breakdown:** Detailed task status
- **Activity feed:** Real-time worker activity (ako teraz dashboard.html)
- **Controls:** Pause, stop, view logs

---

## 📊 Database Schema

```sql
-- Projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Versions (každý brainstorming session = nová verzia)
CREATE TABLE versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    version TEXT NOT NULL,  -- "0.01", "0.02", etc.
    path TEXT NOT NULL,     -- "projects/my-project/v0.01/"
    git_repo_path TEXT,     -- Path to git repo
    prd_content TEXT,       -- PRD.md content
    status TEXT DEFAULT 'draft',  -- draft, orchestrating, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Brainstorming sessions
CREATE TABLE brainstorm_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',  -- active, completed, continued
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES versions(id)
);

-- Brainstorm messages (chat history)
CREATE TABLE brainstorm_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES brainstorm_sessions(id)
);

-- Workers
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id TEXT UNIQUE NOT NULL,  -- "claude-main"
    agent_type TEXT NOT NULL,        -- "claude", "gpt4", "codex"
    capabilities TEXT,               -- JSON array
    mcp_config TEXT,                 -- JSON config
    max_concurrent INTEGER DEFAULT 1,
    enabled BOOLEAN DEFAULT 1,
    status TEXT DEFAULT 'offline',   -- offline, ready, busy, error
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orchestrations
CREATE TABLE orchestrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    status TEXT DEFAULT 'running',   -- running, completed, failed, paused
    phase TEXT,                      -- analytic, planning, execution
    current_wave INTEGER,
    total_waves INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    analysis_report TEXT,            -- JSON
    coordination_plan TEXT,          -- JSON
    accomplishment_report TEXT,      -- JSON
    FOREIGN KEY (version_id) REFERENCES versions(id)
);

-- Issues (bugs, tech debt)
CREATE TABLE issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    type TEXT NOT NULL,              -- bug, tech_debt, improvement
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',      -- open, in_progress, resolved
    priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES versions(id)
);

-- Features
CREATE TABLE features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'planned',   -- planned, in_progress, completed
    priority TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES versions(id)
);

-- Worker tasks (execution tracking)
CREATE TABLE worker_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orchestration_id INTEGER NOT NULL,
    worker_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    wave INTEGER NOT NULL,
    title TEXT,
    status TEXT DEFAULT 'pending',   -- pending, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    files_modified TEXT,             -- JSON array
    error_message TEXT,
    FOREIGN KEY (orchestration_id) REFERENCES orchestrations(id)
);
```

---

## 🤖 Brainstorm Helper Agent

### Design

```python
class BrainstormHelperAgent:
    """
    Interaktívny agent pre PRD.md creation
    
    Features:
    - Reads AP.md (understands orchestration)
    - Conversational interface
    - Smart questions based on project type
    - Real-time PRD.md generation
    - Streaming updates via WebSocket
    """
    
    def __init__(self, llm_provider="openai", model="gpt-4"):
        self.llm = llm_provider
        self.model = model
        self.ap_protocol = self._load_ap_protocol()
        self.conversation_history = []
    
    async def start_session(self, project_name: str) -> str:
        """
        Začatie brainstorming session
        Returns: Initial greeting message
        """
        prompt = f"""
        Si Brainstorm Helper Agent pre Analytic Programming.
        
        Tvoja úloha:
        1. Pomôcť userovi vytvoriť PRD.md (Product Requirements Document)
        2. Pýtať sa smart questions o projekte
        3. Postupne budovať PRD.md
        4. Pripraviť projekt na orchestráciu
        
        Kontext:
        - User práve začal nový projekt: {project_name}
        - Rozumieš AP protocol (multi-agent orchestration)
        - Vieš, že PRD.md bude použitý orchestrátorom
        
        Privítaj usera a spýtaj sa na typ projektu.
        """
        
        response = await self._call_llm(prompt)
        return response
    
    async def process_message(
        self, 
        user_message: str,
        current_prd: str
    ) -> Tuple[str, str]:
        """
        Spracuje user message a vráti:
        - Assistant response
        - Updated PRD.md
        """
        prompt = f"""
        User message: {user_message}
        
        Current PRD.md:
        {current_prd}
        
        Úloha:
        1. Odpovedz userovi (conversational, friendly)
        2. Updatni PRD.md na základe nových informácií
        3. Opýtaj sa follow-up otázku (ak potrebné)
        
        Vráť JSON:
        {{
            "response": "Tvoja odpoveď userovi",
            "updated_prd": "Updatnutý PRD.md (markdown)",
            "next_question": "Optional follow-up question",
            "completion_percentage": 0-100
        }}
        """
        
        result = await self._call_llm(prompt)
        parsed = json.loads(result)
        
        return parsed["response"], parsed["updated_prd"]
```

### Conversation Flow

```
Agent: Ahoj! Som Brainstorm Helper. Aký projekt chceš vytvoriť?
User:  Chcem REST API pre blog

Agent: Super! Blog API. Aké hlavné features potrebuješ?
       (automaticky začína PRD: "# Blog REST API\n## Features\n")
User:  Posts, comments, users, authentication

Agent: Výborne! A aké technológie chceš použiť?
       (pridáva features do PRD)
User:  Python FastAPI, PostgreSQL

Agent: Perfektné! Máš už nejaké špecifické requirements na architektúru?
       (updatuje PRD s tech stackom)
User:  Microservices, Docker

Agent: Excelentné! PRD.md je ready. Môžeš:
       1. Pokračovať v brainstormingu (detailnejšie features)
       2. Spustiť orchestráciu
       3. Manuálne editovať PRD
       
       Čo chceš urobiť?
```

---

## 📁 Version Management

### Directory Structure

```
ap_studio/
  projects/
    blog-api/
      v0.01/
        .git/                    ← Git repo initialized
        .gitignore
        PRD.md                   ← Brainstormed PRD
        issues.json              ← Issues list
        features.json            ← Features list
        orchestration_001.log    ← Orchestration log
        docs/
          analyses/
            ANALYSIS_001.md
          plans/
            PLAN_001.md
          accomplishments/
            ACCOMPLISHMENT_001.md
      v0.02/
        .git/                    ← Separate git repo
        PRD.md                   ← Continued/updated PRD
        ...
      v0.03/
        ...
```

### Version Manager

```python
class VersionManager:
    """
    Manages versioned directories and git repos
    """
    
    async def create_version(
        self,
        project_name: str,
        version: str,
        prd_content: str
    ) -> Path:
        """
        Creates new version directory:
        1. Create projects/{project_name}/v{version}/
        2. Initialize git repo
        3. Save PRD.md
        4. Commit initial PRD
        5. Update database
        """
        version_dir = Path(f"projects/{project_name}/v{version}")
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Init git
        git.Repo.init(version_dir)
        
        # Save PRD
        prd_path = version_dir / "PRD.md"
        prd_path.write_text(prd_content)
        
        # Commit
        repo = git.Repo(version_dir)
        repo.index.add(["PRD.md"])
        repo.index.commit("Initial PRD from brainstorming")
        
        # Update DB
        await self.db.create_version(
            project_name=project_name,
            version=version,
            path=str(version_dir),
            prd_content=prd_content
        )
        
        return version_dir
    
    async def continue_version(
        self,
        project_name: str,
        from_version: str,
        new_version: str
    ) -> Path:
        """
        Continue from existing version (AP_continue.md workflow)
        """
        # Copy existing version
        # Create new git branch
        # Allow continued brainstorming
        pass
```

---

## 🔄 Workflow Integration

### Complete User Flow

```
1. User opens AP Studio
   ↓
2. Clicks "New Project" or selects existing
   ↓
3. BRAINSTORMING TAB opens
   ↓
4. Chat with Brainstorm Helper Agent
   ↓
5. PRD.md builds in real-time (right pane)
   ↓
6. User can:
   a) Continue brainstorming (more details)
   b) Edit PRD manually
   c) Click "Spustiť Orchestráciu"
   ↓
7. IF "Spustiť Orchestráciu":
   a) Version created (v0.01)
   b) Git repo initialized
   c) PRD.md saved & committed
   d) Orchestrator starts (ANALYTIC → PLANNING → EXECUTION)
   e) ORCHESTRATION TAB shows progress
   ↓
8. User monitors orchestration in real-time
   ↓
9. When complete:
   a) View accomplishment report
   b) Option: "Continue Brainstorming" (new version v0.02)
   c) Option: "New Project"
```

### AP_continue.md Integration

```
User wants to continue existing version:

1. Dropdown: Select "v0.01"
2. Click "Continue Brainstorming"
   ↓
3. System:
   a) Loads existing PRD.md
   b) Loads existing git repo
   c) Creates new brainstorm session (linked to v0.01)
   ↓
4. User chats with agent:
   "Chcem pridať notifikácie"
   ↓
5. Agent updates PRD.md (in v0.01)
   ↓
6. User clicks "Spustiť Orchestráciu"
   ↓
7. System:
   a) Git commit updated PRD
   b) Orchestrator uses AP_continue.md workflow
   c) Continues in same version (incremental changes)
```

---

## 🚀 Implementation Plan

### Phase 1: Backend Foundation
1. FastAPI backend setup
2. SQLite database + schema
3. WebSocket infrastructure
4. Version Manager

### Phase 2: Brainstorm Agent
1. BrainstormHelperAgent implementation
2. PRD.md generation logic
3. WebSocket streaming

### Phase 3: Web UI (MVP)
1. Brainstorming view (chat + PRD preview)
2. Basic worker management
3. Simple orchestration monitor

### Phase 4: Full Integration
1. Orchestrator integration
2. Real-time updates
3. Worker discovery UI
4. Version dropdown + continue

### Phase 5: Polish
1. Eye candy UI improvements
2. Advanced features
3. Performance optimization

---

## 🎯 Next Steps

1. **Vytvor FastAPI backend skeleton**
2. **Implementuj database schema**
3. **Build Brainstorm Helper Agent**
4. **Create modern web UI**
5. **Integrate s existing orchestrator**

**Target:** Functional MVP s brainstorming + basic orchestration v 1-2 dni.

---

**Status:** Architecture Design Complete ✅  
**Next:** Start implementation

