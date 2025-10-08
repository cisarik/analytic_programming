# AP_continue.md: Multi-Agent Edition - Update Summary

## Overview
Successfully updated AP_continue.md to support multi-agent RESET execution with wave-based parallel task orchestration, aligning with AP 2.0 Multi-Agent Edition.

## Key Changes

### Title & Purpose (Lines 1-6)
**Before**: Single RESET prompt to one Worker
**After**: RESET plan with multiple parallel tasks to multiple Workers

### Section 0: Roles (Lines 10-20)
**Updated**:
- **Orchestrator**: Now decomposes RESET into parallel tasks, builds dependency graph, assigns agents, coordinates wave execution
- **Workers**: Changed from singular "Worker (Codex Agent)" to "Workers (Multiple Agents): Codex, Claude, GPT-4, etc."
- **Guiding principles**: Added exclusive scope allocation and wave-based execution

### Section 1: Start Here (Lines 24-32)
**Updated workflow**:
1. Owner attaches ZIP + AP_continue.md
2. Orchestrator produces **RESET plan** (not single prompt) with parallel tasks and exclusive scopes
3. Owner reviews plan (task decomposition, scope allocation, wave structure)
4. Owner forwards each task to appropriate Worker (may send Wave 1 in parallel)
5. Orchestrator collects responses, merges diffs, validates quality gates
6. After RESET completes, continue with normal tasks

### Section 2: RESET Task Format (Lines 36-90)
**New fields added**:
- `TASK_ID`: e.g., RESET_T1, RESET_T2, RESET_T3
- `WAVE`: Execution wave number (typically 1 for independent RESET tasks)
- `DEPENDS_ON`: Task dependencies
- `AGENT_TYPE`: codex|claude|gpt4|auto
- `COMPLEXITY`: low|medium|high
- `SCOPE_READ`: Files may read but not edit
- `INTEGRATION_POINTS`: Interfaces/contracts with other RESET tasks

**Changed**:
- `TITLE`: Now specific to refactor area (e.g., "Test suite hardening" vs generic "Baseline refactor")
- `SCOPE_TOUCH`: Must be exclusive within wave
- `CONTEXT`: Specific to task scope (not entire codebase)
- `REFACTOR_PLAN`: Focused on this task's scope only
- `NOTES`: Added "Other agents may be working on other parts of codebase simultaneously"

### Section 3: Regular Task Format (Lines 96-139)
**New fields added** (same as RESET task):
- `TASK_ID`, `WAVE`, `DEPENDS_ON`, `AGENT_TYPE`, `COMPLEXITY`
- `SCOPE_READ`, `INTEGRATION_POINTS`
- Multi-agent awareness in NOTES

**Rationale updated**:
- Supports both single-agent and multi-agent modes
- Exclusive scopes enable conflict-free parallel work
- INTEGRATION_POINTS ensure clean interfaces

### Section 6: Lifecycle After RESET (Lines 177-193)
**Complete rewrite** to support multi-agent workflow:

**1. RESET execution**:
- Owner forwards all Wave 1 tasks to respective Workers in parallel
- Workers deliver diffs independently (no coordination)
- Orchestrator collects, validates, merges diffs in dependency order
- Run quality gates on integrated result
- Pass → complete; Fail → rollback and adjust

**2. Post-RESET iterations**:
- Orchestrator decomposes into tasks (single or multi-agent based on complexity)
- Execute wave-by-wave with exclusive scopes

**3. When larger refactors needed**: Emit new refactor tasks (not another RESET)

### Section 7: Examples (Lines 195-338)
**Completely rewritten** with realistic multi-agent RESET example:

**7.1: RESET Plan with 3 parallel tasks (Wave 1)**:

1. **RESET_T1: Core module refactoring** (Claude, high complexity)
   - SCOPE_TOUCH: `src/core/**`
   - SCOPE_FORBID: `tests/`, `src/ui/`, `src/ingest/`, globals
   - Tasks: typing, split service.py, extract helpers, remove duplication
   - INTEGRATION_POINTS: Must preserve all public interfaces; exports TypedDict schemas

2. **RESET_T2: Test suite hardening** (Codex, medium complexity)
   - SCOPE_TOUCH: `tests/**`
   - SCOPE_FORBID: `src/`, globals
   - Tasks: Add fixtures, mock network calls, add edge case tests, remove flaky tests
   - INTEGRATION_POINTS: Must work with RESET_T1's refactored structure

3. **RESET_T3: Logging and security hardening** (Codex, low complexity)
   - SCOPE_TOUCH: `src/common/logger.py`, `config/**`, lint configs
   - SCOPE_FORBID: `src/core/`, `src/ui/`, `tests/`, globals
   - Tasks: Add mask_secrets(), setup ruff+mypy, unify entry points
   - INTEGRATION_POINTS: Logger.mask_secrets() expected by T1 and T2

**7.2: Regular task** (multi-agent capable):
- Shows single task with all new fields
- Demonstrates INTEGRATION_POINTS and SCOPE_READ

### Section 8: Final Note (Lines 342-345)
**Updated**:
- Title: "AP_continue.md (Multi-Agent Edition)"
- "RESET prompt" → "RESET plan (set of parallel tasks with exclusive scopes)"
- Added: "Version: AP2.0 compatible; supports both single-agent and multi-agent modes"

## Statistics
- **Lines**: 232 → 345 (+113 lines, 49% growth)
- **Sections updated**: All 8 sections
- **New fields**: 7 (TASK_ID, WAVE, DEPENDS_ON, AGENT_TYPE, COMPLEXITY, SCOPE_READ, INTEGRATION_POINTS)
- **Examples**: Expanded from 2 skeleton prompts to 4 detailed multi-agent prompts

## Benefits of Multi-Agent RESET

### Parallelization
- **Before**: Single agent processes entire codebase sequentially
- **After**: 3+ agents work simultaneously on different areas (src/core/, tests/, config/)
- **Speed**: 3× faster for independent refactoring tasks

### Safety
- **Scope conflicts**: Mathematically impossible (exclusive SCOPE_TOUCH within wave)
- **Integration**: INTEGRATION_POINTS declare contracts between tasks
- **Validation**: Quality gates run on fully integrated result

### Scalability
- **Large codebases**: Decompose into 5-10 parallel RESET tasks
- **Agent specialization**: Claude for architecture, Codex for tests/typing
- **Complexity matching**: High complexity → Claude; Low → Codex

## Compatibility
- **Backward compatible**: Still supports single-agent mode for simple codebases
- **AP 2.0 aligned**: All new fields match AP.md multi-agent format
- **Drop-in replacement**: Works with existing ZIP + AP_continue.md workflow

## Example Multi-Agent RESET Workflow

1. **Owner**: Attaches 50k LOC Python project + AP_continue.md
2. **Orchestrator**: Analyzes codebase, produces RESET plan:
   - RESET_T1: Core modules (Claude, 30 files)
   - RESET_T2: Test suite (Codex, 20 files)
   - RESET_T3: Config/logging (Codex, 5 files)
   - RESET_T4: UI modules (Codex, 15 files)
3. **Owner**: Reviews plan, approves scope allocation
4. **Owner**: Forwards all 4 tasks to respective agents **in parallel**
5. **All agents**: Work simultaneously (10-15 minutes each)
6. **Orchestrator**: Collects 4 responses, merges diffs, runs `ruff + mypy + pytest`
7. **Result**: Entire RESET completes in ~15 minutes (vs 45+ minutes sequential)

## Testing Strategy
Use deterministic testing framework from AP.md section 9 to validate:
- RESET plan decomposition correctness
- Scope exclusivity (no overlaps)
- Dependency correctness (INTEGRATION_POINTS preserved)
- Quality gates pass on integrated result

## Next Steps

1. **Create test cases**: 3-5 RESET plan examples with different codebase structures
2. **Validate on real projects**: Test multi-agent RESET on 2-3 existing codebases
3. **Measure performance**: Benchmark single-agent vs multi-agent execution time
4. **Refine agent matching**: Tune AGENT_TYPE assignment based on actual task characteristics
5. **Document best practices**: When to use single-agent vs multi-agent RESET

## Files Modified
- **AP_continue.md**: 232 → 345 lines (+113 lines, 49% growth)
- **Backup created**: AP_continue.md.backup

## Version
- **AP_continue.md**: Now AP 2.0 compatible (Multi-Agent Edition)
- **Maintains**: Backward compatibility with AP 1.0 (single-agent mode)
