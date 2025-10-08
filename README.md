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
- **`orchestrator.py`**: Base orchestrator implementation (~900 lines) with data structures, documentation generation, and auto-documentation engine
- **`orchestrator_enhanced.py`**: Complete orchestrator (~800 lines) with full ANALYTIC/PLANNING phases, scope validation, and streaming
- **`team.json`**: Worker configuration for Claude, GPT-4, and Codex agents
- **`docs/`**: Auto-generated documentation structure (accomplishments, analyses, plans, sessions)

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

### Summary Documents (Read These First)
- **`MULTIAGENT_UPGRADE_COMPLETE.md`**: Comprehensive overview of AP 2.0 upgrade
- **`BEFORE_AFTER_COMPARISON.md`**: Visual comparison of AP 1.0 vs AP 2.0
- **`AP_MULTIAGENT_SUMMARY.md`**: Detailed changes to AP.md
- **`AP_CONTINUE_MULTIAGENT_SUMMARY.md`**: Detailed changes to AP_continue.md

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
1. **Read** `MULTIAGENT_UPGRADE_COMPLETE.md` for comprehensive overview
2. **Study** `AP.md` sections 0-2 for multi-agent orchestration basics
3. **Review** examples in `AP.md` section 3 and `AP_continue.md` section 7
4. **Understand** scope conflict prevention algorithm (AP.md section 2.2)
5. **Practice** with single-file changes (AP 1.0 mode) before multi-agent tasks

### For Using the Orchestrator (NEW!)
1. **Read** `IMPLEMENTATION_SUMMARY.md` for Phase 1 foundation overview
2. **Read** `PHASE2_COMPLETE.md` for complete implementation details
3. **Review** `SESSION_SUMMARY.md` for full development context
4. **Configure** worker agents in `team.json`
5. **Run** `python orchestrator_enhanced.py` to test the orchestrator

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

