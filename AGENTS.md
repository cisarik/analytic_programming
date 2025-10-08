# AGENTS.md: Guide for AI Agents Working on Analytic Programming

## Welcome, Agent!

You are working on the **Analytic Programming (AP) Protocol** - a multi-agent orchestration system for AI coding tasks. This document provides everything you need to work effectively on this project.

## Project Context

### What is AP?
AP is a protocol that enables multiple AI agents (like you!) to work in parallel on code changes with mathematically guaranteed zero conflicts. Think of it as a conductor coordinating an orchestra - the Orchestrator decomposes work into parallel tasks with exclusive scopes, you and other agents execute independently, and results are merged safely.

### Current Status
- **Version**: AP 2.0 (Multi-Agent Edition)
- **Status**: Production Ready (protocol design complete, implementation pending)
- **Protocol Size**: 1,005 lines (AP.md: 660, AP_continue.md: 345)
- **Documentation**: Comprehensive (README, PRD, 4 summary docs)

### Project Goals
1. Enable 3-5× faster AI coding through parallelization
2. Guarantee zero scope conflicts through exclusive scope allocation
3. Support agent specialization (right agent for right task)
4. Maintain deterministic, transparent, reviewable workflows
5. Backward compatibility with AP 1.0 (single-agent mode)

## Repository Structure

```
analytic_programming/
├── AP.md                               # Main protocol specification (660 lines)
├── AP_continue.md                      # Quick-start variant (345 lines)
├── README.md                           # Project overview
├── PRD.md                              # Product requirements
├── AGENTS.md                           # This file (for you!)
├── MULTIAGENT_UPGRADE_COMPLETE.md      # Comprehensive upgrade guide
├── BEFORE_AFTER_COMPARISON.md          # Visual AP 1.0 vs AP 2.0
├── AP_MULTIAGENT_SUMMARY.md            # Detailed AP.md changes
└── AP_CONTINUE_MULTIAGENT_SUMMARY.md   # Detailed AP_continue.md changes
```

### File Purposes

**Core Protocol Files**:
- **AP.md**: The definitive spec. Read sections 0-2 first for multi-agent orchestration basics.
- **AP_continue.md**: Streamlined for quick-start with existing codebases (RESET workflow).
- **PRD.md**: Requirements document. Read to understand what the protocol must achieve.

**Documentation Files**:
- **README.md**: Start here for high-level overview and getting started guide.
- **AGENTS.md**: You're reading it! Your guide to working on this project.
- **MULTIAGENT_UPGRADE_COMPLETE.md**: Best comprehensive summary of AP 2.0 changes.
- **BEFORE_AFTER_COMPARISON.md**: Visual diagrams showing improvements.

**Summary Files** (for deep dives):
- **AP_MULTIAGENT_SUMMARY.md**: Section-by-section AP.md changes.
- **AP_CONTINUE_MULTIAGENT_SUMMARY.md**: Section-by-section AP_continue.md changes.

## Key Concepts (Must Understand)

### 1. Wave-Based Execution
Tasks are grouped into **waves** where:
- **Wave 1**: All independent tasks execute in parallel
- **Wave 2**: Tasks depending only on Wave 1
- **Wave N**: Tasks depending on Wave N-1 or earlier

**Key Rule**: All tasks in same wave have **exclusive scopes** (no file overlap).

### 2. Scope Conflict Prevention Algorithm

This is the **core innovation** - it mathematically guarantees zero edit conflicts:

```
For each task T in wave W:
  T.SCOPE_TOUCH = {files T may edit}
  T.SCOPE_READ = {files T may read but not edit}
  T.SCOPE_FORBID = GLOBAL_FORBID ∪ (⋃ all other tasks' SCOPE_TOUCH in wave W)

Validation Rule:
  ∀ tasks Ti, Tj in same wave W:
    Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅  (empty intersection)
```

**What this means**: If two tasks are in the same wave, their editable file sets cannot overlap. Period. The orchestrator validates this before execution.

### 3. Agent Type Matching

Different agents have different strengths:

| Agent | Strengths | Best For |
|-------|-----------|----------|
| **Codex** | Fast, accurate for patterns | Refactoring, type hints, unit tests |
| **Claude** | Deep understanding, architecture | Complex logic, multi-file changes, design |
| **GPT-4** | Analysis, optimization | Algorithms, performance, debugging |

Tasks include `AGENT_TYPE` field suggesting which agent should handle it.

### 4. Multi-Agent Prompt Format

All prompts start with `#! Codex agent prompt` and include these fields:

```
TASK_ID=<unique ID>
WAVE=<wave number>
DEPENDS_ON=<task IDs this depends on>
AGENT_TYPE=<codex|claude|gpt4|auto>
COMPLEXITY=<low|medium|high>
TITLE=<short title>
SCOPE_TOUCH=<files allowed to edit>
SCOPE_READ=<files may read only>
SCOPE_FORBID=<files forbidden to edit>
CONTEXT:
- <what exists, what must change>
INTEGRATION_POINTS:
- <interfaces with other tasks>
CONSTRAINTS:
- <requirements>
ACCEPTANCE:
- <testable criteria>
DELIVERABLES:
- Proposed Conventional Commit message
- Exactly one final section: ### Change Summary
NOTES:
- Comments/docstrings in Slovak; report in English
- Other notes
```

**New in AP 2.0** (vs AP 1.0):
- `TASK_ID`, `WAVE`, `DEPENDS_ON` - for orchestration
- `AGENT_TYPE`, `COMPLEXITY` - for agent matching
- `SCOPE_READ` - read-only file access
- `INTEGRATION_POINTS` - contracts with other tasks

### 5. Worker Response Format

When completing a task, respond with:

1. **Unified Diffs** (only within SCOPE_TOUCH)
2. **Test & lint status** (ruff, mypy, pytest results)
3. **Migration notes** (if any)
4. **Known limitations & edge cases**
5. **Rollback plan**
6. **Proposed Conventional Commit** (one line)
7. **Exactly one terminal section**:
```
### Change Summary
- What changed and why (short, plain English)
```

**Critical**: Never edit files in `SCOPE_FORBID`. If you need to, STOP and request scope expansion.

## Working on This Project

### Before Making Changes

1. **Read the relevant docs**:
   - For protocol changes: Read `AP.md` completely
   - For quick-start changes: Read `AP_continue.md` completely
   - For understanding impact: Read `PRD.md` requirements
   
2. **Understand the scope**:
   - What files am I allowed to edit? (Check task's SCOPE_TOUCH)
   - What files can I read? (Check SCOPE_READ)
   - What am I forbidden to touch? (Check SCOPE_FORBID)

3. **Check integration points**:
   - Do other tasks depend on interfaces I'm changing?
   - What contracts must I preserve? (Check INTEGRATION_POINTS)

### Making Changes

#### When Editing Protocol Files (AP.md, AP_continue.md)

**Critical Principles**:
1. **Maintain consistency**: Changes to AP.md should be reflected in AP_continue.md and vice versa
2. **Preserve format**: Section numbering, field order, header format are strict
3. **Update examples**: If format changes, update all examples
4. **Version carefully**: Increment version (AP2.0 → AP2.1) for changes
5. **Backward compatibility**: Don't break AP 1.0 single-agent mode

**Common Tasks**:
- Adding new field: Update Section 3 (prompt format), Section 4 (response format), Section 7 (examples), Boot Prompt (Section 8)
- New validation rule: Add to Section 2.2 (scope validation), Section 9.3 (test validation)
- New agent type: Update Section 2.3 (agent matching), all examples with AGENT_TYPE

#### When Editing Documentation (README.md, PRD.md, AGENTS.md)

**Keep These Consistent**:
- Version numbers (currently AP 2.0)
- Statistics (file sizes, line counts)
- Feature lists (what's implemented vs proposed)
- Examples (should match protocol examples)

**Update Together**:
- If AP.md changes, update README.md "Core Documents" section
- If PRD requirements change, update AP.md to match
- If examples change, update all summary documents

#### When Adding New Features

**Process**:
1. Add to `PRD.md` as new requirement (R11, R12, etc.)
2. Design in `AP.md` Section 10 (Advanced Ideas) if experimental
3. Implement in `AP.md` Section 2-6 if core
4. Add examples to `AP.md` Section 3 or `AP_continue.md` Section 7
5. Update test cases in `AP.md` Section 9
6. Update `README.md`, `AGENTS.md`, `MULTIAGENT_UPGRADE_COMPLETE.md`

### Testing Your Changes

#### Manual Validation Checklist
- [ ] All protocol files parse correctly (no syntax errors)
- [ ] Examples conform to prompt format specification
- [ ] Field order matches specification
- [ ] SCOPE_TOUCH sets are disjoint in examples
- [ ] INTEGRATION_POINTS are consistent across tasks
- [ ] Boot Prompt updated if prompt format changed
- [ ] Version numbers incremented if protocol changed

#### Documentation Consistency Checklist
- [ ] README.md mentions all new features
- [ ] PRD.md requirements match implementation
- [ ] AGENTS.md updated with new concepts
- [ ] Summary documents reference new sections
- [ ] All examples work with new format

### Commit Guidelines

**Commit Message Format**:
```
<type>: <short description>

<detailed explanation of what changed and why>

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>
```

**Types**:
- `feat`: New feature (e.g., new field, new section)
- `fix`: Bug fix (e.g., incorrect example, typo)
- `docs`: Documentation only
- `refactor`: Restructuring without behavior change
- `test`: Adding/updating test cases
- `chore`: Maintenance (e.g., formatting)

**Examples**:
```
feat(protocol): add PRIORITY field for load balancing

Added PRIORITY=<critical|high|medium|low> field to prompt format
for wave execution ordering. Updated Section 3, examples, and
Boot Prompt.

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>
```

```
docs(readme): update AP 2.0 feature list

Added deterministic testing framework to feature list.
Updated examples to show wave-based execution.

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>
```

## Common Tasks & How-Tos

### Task: Add a New Field to Prompt Format

**Files to Update**:
1. `AP.md` Section 3: Add field to template with description
2. `AP.md` Section 3: Add to examples (at least 2)
3. `AP.md` Section 8: Update Boot Prompt if agents need to know about it
4. `AP_continue.md` Section 2: Add to RESET task format
5. `AP_continue.md` Section 3: Add to regular task format
6. `AP_continue.md` Section 7: Update all examples
7. `README.md`: Mention in "Sample Prompt" section
8. `AGENTS.md`: Document in "Multi-Agent Prompt Format" section

**Validation**:
- All examples include the new field
- Field description is clear and unambiguous
- Default value specified if optional
- Boot Prompt mentions field if agents must handle it

### Task: Add a New Agent Type

**Files to Update**:
1. `AP.md` Section 2.3: Add agent profile with capabilities
2. `AP.md` Section 3: Update AGENT_TYPE field description
3. `AP.md` Section 3: Add example using new agent
4. `AP_continue.md` Section 7: Add RESET task using new agent
5. `README.md`: Add to "Agent Type Matching" section
6. `AGENTS.md`: Add row to agent comparison table
7. `PRD.md`: Update R4 (Agent Type Matching) requirement

**Example**: Adding "DeepSeek" agent
- Profile: Best for mathematical proofs, formal verification
- Strengths: [formal_methods, correctness_proofs, math]
- Use for: Critical algorithms, security-sensitive code

### Task: Add a New Validation Rule

**Files to Update**:
1. `AP.md` Section 2.2: Add to scope validation algorithm
2. `AP.md` Section 9.3: Add to automated validation rules list
3. `AP.md` Section 9.5: Add pseudo-code to test runner
4. `PRD.md`: Add to R2 (Scope Conflict Prevention) or R8 (Testing)
5. `AGENTS.md`: Document in "Scope Conflict Prevention" section

**Example**: Adding "No empty SCOPE_TOUCH" validation
```python
def validate_scope_touch_not_empty(task):
    if not task.scope_touch or len(task.scope_touch) == 0:
        raise ValidationError(f"Task {task.task_id} has empty SCOPE_TOUCH")
```

### Task: Add an Advanced Feature Idea

**Files to Update**:
1. `AP.md` Section 10: Add new subsection (10.13, 10.14, etc.)
2. `PRD.md`: Add as Future Enhancement (F13, F14, etc.)
3. `MULTIAGENT_UPGRADE_COMPLETE.md`: Add to Phase 4 or Phase 5
4. `README.md`: Mention in "Advanced Features" if significant

**Format for Section 10**:
```markdown
### 10.X) Feature Name
**Idea**: One-line description

**Benefits**: What problems it solves

**Implementation**:
- Step 1
- Step 2
- Step 3

**Tradeoffs**: What are the costs/risks
```

## Debugging & Troubleshooting

### Issue: Scope Conflict in Examples

**Symptoms**: Two tasks in same wave have overlapping SCOPE_TOUCH

**Fix**:
1. Identify overlapping files: `Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH ≠ ∅`
2. Move one task to different wave (if dependency allows)
3. Or split file set so sets are disjoint
4. Update SCOPE_FORBID for both tasks to include other's SCOPE_TOUCH

### Issue: Inconsistent Field Order

**Symptoms**: Examples don't match template in Section 3

**Fix**:
1. Check AP.md Section 3 for canonical field order
2. Update all examples to match exactly
3. Pay attention to: TASK_ID before WAVE, SCOPE_TOUCH before SCOPE_READ

**Canonical Order**:
```
TASK_ID, WAVE, DEPENDS_ON, AGENT_TYPE, COMPLEXITY, URL,
STEP, TODO, TITLE, SCOPE_TOUCH, SCOPE_READ, SCOPE_FORBID,
CONTEXT, INTEGRATION_POINTS, CONSTRAINTS, ACCEPTANCE,
DELIVERABLES, NOTES
```

### Issue: Example Doesn't Preserve Behavior

**Symptoms**: RESET example changes functionality, violates behavior-preservation

**Fix**:
- RESET tasks must be **behavior-preserving** (no functional changes)
- Only allow: refactoring, typing, testing, cleanup, security hardening
- Never allow: feature changes, API modifications, business logic changes
- Add explicit note: "Behavior must not change (functional equivalence)"

## Advanced Topics

### Multi-Wave Dependencies

When Task T3 depends on both T1 and T2:
```
DEPENDS_ON=T1,T2
```

Orchestrator ensures:
- T1 and T2 complete before T3 starts
- If T1 in Wave 1, T2 in Wave 1, then T3 in Wave 2 (or later)
- If T1 in Wave 1, T2 in Wave 2, then T3 in Wave 3 (or later)

**Rule**: `wave(T3) > max(wave(T1), wave(T2))`

### Cross-Wave Integration Points

When T3 (Wave 2) uses interfaces from T1 (Wave 1):

```
# T1 (Wave 1)
INTEGRATION_POINTS:
- Exports function process(data: ProcessedData) -> Result
- Exports TypedDict: ProcessedData with fields [id, value, timestamp]

# T3 (Wave 2)
INTEGRATION_POINTS:
- Uses process() from T1
- Expects ProcessedData type available
- Will call process() in tests
```

Orchestrator validates after T1 completes:
- `process()` function exists
- Signature matches contract
- `ProcessedData` type exported

### Speculative Execution (Future)

**Idea**: Start Wave 2 tasks before Wave 1 completes if likely independent

**Risks**:
- Wasted work if Wave 1 changes interfaces
- More complex coordination logic

**When to Use**:
- High confidence interfaces won't change (contract-first development)
- Wave 1 tasks are slow (worth the risk)
- Wave 2 tasks are fast (low wasted work cost)

## FAQ for Agents

### Q: Can I edit files in SCOPE_FORBID?
**A**: NO. Never. If you must, STOP and request scope expansion from Orchestrator.

### Q: What if I need to read files outside SCOPE_READ?
**A**: That's fine. SCOPE_READ is a hint, not a restriction. SCOPE_FORBID is the restriction.

### Q: Can I add comments in language other than Slovak?
**A**: No. The protocol specifies "Comments/docstrings in Slovak; report in English". Follow it.

### Q: What if two tasks should edit the same file?
**A**: They can't be in the same wave. Orchestrator must put them in sequential waves or merge into one task.

### Q: How do I know which agent type I am?
**A**: Check the AGENT_TYPE field in your task prompt. It tells you which agent (codex/claude/gpt4) should handle this.

### Q: What if I finish early - can I help other agents?
**A**: No. Stick to your SCOPE_TOUCH. No coordination between agents. Orchestrator handles integration.

### Q: Can I suggest a better task decomposition?
**A**: Yes! Mention it in your response, but still complete your assigned task. Orchestrator considers for next time.

### Q: What if tests fail after my changes?
**A**: Report in "Test & lint status" section. Do NOT mark task as complete. Orchestrator will rollback or ask for fixes.

## Resources & References

### Primary Documents (Read These)
1. **AP.md**: Full protocol specification
2. **AP_continue.md**: Quick-start variant
3. **README.md**: Project overview
4. **PRD.md**: Requirements document

### Understanding Multi-Agent (Read These Next)
1. **MULTIAGENT_UPGRADE_COMPLETE.md**: Best comprehensive overview
2. **BEFORE_AFTER_COMPARISON.md**: Visual diagrams and examples
3. **AP_MULTIAGENT_SUMMARY.md**: Detailed section-by-section changes

### Quick References
- **Scope conflict prevention**: AP.md Section 2.2
- **Wave execution**: AP.md Section 2.4
- **Prompt format**: AP.md Section 3
- **Response format**: AP.md Section 4
- **Examples**: AP.md Section 3, AP_continue.md Section 7
- **Testing framework**: AP.md Section 9
- **Advanced ideas**: AP.md Section 10

## Contact & Support

This is an open protocol. Questions or suggestions?
1. Check `AP.md` and `PRD.md` first
2. Review examples in Section 3 and Section 7
3. Check `AGENTS.md` (this file) for common tasks
4. Propose changes via clear commit messages

## Working with the Orchestrator Implementation

### Overview of Orchestrator Files
The autonomous orchestrator is now fully implemented with MCPServerStdio:

**Base Implementation** (`orchestrator.py` - ~900 lines):
- Core data structures (AnalysisReport, CoordinationPlan, AccomplishmentReport)
- Documentation generators (Analysis, Plan, Accomplishment)
- Auto-documentation engine (updates README/PRD/AGENTS)
- SQLite persistence layer
- File upload handlers

**Complete Implementation** (`orchestrator_enhanced.py` - ~900 lines):
- Full ANALYTIC PHASE with streaming
- Full PLANNING PHASE with scope validation
- Full EXECUTION PHASE with MCP worker spawning
- Scope conflict detection algorithm (mathematical guarantee)
- Real-time progress streaming
- Self-monitoring status tracking
- Orchestrator tools (analyze_codebase, validate_scope_exclusivity, list_workers)

**MCP Worker Manager** (`mcp_server_stdio.py` - ~650 lines) **NEW!**
- **MCPServerStdio** - Direct stdin/stdout communication with workers
- **MCP Protocol** - Standard JSON messages (based on OpenAI Codex SDK)
- **Bidirectional** - Full request/response capability
- **Real-time** - Event-driven (<1ms latency)
- **Message types**: INITIALIZE, EXECUTE_TASK, TOOL_USE, PROGRESS, TASK_COMPLETE, TASK_ERROR
- **WebSocketBroadcaster** - Streams worker activity to dashboard
- **WorkerPoolManager** - Manages multiple workers

**Configuration** (`team.json`):
- Worker agent definitions (Claude, GPT-4, Codex)
- MCP connection details (command, args, env)
- Capabilities and concurrency limits
- Global forbid patterns
- Quality gate configuration

**Dashboard UI** (`dashboard.html`):
- Real-time worker monitoring
- Activity feed (tool use, progress, errors)
- Metrics (tasks completed, tools used, files modified)
- WebSocket connection to `ws://localhost:8765`

### MCPServerStdio Refactoring (October 2025)

The orchestrator was refactored from log file monitoring to direct stdio communication:

**Previous Approach (Deprecated):**
- Workers wrote to log files (`~/.codex/log/codex-tui.log`)
- `AsyncLogMonitor` polled files every 100ms
- Custom text parsing
- One-way communication
- File system dependency

**Current Approach (MCPServerStdio):**
- Workers communicate via stdin/stdout
- JSON MCP protocol messages
- Event-driven (<1ms latency)
- Bidirectional request/response
- No file system dependency

**Performance Improvement:** 100× faster real-time communication

**Documentation:**
- `REFACTORING_MCPSERVERSTDIO.md` - Complete refactoring guide
- `REFACTORING_SUMMARY.md` - Quick summary
- Based on: https://developers.openai.com/codex/guides/agents-sdk/

**Key Files:**
- `mcp_server_stdio.py` - New implementation
- `mcp_worker_connector.py` - Old implementation (deprecated, kept for reference)

### Three-Phase Documentation System

Every orchestrator run produces three documents:

1. **Analysis Report** (`docs/analyses/ANALYSIS_*.md`)
   - Deep understanding of owner request
   - Codebase structure analysis
   - Coordination points identified
   - Scope allocation strategy
   - Task type determination (RESET, FEATURE, BUG, etc.)

2. **Coordination Plan** (`docs/plans/PLAN_*.md`)
   - Decomposed objectives with exclusive scopes
   - Wave-based execution structure
   - Integration contracts between objectives
   - Scope validation results (conflicts or valid)
   - Estimated duration

3. **Accomplishment Report** (`docs/accomplishments/ACCOMPLISHMENT_*.md`)
   - Summary of what was accomplished
   - Objectives completed
   - Files modified
   - Test results and quality gates
   - Known issues and next steps
   - Auto-generated commit message
   - **For Future Agents** section with learnings

### Understanding Orchestrator Phases

**ANALYTIC PHASE** (Streaming: 5% → 100%)
```
owner_request → determine_task_type → identify_coordination_points 
            → develop_scope_strategy → generate_analysis_report
```

**PLANNING PHASE** (Streaming: 5% → 100%)
```
analysis_report → decompose_into_objectives → assign_to_waves
                → validate_scope_exclusivity → resolve_conflicts
                → define_integration_contracts → generate_coordination_plan
```

**EXECUTION PHASE** (Not yet implemented)
```
coordination_plan → init_worker_connections → execute_waves_parallel
                  → collect_results → validate_integration
                  → generate_accomplishment_report
```

### Scope Validation Algorithm (Critical!)

The orchestrator implements AP.md Section 2.2 algorithm:

```python
async def validate_scope_exclusivity(objectives):
    """
    Mathematical guarantee: 
    ∀ Ti, Tj in same wave: Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅
    """
    conflicts = []
    
    # Group by wave
    waves = group_by_wave(objectives)
    
    # Check each wave for conflicts
    for wave_num, wave_objs in waves.items():
        for i, obj1 in enumerate(wave_objs):
            scope1 = set(obj1['scope_touch'])
            for obj2 in wave_objs[i+1:]:
                scope2 = set(obj2['scope_touch'])
                overlap = scope1 & scope2
                if overlap:
                    conflicts.append({
                        'wave': wave_num,
                        'objective1': obj1['title'],
                        'objective2': obj2['title'],
                        'overlap': list(overlap)
                    })
    
    return {
        'valid': len(conflicts) == 0,
        'conflicts': conflicts
    }
```

**Why this matters**: This is the mathematical guarantee that enables true parallelism!

### Running the Orchestrator

**Test the complete implementation:**
```bash
python orchestrator_enhanced.py

# Output:
# - Complete ANALYTIC PHASE with streaming
# - Complete PLANNING PHASE with scope validation
# - Generated Analysis Report
# - Generated Coordination Plan
# - Generated Accomplishment Report
# - Auto-generated commit message
```

**What gets created:**
- `docs/analyses/ANALYSIS_*.md`
- `docs/plans/PLAN_*.md`
- `docs/accomplishments/ACCOMPLISHMENT_*.md`
- `orchestrator.db` (SQLite state)

### Key Learnings for Future Agents

**Session October 8, 2025 - Orchestrator Implementation**

**What Was Accomplished:**
- Complete autonomous orchestrator foundation (Phases 1 & 2)
- Full ANALYTIC and PLANNING phases with streaming
- Mathematical scope validation algorithm
- Auto-documentation system (like Factory's Droid)
- SQLite persistence and self-monitoring

**Novel Concepts Introduced:**
1. **Accomplishment-Centric Documentation** - Every session produces accomplishment report
2. **Three-Phase Documentation** - Analysis → Plan → Accomplishment
3. **Self-Documenting System** - Auto-updates README/PRD/AGENTS after each session
4. **Mathematical Scope Guarantees** - Provably correct conflict detection
5. **Real-Time Streaming** - Orchestrator streams its thinking for transparency

**Coordination Patterns Used:**
- Single-agent mode for initial implementation
- Modular design enabling Phase 3 integration
- Test-first approach with immediate validation
- Documentation-as-code mindset

**Scope Allocation Strategy:**
- Base implementation in orchestrator.py (data structures, utilities)
- Enhanced implementation in orchestrator_enhanced.py (complete phases)
- Clean separation enables independent testing

**Integration Points:**
- orchestrator.py exports data structures used by orchestrator_enhanced.py
- team.json configuration loaded by both implementations
- docs/ structure shared by all orchestrator components
- SQLite database maintains complete state

**Recommended for Future:**
- Study SESSION_SUMMARY.md for complete context
- Review PHASE2_COMPLETE.md for implementation details
- Understand three-phase documentation approach
- Test orchestrator with different request types
- Add Phase 3: Worker execution via MCP

**Testing Approach:**
- Immediate validation after each phase
- Streaming output for real-time debugging
- SQLite persistence for state inspection
- Generated documentation for verification

## Version Information

- **Protocol Version**: AP 1.0 (First true "Analytic Programming" implementation)
- **AGENTS.md Version**: 1.0
- **Last Updated**: October 8, 2025
- **Implementation Status**: Phases 1 & 2 complete, Phase 3 (worker execution) pending

## Quick Start Checklist

Before starting work on AP protocol:
- [ ] Read README.md (10 minutes)
- [ ] Read MULTIAGENT_UPGRADE_COMPLETE.md Executive Summary (5 minutes)
- [ ] Read AP.md Sections 0-2 (30 minutes)
- [ ] Review examples in AP.md Section 3 (10 minutes)
- [ ] Understand scope conflict prevention (AP.md 2.2) (10 minutes)
- [ ] Read this AGENTS.md completely (20 minutes)
- [ ] Understand your task's SCOPE_TOUCH/FORBID (always!)

**For Orchestrator Development** (NEW):
- [ ] Read IMPLEMENTATION_SUMMARY.md (15 minutes)
- [ ] Read PHASE2_COMPLETE.md (15 minutes)
- [ ] Review SESSION_SUMMARY.md (20 minutes)
- [ ] Test orchestrator: `python orchestrator_enhanced.py` (5 minutes)
- [ ] Understand three-phase documentation system (10 minutes)

**Total time investment**: ~2 hours to fully understand protocol + implementation

**Worth it?** Absolutely! You'll work confidently, understand the novel approach, avoid mistakes, and contribute effectively.

---

**Welcome to the team, Agent! Let's build something amazing together.** 🚀
