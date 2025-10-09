# Analytic Programming (AP 1.0)

Analytic Programming (AP) is a collaboration protocol between the Owner, Orchestrator, and Workers (multiple AI agents) that enforces small deterministic increments, parallel execution, and transparent quality control. It clearly separates prompt design (Orchestrator) from implementation (Workers) while enabling conflict-free parallel task execution across multiple coding agents.

## What AP Provides
- **Multi-agent orchestration**: Parallel execution across Codex, Claude, GPT-4, and other agents
- **Wave-based execution**: Tasks grouped into waves with exclusive scope allocation
- **Zero conflicts**: Mathematical guarantee via scope conflict prevention algorithm
- **3-5× faster**: Parallel execution reduces time from 45+ minutes to ~15 minutes for large refactors
- **Agent specialization**: Right agent for the right task (Claude for architecture, Codex for tests)
- **Deterministic testing**: Framework for validating orchestration logic
- **Autonomous orchestrator**: Self-monitoring orchestrator with real-time streaming and auto-documentation (Phases 1 & 2 complete)

## Core Documents
- **`AP.md`**: The definitive Analytic Programming Protocol specification (version 1.0) including multi-agent orchestration, wave execution, scope management, and Boot Prompt
- **`AP_continue.md`**: Streamlined protocol for quick-start with codebase (multi-agent RESET plan)
- **`PRD.md`**: Product requirements; the single source of truth for functional scope
- **`AGENTS.md`**: Comprehensive guide for AI agents working on this project

## Implementation

### 🎨 AP Studio - Web-Based IDE (NEW! October 9, 2025)

**Complete web interface pre Analytic Programming s real-time streaming:**

**Core Files:**
- **`ap_studio.html`**: Stunning dark forest UI (~2400 lines) - brainstorming, workers, orchestration tabs with file management
- **`ap_studio_backend.py`**: FastAPI backend (~550 lines) - 3 WebSocket channels, REST API, project workspace
- **`ap_studio_db.py`**: SQLite database layer (~300 lines) - projects, versions, workers, orchestrations
- **`brainstorm_agent_mcp.py`**: MCP-enhanced brainstorming agent (~500 lines) - interactive PRD.md with tool calling
- **`project_workspace.py`**: Project workspace manager (~480 lines) - `~/.ap/projects/` structure
- **`version_manager.py`**: Git + version management (~150 lines) - separate repos per version
- **`orchestration_launcher.py`**: Orchestration bridge (~350 lines) - real-time progress streaming

**Quick Start:**
```bash
# Install dependencies (including mcp-use, langchain)
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY=sk-proj-YOUR-KEY

# Start backend
python ap_studio_backend.py

# Open UI
open ap_studio.html  # or http://localhost:8000
```

**Features:**

**Phase 0: Brainstorming** ✅
- MCP-enhanced agent with tool calling (mcp-use library)
- Real-time PRD.md editing with **green highlighting**
- **Undo capability** - hover over changes → "↶ Undo" button
- Project workspace (`~/.ap/projects/<name>/`)
- Auto-loaded context files (AGENTS.md, README.md, PRD.md with ✅)

**Interactive MD Files** ✅ NEW!
- **Click-to-chat** - klikni na TODO/BUG/Feature → pošle sa do chatu
- **File tabs** - multi-file view (PRD.md, TODOs.md, BUGs.md, FEATURES.md)
- **Dropdown selector** - ✅ checkmarks pre loaded context files
- **Zero typing** - všetko klikateľné, nič netreba vypisovať

**Worker Management** ✅
- Add, discover, monitor MCP workers via UI
- Real-time status updates
- Capability visualization

**Orchestration Monitor** ✅
- Real-time progress: ANALYTIC → PLANNING → EXECUTION
- Wave-based execution tracking
- Activity log with timestamps

**UI Enhancements** ✅
- **Compact design** - 3px padding reduction everywhere
- **Green borders** - toolbar & PRD preview
- **Brighter animations** - background pulse (0.08 → 0.15 opacity)
- **Dark Forest Theme** - OpenAI-inspired design

**Documentation:**
- `MCP_BRAINSTORM_README.md` - MCP agent guide (NEW!)
- `PROJECT_WORKSPACE_README.md` - Workspace system guide (NEW!)
- `sessions/2025-09-10/INTERACTIVE_PRD_BRAINSTORMING.md` - Session docs (NEW!)
- `START_AP_STUDIO.md` - Quick start guide (<2 minutes)
- `AP_STUDIO_ARCHITECTURE.md` - System architecture
- `ORCHESTRATION_INTEGRATION.md` - Technical details

### Core Components
- **`orchestrator.py`**: Base orchestrator (~900 lines) - data structures, documentation generation, auto-documentation engine
- **`orchestrator_enhanced.py`**: Complete orchestrator (~900 lines) - full ANALYTIC/PLANNING/EXECUTION phases with streaming
- **`mcp_server_stdio.py`**: MCP worker manager (~650 lines) - direct stdio communication using OpenAI Codex SDK pattern
- **`mcp_capability_discovery.py`**: Automatic capability discovery system (~400 lines) - LLM-powered worker analysis
- **`discover_worker.py`**: CLI tool for discovering worker capabilities with interactive UI
- **`dashboard.html`**: Real-time dashboard UI for monitoring worker activity and metrics (legacy - see AP Studio)
- **`team.json`**: Worker configuration (Claude, GPT-4, Codex) with MCP connection details
- **`docs/`**: Auto-generated documentation (accomplishments, analyses, plans, sessions)

### MCPServerStdio - Direct Worker Communication (Phase 3) 🚀

**Architecture:**
```
Orchestrator → MCPServerStdio → Worker (stdin/stdout)
                     ↕
              JSON MCP Messages
                     ↓
           WebSocket → Dashboard
```

**Key Features:**
- ✅ **Direct stdio communication** - no file system dependency
- ✅ **MCP Protocol** - standard JSON messages (based on OpenAI Codex SDK)
- ✅ **Bidirectional** - full request/response capability
- ✅ **Real-time** - event-driven (<1ms latency vs 100ms polling)
- ✅ **Error handling** - task errors, acknowledgments, progress tracking
- ✅ **WebSocket streaming** - live updates to dashboard (`ws://localhost:8765`)

**Quick Start:**
```bash
# Install dependencies
pip install aiofiles websockets

# Run orchestrator (demo mode)
python orchestrator_enhanced.py

# Open dashboard
open dashboard.html
```

**To enable real workers:** Create MCP-compliant worker scripts with standard MCP protocol (JSON messages via stdin/stdout)

### MCP Capability Discovery - Automatic Worker Analysis 🔍

**New Feature (October 2025)**: Automaticky objavuje schopnosti (capabilities) MCP serverov pomocou LLM analýzy.

**Workflow:**
```
1. Spusti MCP worker → 2. Získa zoznam tools (LIST_TOOLS)
3. Analyzuje cez LLM API → 4. Vygeneruje capability tags
5. Updatne team.json (s backup)
```

**Quick Start:**
```bash
# Objavenie capabilities pre jedného workera
python discover_worker.py --worker-id claude-main

# Auto-approve (bez potvrdenia)
python discover_worker.py --worker-id gpt4-main --auto-approve

# Re-discover pre všetkých workerov
python discover_worker.py --rediscover-all

# Zoznam workerov
python discover_worker.py --list-workers
```

**Key Features:**
- ✅ **LLM-powered analysis** - OpenAI/Claude analyzuje dostupné tools
- ✅ **Automatic tagging** - Generuje 3-7 capability tags (refactoring, python, debugging, etc.)
- ✅ **Interactive UI** - Potvrdenie pred zmenou team.json
- ✅ **Backup system** - Automatický backup pred každou zmenou
- ✅ **Confidence scoring** - LLM poskytuje confidence score (0.0-1.0)
- ✅ **Orchestrator integration** - Seamless integration s orchestrator_enhanced.py

**Dokumentácia:** Pozri `MCP_CAPABILITY_DISCOVERY.md` pre kompletný guide s príkladmi.

## Required Artifacts
When working with the Orchestrator, **always attach**:
1. **`AP.md`**: Protocol specification with multi-agent orchestration rules
2. **`PRD.md`**: Product requirements (if applicable)
3. **`AGENTS.md`**: Agent-specific guidelines and project context

> The Orchestrator needs all three to craft valid multi-agent task plans with exclusive scopes and proper wave assignments.

## Roles and Workflow (Multi-Agent)
- **Owner** sets goals, prioritizes, and approves multi-agent task plans with scope allocations
- **Orchestrator** decomposes objectives into parallel tasks, builds dependency graphs, allocates exclusive scopes, assigns agent types, coordinates wave execution, integrates results
- **Workers (Multiple Agents)** - Codex, Claude, GPT-4, etc. - each works on exclusive scope in parallel, no coordination needed, reports in strict response format

### Multi-Agent Execution Flow
1. **Owner** states objective → Orchestrator analyzes codebase
2. **Orchestrator** decomposes → Creates task graph with exclusive scopes organized in waves
3. **Owner** reviews plan → Approves task allocation and wave structure
4. **Wave execution** → All Wave N tasks sent to respective agents IN PARALLEL
5. **Integration** → Orchestrator merges diffs, runs quality gates
6. **Next wave** → Proceed to Wave N+1 if all tasks pass; otherwise rollback and adjust

## Sample Prompt for the Orchestrator (Multi-Agent)
Use this prompt when you need the Orchestrator to decompose a request into multi-agent tasks:

```
You are the Orchestrator for project <ProjectName> operating under Analytic Programming protocol AP 1.0.

ATTACHED DOCUMENTS:
- AP.md: Multi-agent protocol specification with wave execution and scope management
- PRD.md: Product requirements to be broken down
- AGENTS.md: Agent capabilities and project context
- Codebase: (ZIP or file listing)

TASKS:
1. Analyze the codebase structure and identify independent areas
2. Decompose the request into atomic tasks with exclusive scopes
3. Build dependency graph and assign tasks to waves
4. Match tasks to appropriate agent types (codex/claude/gpt4)
5. Ensure SCOPE_TOUCH sets are disjoint within each wave
6. Define INTEGRATION_POINTS for dependent tasks

RETURN:
For each wave, provide complete task prompts with:
- TASK_ID, WAVE, DEPENDS_ON
- AGENT_TYPE, COMPLEXITY
- SCOPE_TOUCH, SCOPE_READ, SCOPE_FORBID (exclusive within wave)
- INTEGRATION_POINTS
- All other fields per AP.md Section 3

VALIDATION:
Confirm that ∀ tasks Ti, Tj in same wave: Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅
```

This ensures:
- Multi-agent task decomposition with exclusive scopes
- Wave-based execution with proper dependencies
- Agent type matching based on task characteristics
- Zero scope conflicts (mathematically guaranteed)

## Using AP_continue (Multi-Agent RESET)
`AP_continue.md` enables quick-start with existing codebases using multi-agent parallel RESET. The Orchestrator decomposes baseline refactoring into 3-5 parallel tasks with exclusive scopes.

### Multi-Agent RESET Example
1. **Owner** attaches ZIP + `AP_continue.md` to new chat
2. **Orchestrator** analyzes codebase and produces **RESET plan** with parallel tasks:
   - RESET_T1: Core typing (Claude, `src/core/**`)
   - RESET_T2: Test hardening (Codex, `tests/**`)
   - RESET_T3: Logging security (Codex, `logger.py, config/**`)
   - All with exclusive SCOPE_TOUCH (no overlaps)
3. **Owner** reviews plan, forwards all Wave 1 tasks to respective agents IN PARALLEL
4. **Agents** work simultaneously (~15 minutes vs 45+ sequential)
5. **Orchestrator** merges diffs, runs quality gates, validates
6. **Subsequent work** continues with regular multi-agent tasks

**Benefits**: 3× faster baseline refactoring, zero conflicts, behavior preservation guaranteed

## Key Features

### Wave-Based Execution
Tasks grouped into waves where:
- **Wave N**: All tasks execute in parallel (exclusive scopes)
- **Wave N+1**: Starts only after Wave N completes and validates
- **Dependencies**: Explicitly tracked via `DEPENDS_ON` field

### Scope Conflict Prevention Algorithm
```
For each task T in wave W:
  T.SCOPE_FORBID = GLOBAL_FORBID ∪ (⋃ other tasks' SCOPE_TOUCH in wave W)

Validation: ∀ Ti, Tj in same wave: Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅
```
**Result**: Zero edit conflicts (mathematical guarantee)

### Agent Type Matching
- **Codex**: Fast, good for refactoring, type hints, unit tests
- **Claude**: Best for architecture, complex logic, multi-file changes
- **GPT-4**: Excellent for algorithms, performance, debugging

### Deterministic Testing
Framework for validating orchestration logic (AP.md Section 9):
- YAML test cases with expected task decompositions
- 6 automated validation rules
- Test categories: MA-BASIC, MA-SEQUENTIAL, MA-COMPLEX, MA-CONFLICT

## Documentation Files

### Protocol Specifications
- **`AP.md`**: Full AP 2.0 protocol (660 lines)
- **`AP_continue.md`**: Quick-start variant (345 lines)

## Version
- **AP 1.0**: First true "Analytic Programming" implementation
  - Multi-agent parallel execution with wave-based orchestration
  - 3-5× faster for independent tasks
  - Zero scope conflicts (guaranteed)
  - Agent specialization
  - Autonomous orchestrator with self-monitoring

## Getting Started

### For Understanding the Protocol
1. **Read** `README.md` (this file) for project overview
2. **Study** `AP.md` sections 0-2 for multi-agent orchestration basics
3. **Review** examples in `AP.md` section 3 and `AP_continue.md` section 7
4. **Understand** scope conflict prevention algorithm (AP.md section 2.2)
5. **Review** `PRD.md` for requirements and acceptance criteria

### For Using the Orchestrator
1. **Read** `CURRENT_IMPLEMENTATION.md` for complete implementation status
2. **Configure** worker agents in `team.json`
3. **Run** `python orchestrator_enhanced.py` to test the orchestrator
4. **Open** `dashboard.html` to monitor workers in real-time

### Quick Test
```bash
# Test the orchestrator with streaming output
python orchestrator_enhanced.py

# Output: Complete ANALYTIC and PLANNING phases with:
# - Analysis Report saved to docs/analyses/
# - Coordination Plan saved to docs/plans/
# - Accomplishment Report saved to docs/accomplishments/
# - Auto-generated commit message
```

## Contributing

When proposing changes to the AP protocol:
1. Update deterministic test cases (AP.md section 9)
2. Update all documentation files consistently
3. Validate scope conflict prevention guarantees
4. Measure performance impact
5. Maintain the "Analytic" philosophy: deep analysis before coordination

