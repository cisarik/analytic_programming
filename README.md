# Analytic Programming

Analytic Programming (AP) is a collaboration protocol between the Owner, Orchestrator, and Worker that enforces small deterministic increments and transparent quality control. It clearly separates prompt design (Orchestrator) from implementation (Worker) while keeping all project truth in `PRD.md` and `AP.md`.

## What AP Provides
- A permanent reference document `AP.md` describing roles, prompt formats, and quality expectations.
- A disciplined Owner → Orchestrator → Worker loop that favors small, reversible diffs.
- Better auditability thanks to precise inputs (PRD) and structured Worker responses.

## Required Artifacts
- `AP.md`: the definitive Analytic Programming Protocol specification (currently version AP1.0) including the Boot Prompt.
- `PRD.md`: product requirements; the single source of truth for functional scope.

> Whenever you share a prompt or a task, **always attach `AP.md` together with the corresponding `PRD.md`**. The Orchestrator needs both to craft valid tasks and to ensure the Worker uses the current Boot Prompt.

## Roles and Workflow
- **Owner** sets goals, prioritizes, and approves scope.
- **Orchestrator** reads `PRD.md`, derives atomic tasks, and prepares Worker prompts exactly according to the template defined in `AP.md`.
- **Worker (Codex Agent)** changes only what is listed in `SCOPE_TOUCH`, reports in the strict response format, and satisfies the quality gates.

## Sample Prompt for the Orchestrator
Use the prompt below when you need the Orchestrator to analyze a fresh PRD and prepare the first INIT step. Adjust the INFO section so it matches your project context.

```
You are the Orchestrator for project <ProjectName> operating under Analytic Programming protocol AP1.0.

INFO
- AP.md (attached): authoritative protocol specification with Boot Prompt.
- PRD.md (attached): product requirements to be broken down.

Tasks
1. Read AP.md and confirm you will obey every rule in Sections 2 and 3 when crafting worker prompts.
2. Thoroughly analyze PRD.md, extract scope, risks, acceptance criteria, and constraints relevant for the first delivery step.
3. Design the very first INIT worker task that will move the project forward while staying within the minimal viable scope.

Return the results as a JSON object with fields:
- `boot_prompt`: exact text block from section "Boot Prompt" in AP.md (no edits, keep formatting).
- `init_step_prompt`: complete worker prompt for the INIT task, fully matching the template from AP.md (include the `#! Codex agent prompt` header and fill all required fields).
- `analysis_notes`: bullet summary (strings) of the most important insights from PRD.md that shaped the INIT step.

Do not execute the task yourself; only provide the boot prompt and the INIT worker prompt synthesized from the documents.
```

This prompt ensures the Orchestrator:
- uses `AP.md` as the authoritative rule set,
- thoroughly reviews `PRD.md`,
- delivers the exact Boot Prompt (copied from `AP.md`) and the initial Worker INIT prompt.
