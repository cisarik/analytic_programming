# Analytic Programming — AP_continue.md (Multi-Agent Edition)

> **Purpose.** Allow the **Owner** to attach a ZIP (project code) + this single file and immediately continue Analytic Programming in a fresh session — *without* PRD/AGENTS/brainstorming. The codebase itself is the source of truth. This document defines:
> 1) How the **Orchestrator** begins (deep analysis → **RESET plan** with multiple parallel tasks),  
> 2) The exact Orchestrator → Worker prompt formats (multi-agent, wave-based),  
> 3) The Worker → Orchestrator response format and quality gates.

---

## 0) Roles
- **Owner**: sets priorities, approves scope, merges changes.
- **Orchestrator (ChatGPT)**: reads the code deeply, decomposes RESET into parallel tasks with exclusive scopes, builds dependency graph, assigns agents, coordinates wave execution, reviews results. In the first step **only** produces the **RESET plan** (no code).
- **Workers (Multiple Agents)**: Codex, Claude, GPT-4, etc. apply code diffs in parallel; each follows exclusive scope, tests, and style; no coordination needed between agents.

**Guiding principles**
- Small, reversible diffs; deterministic behavior; strict interfaces; no surprises.
- **Exclusive scope allocation**: no two agents touch the same file simultaneously in RESET.
- **Wave-based execution**: parallel tasks within waves; sequential waves for dependencies.
- Minimize dependencies; zero flakiness; no secrets in code or logs.
- Explicit **scope control** on every task: what **may** be edited, what can be **read**, what is **forbidden**.

---

## 1) Start here (fresh session with ZIP + this file)
1. **Owner** attaches ZIP of the repo + `AP_continue.md` into a new chat.  
2. **Orchestrator** analyzes the code (architecture, tests, types, packaging, performance smells, duplication, dead code, risky patterns) and replies with **RESET plan**: a set of parallel tasks with exclusive scopes, organized into waves — nothing else.  
3. **Owner** reviews the RESET plan (task decomposition, scope allocation, wave structure).
4. **Owner** forwards each RESET task to the **appropriate Worker** (may send all Wave 1 tasks in parallel).  
5. **Orchestrator** collects responses, merges diffs, validates quality gates.
6. After RESET completes, Orchestrator continues with normal feature tasks.

> The RESET plan is a one‑time baseline refactor that unifies style, hardens structure, and removes dead/duplicate code **without changing behavior**. It's decomposed into parallel tasks when possible (e.g., separate agents for tests/, src/ui/, src/core/).

---

## 2) Orchestrator → Worker **RESET task** (multi-agent, wave-based)
The **first line MUST be exactly**:
```
#! Codex agent prompt
```

Then use the fields below (order fixed; omit empty fields). Each RESET task has **exclusive scope** and may run in parallel with other RESET tasks in the same wave.

```
TASK_ID=<unique ID, e.g., RESET_T1, RESET_T2>
WAVE=<execution wave number, typically 1 for most RESET tasks>
DEPENDS_ON=<comma-separated task IDs, if any dependencies>
AGENT_TYPE=<codex|claude|gpt4|auto>
COMPLEXITY=<low|medium|high>
URL={{CHAT_URL}}
TITLE=RESET: <specific refactor area, e.g., "Test suite hardening" or "Core module typing">
SCOPE_TOUCH=<files/dirs allowed to edit, comma-separated; MUST be exclusive within wave>
SCOPE_READ=<files/dirs may read but not edit, comma-separated>
SCOPE_FORBID=<files/dirs forbidden to edit, comma-separated>
CONTEXT:
- <Summarized analysis specific to this task: smells, duplication, dead code, patterns in SCOPE_TOUCH>
- <Build/packaging observations relevant to this scope>
- <Test & lint status for this scope; expectations>
INTEGRATION_POINTS:
- <Interfaces/contracts with other RESET tasks, e.g., "RESET_T2 expects Logger.mask_secrets() available">
REFACTOR_PLAN:
- <Atomic sub-steps for THIS scope only>
- <Keep public interfaces stable; pin schemas/contracts>
CONSTRAINTS:
- Behavior must not change (functional equivalence)
- No new dependencies unless explicitly listed and justified
- No network in tests; do not touch secrets; keep `.env` out of VCS
- Maintain determinism; seed RNG where applicable
ACCEPTANCE:
- All linters/types/tests pass for this scope
- Size of diffs is reasonable; changes focused
- Logging remains key-safe; performance not degraded
DELIVERABLES:
- Unified patch/diffs (touch only SCOPE_TOUCH)
- Proposed Conventional Commit message
- Exactly one final section: `### Change Summary`
NOTES:
- Comments/docstrings in Slovak; report in English
- If any behavior must change, STOP and request scope expansion
- Other agents may be working on other parts of codebase simultaneously
```

**Typical SCOPE defaults**
- `SCOPE_TOUCH`: `src/**, app/**, package/**, tests/**, tools/**` (adjust to repo)  
- `SCOPE_FORBID`: `.git/, venv/, dist/, build/, node_modules/, .env, secrets/, large_assets/`

**What the RESET typically includes**
- Remove dead/duplicated code; unify naming/layout; split god‑objects.
- Introduce type annotations; enforce lints (`ruff` or repo lint); add missing tests for core logic only.
- Stabilize packaging & entry‑points; isolate side effects; harden logging (mask secrets).
- Extract pure utilities; cap function/module sizes; add simple CI config if repo uses it.
- Keep UX and external APIs stable; do not modify licensed assets.

---

## 3) Orchestrator → Worker **regular task** (post‑RESET, multi-agent capable)
The **first line MUST be**:
```
#! Codex agent prompt
```

Then:

```
TASK_ID=<unique ID, e.g., T1, T2.1, T3>
WAVE=<execution wave number>
DEPENDS_ON=<comma-separated task IDs, if any dependencies>
AGENT_TYPE=<codex|claude|gpt4|auto>
COMPLEXITY=<low|medium|high>
URL={{CHAT_URL}}
STEP=<free-form step label, optional>
TODO=<free-form todo label, optional>
TITLE=<short task title>
SCOPE_TOUCH=<files/dirs allowed to edit; MUST be exclusive within wave>
SCOPE_READ=<files/dirs may read but not edit, comma-separated>
SCOPE_FORBID=<files/dirs forbidden to edit>
CONTEXT:
- <Concise background bullets; what exists; what must change>
INTEGRATION_POINTS:
- <Interfaces/contracts with other tasks in this session>
CONSTRAINTS:
- <Constraints 1..n>
ACCEPTANCE:
- <Testable, specific criteria 1..n>
DELIVERABLES:
- Unified patch/diffs (touch only SCOPE_TOUCH)
- Proposed Conventional Commit message
- Exactly one `### Change Summary`
NOTES:
- Comments/docstrings in Slovak; report in English
- Determinism; no network in tests; skip heavy UI tests on CI
- No new dependencies without explicit permission
- Other agents may be working on other parts of codebase simultaneously
```

**Rationale**
- Supports both single-agent mode (simple tasks) and multi-agent mode (parallel execution)
- Exclusive scopes enable conflict-free parallel work
- INTEGRATION_POINTS ensure clean interfaces between parallel tasks

---

## 4) Worker → Orchestrator **response format** (strict)
Worker must respond in the following order. Non‑applicable sections may be omitted.

1) **Unified Diffs** (paths clear; only within `SCOPE_TOUCH`).
2) **Test & lint status** (expected local results):  
   - linter(s): OK/violations (short)  
   - type checker: OK/issues (short)  
   - tests: OK/failing (counts; highlight new/changed tests)
3) **Migration notes** (config/env/data), one‑liners.
4) **Known limitations & edge cases** (bullets).
5) **Rollback plan** (how to revert safely).
6) **Proposed Conventional Commit** (one line).
7) **Exactly one** terminal section:
```
### Change Summary
- What changed and why (short, plain English)
```

**Hard requirements**
- No secrets in diffs/logs.  
- No git/system commands in the response.  
- Respect `SCOPE_FORBID`. Request scope expansion if needed.

---

## 5) Quality gates (repo‑agnostic)
- Use repo’s own tools if present. If none, Worker should add minimal: linter + type checker + tests (approved in RESET).
- **No network in tests.**  
- **Determinism** where feasible (seed RNG).  
- **Performance**: avoid N^3 regressions; prefer clarity with measured impact.  
- **Security**: never print `.env` or secrets; mask tokens in logs.  
- **Logging**: structured/pretty where possible; include trace IDs for multi‑step flows.

---
## 6) Lifecycle after RESET
1. **RESET execution**:
   - Owner forwards all Wave 1 RESET tasks to respective Workers (parallel)
   - Workers deliver diffs independently (no coordination needed)
   - Orchestrator collects all responses
   - Orchestrator validates: no scope violations, all acceptance criteria met
   - Orchestrator merges diffs in dependency order
   - Run quality gates (lint, type, test) on integrated result
   - If pass → RESET complete; if fail → rollback and adjust

2. **Post-RESET iterations**:
   - Owner states next objective
   - Orchestrator decomposes into tasks (single-agent or multi-agent based on complexity)
   - Execute wave-by-wave with exclusive scopes
   - Iterate until Owner's goals met

3. **When larger refactors needed**: Orchestrator emits new refactor tasks (not another RESET)
4. When larger refactors are needed, Orchestrator emits a new (smaller‑scope) **refactor task** — not another RESET.

---

## 7) Multi-Agent Examples

### 7.1 RESET Plan: 3 parallel tasks (Wave 1)

**RESET_T1: Core module refactoring**
```
#! Codex agent prompt
TASK_ID=RESET_T1
WAVE=1
DEPENDS_ON=
AGENT_TYPE=claude
COMPLEXITY=high
URL={{CHAT_URL}}
TITLE=RESET: Core module typing and structure (behavior-preserving)
SCOPE_TOUCH=src/core/**
SCOPE_READ=tests/,src/common/**
SCOPE_FORBID=tests/,src/ui/,src/ingest/,.git/,dist/,build/,venv/,node_modules/,secrets/,.env
CONTEXT:
- Long functions (>150 LOC) in src/core/service.py
- Missing type annotations in src/core/
- Duplicated logic between core/processor.py and core/handler.py
INTEGRATION_POINTS:
- Must preserve all public interfaces for RESET_T2 and RESET_T3
- src/core/types.py will export TypedDict schemas for other modules
REFACTOR_PLAN:
- Add typing to all src/core/ modules
- Break service.py into service/{ingest,process,emit}.py
- Extract pure helpers to src/common/utils.py
- Remove duplication between processor and handler
CONSTRAINTS:
- Behavior preserved; no new deps
- All public interfaces stable
ACCEPTANCE:
- mypy --strict passes for src/core/
- All existing tests pass
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Slovak comments; English report
```

**RESET_T2: Test suite hardening**
```
#! Codex agent prompt
TASK_ID=RESET_T2
WAVE=1
DEPENDS_ON=
AGENT_TYPE=codex
COMPLEXITY=medium
URL={{CHAT_URL}}
TITLE=RESET: Test suite hardening and determinism (behavior-preserving)
SCOPE_TOUCH=tests/**
SCOPE_READ=src/**
SCOPE_FORBID=src/,.git/,dist/,build/,venv/,node_modules/,secrets/,.env
CONTEXT:
- Few brittle tests; some tests hit network
- Missing test coverage for src/core/handler.py edge cases
- No fixtures; lots of repeated setup code
INTEGRATION_POINTS:
- Tests must work with RESET_T1's refactored core module structure
- Uses interfaces defined in src/core/types.py
REFACTOR_PLAN:
- Add pytest fixtures for common setup
- Mock all network calls; ensure determinism
- Add tests for edge cases in handler.py
- Remove flaky timing-dependent tests
CONSTRAINTS:
- Behavior preserved; no new deps (pytest/pytest-mock already present)
- No network in tests
ACCEPTANCE:
- All tests pass; pytest runs deterministically
- Coverage for src/core/ >= 80%
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Deterministic; mock all external calls
```

**RESET_T3: Logging and security hardening**
```
#! Codex agent prompt
TASK_ID=RESET_T3
WAVE=1
DEPENDS_ON=
AGENT_TYPE=codex
COMPLEXITY=low
URL={{CHAT_URL}}
TITLE=RESET: Logging security and config (behavior-preserving)
SCOPE_TOUCH=src/common/logger.py,config/**,.ruff.toml,mypy.ini
SCOPE_READ=src/**,tests/**
SCOPE_FORBID=src/core/,src/ui/,tests/,.git/,dist/,build/,venv/,node_modules/,secrets/,.env
CONTEXT:
- Logger in src/common/logger.py prints secrets (API keys visible in logs)
- No lint config; need ruff + mypy setup
- Two entry points; unify to one CLI
INTEGRATION_POINTS:
- Logger.mask_secrets() method expected by RESET_T1 and RESET_T2
REFACTOR_PLAN:
- Add mask_secrets() to logger; mask API keys, tokens, passwords
- Introduce .ruff.toml and mypy.ini with strict settings
- Delete legacy/old_entry.py; keep only src/main.py as entry point
CONSTRAINTS:
- Behavior preserved; no new deps
- Secrets never logged
ACCEPTANCE:
- grep -r "api_key" logs/ shows no actual keys
- ruff and mypy configs present and strict
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Security-critical; test secret masking thoroughly
```

### 7.2 Regular task (multi-agent capable)
```
#! Codex agent prompt
TASK_ID=T1
WAVE=1
DEPENDS_ON=
AGENT_TYPE=codex
COMPLEXITY=medium
URL={{CHAT_URL}}
TITLE=Add JSON schema validation and error handling to ingest pipeline
SCOPE_TOUCH=src/ingest/**,tests/test_ingest.py
SCOPE_READ=src/core/types.py
SCOPE_FORBID=src/core/**,src/ui/**,secrets/,.env
CONTEXT:
- Current ingest accepts arbitrary payloads; we need strict schema + error mapping
- Using TypedDict from src/core/types.py for schemas
INTEGRATION_POINTS:
- None (independent task)
CONSTRAINTS:
- No new deps; use stdlib typing & jsonschema if already present
ACCEPTANCE:
- Invalid fields raise structured errors; tests cover happy/edge paths
- mypy passes for src/ingest/
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Determinism; no network in tests
```

---

## 8) Final note
This **AP_continue.md (Multi-Agent Edition)** is drop‑in: attach it with your ZIP and we can continue *immediately*. The Orchestrator's first reply will be only the **RESET plan** (set of parallel tasks with exclusive scopes) — no code, no extra artifacts.

**Version**: AP2.0 compatible; supports both single-agent (simple tasks) and multi-agent (parallel execution) modes.
