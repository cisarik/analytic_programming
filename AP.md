# Analytic Programming Protocol (Multi-Agent Edition)

> **Purpose.** Make collaboration between **Owner** (you), **Orchestrator** (me), and **Workers** (multiple coding agents) smooth, deterministic, and reviewable. This document standardizes task prompts, responses, scope control, parallel execution, and quality gates while staying lightweight.

---

## 0) Roles & responsibilities
- **Owner (you)**: sets product vision and priorities, approves scope, merges changes.
- **Orchestrator (ChatGPT)**: decomposes objectives into atomic tasks, builds dependency graphs, allocates exclusive scopes, drafts precise prompts, coordinates parallel execution waves, integrates results, reviews Worker outputs.
- **Workers (Coding Agents)**: multiple agents (Codex, Claude, GPT-4, etc.) apply focused code diffs in parallel; each follows exclusive scope, tests, and style; reports back in the exact response format.

**Guiding principles**
- Small, reversible diffs; deterministic behavior; strict interfaces; no surprises.
- **Exclusive scope allocation**: no two agents touch the same file simultaneously.
- **Wave-based execution**: parallel tasks within waves; sequential waves for dependencies.
- Tests before/with changes for core logic; UI tests are optional and skipped on CI.
- Minimize dependencies; never touch secrets; zero flakiness.
- Be explicit about **what may be edited** (SCOPE), **what is forbidden**, and **what can be read**.

---

## 1) Repository & artifacts (baseline)
- **PRD.md**: product requirements, always the single source of truth.
- **AP.md**: this protocol + the **Boot Prompt** and project‑specific rules.
- **.env** (git‑ignored): secrets; never printed in logs or diffs.
- **Quality gates**: `ruff`, `mypy --strict`, `pytest`. UI/Qt tests optional and skipped on CI.
- **Logging**: requests/responses pretty‑printed; API keys masked; trace IDs per move/task.

---

## 2) Multi-Agent Orchestration (Wave-Based Execution)

### 2.1) Task Decomposition & Dependency Graph
When Owner requests work, Orchestrator:
1. **Analyzes** the request and codebase structure
2. **Decomposes** into atomic, testable tasks
3. **Builds dependency graph**: identifies which tasks depend on others
4. **Allocates exclusive scopes**: each task gets unique `SCOPE_TOUCH` (no overlaps)
5. **Assigns to waves**: 
   - Wave 1: all tasks with no dependencies (parallel)
   - Wave 2: tasks depending only on Wave 1 (parallel within wave)
   - Wave N: tasks depending on Wave N-1 or earlier
6. **Matches agents**: assigns task to appropriate agent type based on complexity/capability

### 2.2) Scope Conflict Prevention Algorithm
```
For each task T in wave W:
  T.SCOPE_TOUCH = {files/dirs T may edit}
  T.SCOPE_READ = {files T may read but not edit}
  T.SCOPE_FORBID = GLOBAL_FORBID ∪ (⋃ all other tasks' SCOPE_TOUCH in wave W)

Validation:
  ∀ tasks T1, T2 in same wave W:
    T1.SCOPE_TOUCH ∩ T2.SCOPE_TOUCH = ∅  (no edit conflicts)
    
  If validation fails → split into sequential waves
```

**GLOBAL_FORBID** (never editable by any agent):
- `.git/`, `venv/`, `.env`, `node_modules/`, `dist/`, `build/`, `secrets/`, `__pycache__/`
- Any files explicitly marked as read-only by Owner

### 2.3) Agent Types & Capability Matching
Each agent type declares capabilities:
```
AGENT_TYPES:
  codex:
    strengths: [refactoring, type_hints, python, js]
    speed: fast
    context_window: medium
  
  claude:
    strengths: [architecture, complex_logic, cross_file_changes, analysis]
    speed: medium
    context_window: large
  
  gpt4:
    strengths: [algorithms, performance, testing, debugging]
    speed: slow
    context_window: large
```

Orchestrator assigns based on:
- Task complexity (low/medium/high)
- Required file types (py, js, ts, etc.)
- Nature of work (refactor, feature, fix, test)
- Agent availability and load

### 2.4) Wave Execution Protocol
```
For wave W:
  1. Orchestrator sends all W tasks to respective agents IN PARALLEL
  2. Agents work independently (no coordination needed due to exclusive scopes)
  3. Orchestrator collects all responses
  4. Validates: all tasks passed acceptance criteria
  5. If any task FAILS:
     - Mark dependent tasks in later waves as BLOCKED
     - Owner decides: fix & retry, or adjust plan
  6. If all tasks PASS:
     - Merge diffs in dependency order (if within-wave deps exist)
     - Run quality gates (lint, type, test) on integrated result
     - Proceed to Wave W+1

STOP conditions:
  - Any task violates SCOPE_FORBID → immediate abort
  - Merge conflicts detected → Orchestrator requests scope renegotiation
  - Quality gates fail → all wave results rolled back
```

### 2.5) Integration & Merge Strategy
After wave completion:
1. **Dependency-ordered merge**: apply diffs respecting task dependencies
2. **Conflict detection**: check for unexpected overlaps (should be impossible if scopes correct)
3. **Interface validation**: verify contracts between tasks (function signatures, schemas)
4. **Quality gates**: run full test suite, linters, type checkers
5. **Rollback plan**: if integration fails, revert entire wave atomically

### 2.6) Failure Handling & Recovery
- **Task failure**: re-assign to different agent OR split into smaller tasks OR escalate to Owner
- **Scope violation**: immediate abort; Orchestrator re-plans with corrected scopes
- **Integration failure**: rollback wave; analyze conflicts; re-plan with adjusted scopes
- **Timeout**: mark as failed; Owner decides retry strategy

---

## 3) Orchestrator → Worker prompt (MUST start with a header)
The **first line MUST be exactly**:
```
#! Codex agent prompt
```

Then use the fields below (plain text; order fixed). Empty fields may be omitted.

```
TASK_ID=<unique task identifier within session, e.g., T1, T2.1, T3>
WAVE=<execution wave number, e.g., 1, 2, 3>
DEPENDS_ON=<comma-separated task IDs this depends on, e.g., T1,T2; empty if wave 1>
AGENT_TYPE=<preferred agent: codex|claude|gpt4|auto>
COMPLEXITY=<low|medium|high>
STEP=<free-form step identifier, optional>
TODO=<free-form todo identifier, optional>
TITLE=<short task title>
SCOPE_TOUCH=<files/dirs allowed to edit, comma-separated; MUST be exclusive within wave>
SCOPE_READ=<files/dirs may read but not edit, comma-separated, optional>
SCOPE_FORBID=<files/dirs forbidden to edit, comma-separated>
CONTEXT:
- <concise background bullets, optional>
INTEGRATION_POINTS:
- <interfaces/contracts with other tasks, e.g., "T2 expects function foo(x: int) -> str in module.py">
CONSTRAINTS:
- <constraint 1>
- <constraint 2>
ACCEPTANCE:
- <criterion 1>
- <criterion 2>
DELIVERABLES:
- Concise diff summary (only key hunks within SCOPE_TOUCH; no full patch dump)
- Proposed Conventional Commit message
- Exactly one final section: `### Change Summary`
NOTES:
- Comments/docstrings in Slovak; report in English
- Determinism; no network in tests; skip UI/Qt tests on CI
- No new dependencies without explicit permission
- Do not run git commands; do not write secrets
```

**Rationale**
- `SCOPE_TOUCH` and `SCOPE_FORBID` prevent collateral edits.
- `CONSTRAINTS` and `ACCEPTANCE` are the contract.
- `STEP`/`TODO` are free‑form labels (no hard numbering needed).

**Multi-agent example (Wave 1: parallel tasks)**
```
#! Codex agent prompt
TASK_ID=T1
WAVE=1
DEPENDS_ON=
AGENT_TYPE=codex
COMPLEXITY=medium
TITLE=Implement click-to-place UI components
SCOPE_TOUCH=scrabgpt/ui/app.py,scrabgpt/ui/board.py
SCOPE_READ=scrabgpt/core/game.py
SCOPE_FORBID=scrabgpt/core/,scrabgpt/ai/,tests/
CONTEXT:
- Need UI for placing tiles on board with click interaction
INTEGRATION_POINTS:
- T2 expects Board.place_tile(x, y, tile) -> bool method
CONSTRAINTS:
- Keep UI resizable; no breaking existing interactions
ACCEPTANCE:
- Click-to-place works; visual feedback on hover
- ruff/mypy --strict pass
DELIVERABLES:
- Concise diff summary (key hunks only)
- Conventional Commit
- ### Change Summary
NOTES:
- Slovak comments; English report
```

```
#! Codex agent prompt
TASK_ID=T2
WAVE=1
DEPENDS_ON=
AGENT_TYPE=claude
COMPLEXITY=high
TITLE=Implement AI scoring and validation logic
SCOPE_TOUCH=scrabgpt/ai/client.py,scrabgpt/ai/scorer.py
SCOPE_READ=scrabgpt/core/game.py,scrabgpt/ui/board.py
SCOPE_FORBID=scrabgpt/ui/,scrabgpt/core/,tests/
CONTEXT:
- Need OpenAI-based tile scoring and word validation
INTEGRATION_POINTS:
- Provides score_placement(board_state, tiles) -> int for T3
- T1 calls place_tile() which internally validates via this module
CONSTRAINTS:
- Log OpenAI requests/responses with masked key
- No network in tests (mock API)
ACCEPTANCE:
- Score calculation correct; bingo +50 bonus works
- API key never exposed in logs
- pytest all green
DELIVERABLES:
- Conventional Commit message
- ### Change Summary
NOTES:
- Deterministic; mock API responses in tests
```

**Wave 2 example (depends on Wave 1)**
```
#! Codex agent prompt
TASK_ID=T3
WAVE=2
DEPENDS_ON=T1,T2
AGENT_TYPE=gpt4
COMPLEXITY=medium
TITLE=Integrate UI with AI scoring and add end-to-end tests
SCOPE_TOUCH=tests/test_integration.py,scrabgpt/main.py
SCOPE_READ=scrabgpt/ui/app.py,scrabgpt/ai/client.py
SCOPE_FORBID=scrabgpt/core/
CONTEXT:
- T1 provides UI, T2 provides scoring; now wire together and test
INTEGRATION_POINTS:
- Uses Board.place_tile() from T1
- Uses score_placement() from T2
CONSTRAINTS:
- Tests must be deterministic; mock all AI calls
ACCEPTANCE:
- End-to-end test: place tiles → score calculated → result displayed
- All quality gates pass
DELIVERABLES:
- Conventional Commit message
- ### Change Summary
```

---

## 4) Worker → Orchestrator response (strict format)
Worker must respond in the following order. When something doesn’t apply, the section can be omitted (not replaced with placeholders).

1) **Concise Diff Summary** (touching only `SCOPE_TOUCH`): highlight key hunks and intent; avoid pasting full patches unless explicitly requested.
2) **Test & lint status** (expected results locally):  
   - `ruff`: OK/violations (short)  
   - `mypy --strict`: OK/issues (short)  
   - `pytest`: OK/failing tests (short; include counts)
3) **Migration notes** (if any): config/env/data migrations, one-liners.
4) **Known limitations & edge cases** (bullet list).
5) **Rollback plan** (how to revert the change set safely).
6) **Proposed Conventional Commit** (one line).
7) **Exactly one** terminal section:
```
### Change Summary
- What changed and why (short, plain English)
```

**If acceptance cannot be fully met**
- Produce partial diff summaries **or** no diffs, plus a concise **Failure Report**:
  - What blocked the task (facts only)
  - What was tried (brief)
  - Proposed next actionable steps or an adjusted prompt

**Hard requirements**
- No secrets in diffs or logs.
- Do not run git or system package managers.
- Respect `SCOPE_FORBID`. If a change is needed there, stop and request scope expansion.

---

## 5) Task design guidelines (Orchestrator rules)
- **Atomize** tasks: one capability at a time; avoid cross‑cutting refactors.
- **Pin interfaces**: schemas, params, and contracts stated explicitly.
- **Timebox retries**: schema/JSON violations → at most 1 guided retry; then escalate.
- **Be incremental**: feature‑flags (when helpful), default to off; preserve backward compatibility.
- **Keep payloads compact**: especially for model calls; never ship unnecessary state.
- **Determinism**: seed RNG; stable snapshot tests for pure logic.

---

## 6) Quality & safety rails
- **Dependencies**: adding or updating requires explicit approval in the prompt; otherwise use stdlib/existing libs.
- **Testing**: core logic covered; UI tests optional; avoid flakiness; no network in tests.
- **Logging**: pretty‑print JSON requests/responses; mask keys; include `trace_id` per task or move.
- **Performance**: avoid accidental O(N^3) passes in hot paths; prefer clarity but watch allocations.
- **Security**: never print `.env` contents; red‑flag any PII or secret handling in review.
- **Accessibility/UX**: resizable layouts; color‑blind aware palettes when possible.

---

## 7) Versioning & compatibility
- This spec is **AP2.0 (Multi-Agent Edition)**. Include `AP2.0` in AGENTS.md so Worker knows the contract version.
- Previous version AP1.0 (single-agent) remains supported for backward compatibility
- Future updates will be AP2.1, AP2.2, …; prompts may reference `AP_VERSION=AP2.0` explicitly
- Agents must declare which AP versions they support

---

## 8) Boot Prompt (to include in AGENTS.md)
> Use this exact section verbatim inside **AGENTS.md** so Codex Agent has a stable operating mode.

```
You are Worker agent operating under Analytic Programming protocol (Multi-Agent Edition).

**Core principles**:
- Work in small, reviewable diffs; respect SCOPE_TOUCH/SCOPE_READ/SCOPE_FORBID strictly
- You may work in parallel with other agents on the same codebase
- Your SCOPE_TOUCH is exclusive: no other agent will touch these files in your wave
- Comments/docstrings in Slovak; report in English
- Deterministic behavior; no network in tests; skip UI/Qt tests on CI
- Never run git or system commands; never write secrets to code or logs
- Log model requests/responses (keys masked)

**Multi-agent awareness**:
- Check TASK_ID, WAVE, DEPENDS_ON: understand your task's position in workflow
- Respect INTEGRATION_POINTS: other tasks depend on interfaces you define
- If you need to edit files in SCOPE_FORBID, STOP and request scope expansion
- Your work will be merged with other agents' work: preserve contracts

You will receive prompts whose **first line is**: `#! Codex agent prompt`.
Follow all fields (TASK_ID, WAVE, DEPENDS_ON, AGENT_TYPE, TITLE, SCOPE_*, CONTEXT, INTEGRATION_POINTS, CONSTRAINTS, ACCEPTANCE, DELIVERABLES, NOTES).
Return your response in the **Worker → Orchestrator** format defined by AP section 4, ending with exactly one `### Change Summary`.
If acceptance cannot be met, stop, provide a Failure Report (facts only), and propose the next task.
```

---

<<<<<<< HEAD
## 9) Deterministic Testing System for AP

### 9.1) Purpose
Validate that the Orchestrator correctly:
- Decomposes requests into tasks
- Allocates exclusive scopes (no conflicts)
- Builds correct dependency graphs
- Assigns appropriate waves and agent types
- Generates valid prompts conforming to protocol

### 9.2) Test Case Structure
Each test case is a YAML/JSON file containing:

```yaml
test_id: "MA001"
description: "Parallel UI and AI tasks with integration task"
input:
  codebase_structure:
    - "scrabgpt/ui/app.py"
    - "scrabgpt/ui/board.py"
    - "scrabgpt/ai/client.py"
    - "scrabgpt/ai/scorer.py"
    - "scrabgpt/core/game.py"
    - "tests/test_integration.py"
  request: "Add click-to-place UI and AI scoring with OpenAI, then integrate"
  
expected_output:
  tasks:
    - task_id: "T1"
      wave: 1
      depends_on: []
      scope_touch: ["scrabgpt/ui/app.py", "scrabgpt/ui/board.py"]
      scope_forbid: ["scrabgpt/core/", "scrabgpt/ai/", "tests/"]
      agent_type: "codex"
      
    - task_id: "T2"
      wave: 1
      depends_on: []
      scope_touch: ["scrabgpt/ai/client.py", "scrabgpt/ai/scorer.py"]
      scope_forbid: ["scrabgpt/ui/", "scrabgpt/core/", "tests/"]
      agent_type: "claude"
      
    - task_id: "T3"
      wave: 2
      depends_on: ["T1", "T2"]
      scope_touch: ["tests/test_integration.py"]
      scope_forbid: ["scrabgpt/core/"]
      agent_type: "gpt4"
  
  validations:
    - scope_conflicts: false  # No T1.SCOPE_TOUCH ∩ T2.SCOPE_TOUCH
    - wave_1_parallel: true
    - wave_2_depends_on_wave_1: true
    - all_global_forbid_respected: true
```

### 9.3) Validation Rules
Automated validator checks:
1. **Scope exclusivity**: ∀ tasks Ti, Tj in same wave: Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅
2. **Dependency consistency**: If Ti depends on Tj, then wave(Ti) > wave(Tj)
3. **Scope coverage**: ⋃ all SCOPE_TOUCH covers all files mentioned in request
4. **FORBID correctness**: Each task's SCOPE_FORBID includes GLOBAL_FORBID + other tasks' SCOPE_TOUCH
5. **Prompt format**: Generated prompts conform to section 3 format
6. **Integration points**: Tasks with dependencies declare INTEGRATION_POINTS

### 9.4) Test Categories
- **MA-BASIC**: Simple 2-3 parallel tasks, no dependencies
- **MA-SEQUENTIAL**: 3+ tasks in sequential waves
- **MA-COMPLEX**: Mixed parallel/sequential with 5+ tasks, multiple waves
- **MA-CONFLICT**: Cases that should detect and prevent scope conflicts
- **MA-AGENT-MATCH**: Validate appropriate agent type assignment
- **MA-FAILURE**: Test failure handling and rollback scenarios

### 9.5) Test Execution
```python
# Pseudo-code for test runner
def test_orchestrator(test_case):
    # 1. Load test case
    tc = load_yaml(test_case)
    
    # 2. Run orchestrator
    result = orchestrator.decompose(
        request=tc.input.request,
        codebase=tc.input.codebase_structure
    )
    
    # 3. Validate structure
    assert len(result.tasks) == len(tc.expected_output.tasks)
    
    # 4. Validate each task
    for i, task in enumerate(result.tasks):
        expected = tc.expected_output.tasks[i]
        assert task.task_id == expected.task_id
        assert task.wave == expected.wave
        assert set(task.depends_on) == set(expected.depends_on)
        assert set(task.scope_touch) == set(expected.scope_touch)
        # ... more assertions
    
    # 5. Run validation rules
    assert no_scope_conflicts_in_wave(result.tasks)
    assert dependencies_respect_waves(result.tasks)
    assert scope_coverage_complete(result.tasks, tc.input.request)
    assert forbid_includes_global_and_others(result.tasks)
    
    return "PASS"
```

### 9.6) Regression Suite
Maintain a suite of test cases covering:
- Common request patterns (feature + tests, refactor + types, bug fix + tests)
- Edge cases (single file, entire module, cross-cutting concerns)
- Failure modes (circular dependencies, impossible scope allocation)
- Performance (large codebases, 10+ parallel tasks)

### 9.7) Continuous Validation
- Run test suite before deploying AP protocol changes
- Add new test case for each discovered orchestration bug
- Benchmark: all tests should pass deterministically every time

---

## 10) Advanced Prompt Engineering Ideas

### 10.1) Load Balancing & Task Distribution
**Idea**: Add `ESTIMATED_DURATION` and `PRIORITY` to balance agent workload
```
ESTIMATED_DURATION=<short|medium|long>  # helps distribute work evenly
PRIORITY=<critical|high|medium|low>      # affects execution order within wave
```
Benefits: prevents one agent from being bottleneck; critical tasks start first

### 10.2) Progress Tracking & Real-time Status
**Idea**: Agents emit progress events during work
```
# Agent emits during execution:
PROGRESS: 25% - Analyzing codebase
PROGRESS: 50% - Implementing core logic
PROGRESS: 75% - Writing tests
PROGRESS: 100% - Finalizing
```
Benefits: Owner visibility; early detection of stuck agents; better ETA

### 10.3) Partial Rollback & Granular Recovery
**Idea**: Instead of rolling back entire wave on failure, identify minimal rollback set
```
If T3 fails and T5 depends on T3:
  - Rollback only T3 and T5 (not independent T1, T2, T4)
  - Re-execute just failed dependency chain
  - Keep successful independent work
```
Benefits: faster recovery; less wasted work

### 10.4) Adaptive Re-planning
**Idea**: Orchestrator adjusts plan based on intermediate results
```
After Wave 1 completes:
  - Analyze actual complexity vs estimated
  - Detect new dependencies discovered during implementation
  - Re-optimize Wave 2+ task allocation
  - Suggest scope adjustments to Owner
```
Benefits: plan adapts to reality; better resource utilization

### 10.5) Agent Capability Learning
**Idea**: Track agent performance metrics to improve future assignments
```
METRICS_PER_AGENT:
  codex:
    avg_duration: {refactor: 5min, feature: 12min, tests: 8min}
    success_rate: {refactor: 95%, feature: 85%, tests: 90%}
    best_for: [type_hints, small_refactors, unit_tests]
  
  claude:
    avg_duration: {architecture: 20min, complex_logic: 15min}
    success_rate: {architecture: 92%, complex_logic: 88%}
    best_for: [multi_file_changes, algorithms, design_patterns]
```
Benefits: smarter agent assignment over time; predictable performance

### 10.6) Cross-Wave Optimization
**Idea**: Reorder tasks to maximize parallelism
```
Original plan:
  Wave 1: T1, T2
  Wave 2: T3 (depends on T1)
  Wave 3: T4 (depends on T3)

Optimized:
  Wave 1: T1, T2, T4_prep (independent part of T4)
  Wave 2: T3 (depends on T1), T4_final (depends on T3, T4_prep)
```
Benefits: more parallel work; faster completion; better resource usage

### 10.7) Dry-Run & Validation Mode
**Idea**: Execute orchestration logic without sending to agents
```
DRY_RUN=true in Orchestrator mode:
  1. Decompose request
  2. Allocate scopes
  3. Build dependency graph
  4. Validate all constraints
  5. Generate all prompts
  6. Output plan for Owner review
  7. STOP (don't execute)
```
Benefits: validate plan before expensive execution; catch errors early

### 10.8) Conflict Prediction (ML-based)
**Idea**: Predict merge conflicts before execution using ML
```
For each pair (Ti, Tj) in same wave:
  semantic_similarity = embedding_distance(Ti.code_context, Tj.code_context)
  conflict_probability = model.predict(
    scope_overlap=0,
    semantic_similarity=semantic_similarity,
    file_coupling=coupling_metric(Ti.SCOPE_READ, Tj.SCOPE_READ)
  )
  
  if conflict_probability > threshold:
    → move Ti or Tj to different wave
```
Benefits: proactive conflict avoidance; higher integration success rate

### 10.9) Dynamic Scope Adjustment Protocol
**Idea**: Allow agents to request scope changes mid-task
```
# Agent discovers it needs to edit file in SCOPE_FORBID
Agent response:
  STATUS=BLOCKED
  REASON=Need to edit scrabgpt/core/game.py (currently in SCOPE_FORBID)
  REQUESTED_SCOPE_ADDITION=scrabgpt/core/game.py
  JUSTIFICATION=Must update GameState interface to support new feature
  
Orchestrator:
  1. Check if requested file is in another agent's SCOPE_TOUCH
  2. If yes → coordinate with that agent or sequential ordering
  3. If no → grant scope expansion and resume
  4. Update SCOPE_FORBID for other agents in wave
```
Benefits: flexibility; handles unforeseen dependencies; reduces false starts

### 10.10) Quality & Performance Metrics
**Idea**: Track and optimize orchestration quality over time
```
SESSION_METRICS:
  total_tasks: 12
  waves_executed: 3
  total_duration: 45min
  integration_conflicts: 0
  quality_gate_passes: {wave1: true, wave2: true, wave3: true}
  scope_violations: 0
  scope_expansions: 2
  
AGENT_PERFORMANCE:
  codex: {tasks: 4, avg_duration: 8min, success: 100%}
  claude: {tasks: 5, avg_duration: 10min, success: 100%}
  gpt4: {tasks: 3, avg_duration: 12min, success: 100%}
  
OPTIMIZATION_SUGGESTIONS:
  - Wave 2 could have been merged with Wave 1 (no real dependency)
  - Consider splitting T7 (too complex, 25min duration)
```
Benefits: continuous improvement; data-driven decisions; transparency

### 10.11) Contract-First Development
**Idea**: Generate interfaces/contracts before implementation tasks
```
Wave 0 (Contract Definition):
  - Define all function signatures
  - Specify data schemas
  - Document interfaces between components
  - Generate stub implementations
  
Wave 1+ (Implementation):
  - Implement against frozen contracts
  - No interface changes allowed (only internals)
  - Integration guaranteed by design
```
Benefits: eliminates integration issues; enables true parallelism; design clarity

### 10.12) Speculative Execution
**Idea**: Start likely Wave N+1 tasks before Wave N completes
```
While Wave 2 executing:
  - Analyze which Wave 3 tasks are likely independent of Wave 2 results
  - Start Wave 3 tasks speculatively
  - If Wave 2 changes interfaces → discard speculative work
  - If Wave 2 preserves contracts → keep speculative work
  
Tradeoff: risk of wasted work vs potential time savings
```
Benefits: reduced latency; better resource utilization (if cache hit rate high)

---

## 11) Multi-Agent Lifecycle
1. **Owner states objective** → Orchestrator analyzes codebase and request
2. **Orchestrator decomposes** → Builds task graph, allocates scopes, assigns waves
3. **Owner reviews plan** → Approves task allocation, scope assignments, wave structure
4. **Wave execution**:
   - Orchestrator sends all Wave N tasks to respective agents IN PARALLEL
   - Each agent works independently with exclusive scope
   - Orchestrator collects responses
5. **Integration & validation**:
   - Merge diffs in dependency order
   - Run quality gates (lint, type, test)
   - If pass → proceed to next wave
   - If fail → rollback, re-plan, retry
6. **Owner review** → Examines integrated changes, approves or requests adjustments
7. **Iterate** → Continue with remaining waves until objective complete

**Single-agent mode**: For simple tasks, Orchestrator may skip multi-agent decomposition and send single task to one agent (backward compatible).

---
