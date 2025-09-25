# Analytic Programming — AP_continue.md

> **Purpose.** Allow the **Owner** to attach a ZIP (project code) + this single file and immediately continue Analytic Programming in a fresh session — *without* PRD/AGENTS/brainstorming. The codebase itself is the source of truth. This document defines:
> 1) How the **Orchestrator** begins (deep analysis → one **RESET prompt**),  
> 2) The exact Orchestrator → Worker prompt formats, and  
> 3) The Worker → Orchestrator response format and quality gates.

---

## 0) Roles (unchanged)
- **Owner**: sets priorities, approves scope, merges changes.
- **Orchestrator (ChatGPT)**: reads the code deeply, proposes focused tasks, and reviews results. In the first step **only** produces the **RESET prompt** (no code).
- **Worker (Codex Agent)**: applies code diffs in small, reviewable increments; follows scope, tests, and style.

**Guiding principles**
- Small, reversible diffs; deterministic behavior; strict interfaces; no surprises.
- Minimize dependencies; zero flakiness; no secrets in code or logs.
- Explicit **scope control** on every task: what **may** be edited vs what is **forbidden**.

---

## 1) Start here (fresh session with ZIP + this file)
1. **Owner** attaches ZIP of the repo + `AP_continue.md` into a new chat.  
2. **Orchestrator** analyzes the code (architecture, tests, types, packaging, performance smells, duplication, dead code, risky patterns) and replies with **one single artifact: the RESET prompt** — nothing else.  
3. **Owner** forwards the RESET prompt to the **Worker** (Codex Agent).  
4. After the Worker returns diffs, the Orchestrator reviews and continues with normal single‑slice tasks.

> The RESET prompt is a one‑time baseline refactor plan that unifies style, hardens structure, and removes dead/duplicate code **without changing behavior**.

---

## 2) Orchestrator → Worker **RESET prompt** (one‑time, must start with a header)
The **first line MUST be exactly**:
```
#! Codex agent prompt
```

Then use the fields below (order fixed; omit empty fields). The RESET prompt is self‑contained and may cover multiple files, but must remain **behavior‑preserving**.

```
URL={{CHAT_URL}}
TITLE=RESET: Baseline refactor & structure hardening (behavior-preserving)
SCOPE_TOUCH=<files/dirs allowed to edit, comma-separated>
SCOPE_FORBID=<files/dirs forbidden to edit, comma-separated>
CONTEXT:
- <Summarized analysis by Orchestrator: architecture map, key smells, duplication, dead code, risky patterns, performance hotspots, missing tests/types/docs>
- <Build/packaging observations, runtime entry points, env handling, logging situation>
- <Test & lint status if present; expectations>
REFactor_PLAN:
- <Atomic sub-steps, each small and reviewable; avoid cross-cutting refactors in one go>
- <Keep public interfaces stable; pin schemas/contracts>
CONSTRAINTS:
- Behavior must not change (functional equivalence)
- No new dependencies unless explicitly listed and justified
- No network in tests; do not touch secrets; keep `.env` out of VCS
- Maintain determinism; seed RNG where applicable
ACCEPTANCE:
- All linters/types/tests pass (or are added minimally and pass)
- Size of diffs is reasonable; commits logically grouped
- Logging remains key-safe; performance not degraded
DELIVERABLES:
- Unified patch/diffs (touch only SCOPE_TOUCH)
- Proposed Conventional Commit message
- Exactly one final section: `### Change Summary`
NOTES:
- Comments/docstrings in Slovak; report in English
- If any behavior must change, STOP and request scope expansion
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

## 3) Orchestrator → Worker **regular task prompt** (post‑RESET, single‑slice)
The **first line MUST be**:
```
#! Codex agent prompt
```

Then:

```
URL={{CHAT_URL}}
STEP=<free-form step label, optional>
TODO=<free-form todo label, optional>
TITLE=<short task title>
SCOPE_TOUCH=<files/dirs allowed to edit>
SCOPE_FORBID=<files/dirs forbidden to edit>
CONTEXT:
- <Concise background bullets; what exists; what must change>
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
```

**Rationale**
- This mirrors RESET format but is scoped to a single capability/change, ensuring rapid, safe iteration.

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
1. Owner forwards RESET prompt to Worker.  
2. Worker delivers diffs → Orchestrator reviews vs. **ACCEPTANCE**.  
3. Iterate with **single, focused tasks** until Owner’s goals are met.  
4. When larger refactors are needed, Orchestrator emits a new (smaller‑scope) **refactor task** — not another RESET.

---

## 7) Minimal examples

### 7.1 RESET prompt (skeleton)
```
#! Codex agent prompt
URL={{CHAT_URL}}
TITLE=RESET: Baseline refactor & structure hardening (behavior-preserving)
SCOPE_TOUCH=src/**,tests/**,tools/**
SCOPE_FORBID=.git/,dist/,build/,venv/,node_modules/,secrets/,.env
CONTEXT:
- Codebase scanned: duplicated utils (a/b/utils.py), dead modules (legacy/*), long functions (>150 LOC) in src/core/service.py
- Packaging: two entry points; unify to one CLI; logging prints secrets (mask needed)
- Types/tests: missing typing in src/core/ and few brittle tests
REFACTOR_PLAN:
- Extract pure helpers to src/common/; delete legacy/*
- Add typing to src/core/*; break service.py into service/{ingest,process,emit}.py
- Introduce ruff+mypy config; stabilize tests; mask secrets in logger
CONSTRAINTS:
- Behavior preserved; no new deps
ACCEPTANCE:
- Lint/type/test all green; diffs small and grouped
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Slovak comments; English report
```

### 7.2 Regular task (skeleton)
```
#! Codex agent prompt
URL={{CHAT_URL}}
TITLE=Add JSON schema validation and error handling to ingest pipeline
SCOPE_TOUCH=src/ingest/**,tests/**
SCOPE_FORBID=src/core/**,secrets/,.env
CONTEXT:
- Current ingest accepts arbitrary payloads; we need strict schema + error mapping
CONSTRAINTS:
- No new deps; use stdlib typing & jsonschema if already present
ACCEPTANCE:
- Invalid fields raise structured errors; tests cover happy/edge paths
DELIVERABLES:
- Diffs + Conventional Commit + ### Change Summary
NOTES:
- Determinism; no network in tests
```

---

## 8) Final note
This **AP_continue.md** is drop‑in: attach it with your ZIP and we can continue *immediately*. The Orchestrator’s first reply will be only the **RESET prompt** — no code, no extra artifacts.
