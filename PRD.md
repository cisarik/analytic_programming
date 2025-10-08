# Product Requirements Document: Analytic Programming Protocol

## Project Overview
**Product Name**: Analytic Programming (AP) Protocol
**Version**: 1.0
**Status**: Production Ready
**Last Updated**: October 2025

## Vision
Enable deterministic, transparent, and scalable collaboration between human owners and multiple AI coding agents through wave-based parallel execution with mathematically guaranteed conflict-free scope management.

## Problem Statement
Traditional AI coding workflows face:
1. **Sequential bottlenecks**: Large refactors take 45+ minutes
2. **No parallelization**: Cannot leverage multiple AI agents simultaneously
3. **Scope conflicts**: Risk of multiple agents editing same files
4. **No specialization**: Single agent handles all tasks regardless of complexity
5. **Opaque orchestration**: No clear decomposition or dependency management
6. **Lack of true analysis**: Previous approaches jumped to task planning without deep analytical understanding

## Solution
Analytic Programming provides a protocol for multi-agent orchestration enabling:
- **3-5× faster execution** via parallel wave-based task execution
- **Zero scope conflicts** through exclusive scope allocation algorithm
- **Agent specialization** by matching tasks to best-suited agent types
- **Transparent workflow** with explicit dependency graphs and integration points
- **Deterministic validation** through automated testing framework

## Core Requirements

### R1: Multi-Agent Orchestration (CRITICAL)
**Priority**: P0
**Status**: ✅ Implemented

The system MUST support orchestration of multiple AI agents working in parallel:
- **R1.1**: Decompose objectives into atomic tasks with exclusive scopes
- **R1.2**: Build dependency graphs and assign tasks to execution waves
- **R1.3**: Match tasks to appropriate agent types (Codex, Claude, GPT-4)
- **R1.4**: Coordinate wave execution (parallel within wave, sequential across waves)
- **R1.5**: Merge diffs and validate integration after each wave

**Acceptance Criteria**:
- Can decompose request into 3-10 parallel tasks
- SCOPE_TOUCH sets are disjoint within each wave
- Dependency graph correctly orders waves
- Agent type assignment matches task characteristics
- Integration validates all INTEGRATION_POINTS

### R2: Scope Conflict Prevention (CRITICAL)
**Priority**: P0
**Status**: ✅ Implemented

The system MUST mathematically guarantee zero edit conflicts:
- **R2.1**: Allocate exclusive SCOPE_TOUCH to each task in a wave
- **R2.2**: Validate that ∀ Ti, Tj in same wave: Ti.SCOPE_TOUCH ∩ Tj.SCOPE_TOUCH = ∅
- **R2.3**: Compute SCOPE_FORBID = GLOBAL_FORBID ∪ (⋃ other tasks' SCOPE_TOUCH)
- **R2.4**: Allow SCOPE_READ for read-only file access
- **R2.5**: Abort execution if scope violation detected

**Acceptance Criteria**:
- Scope validation algorithm detects all conflicts
- No two agents can edit same file in same wave
- GLOBAL_FORBID respected by all tasks
- SCOPE_READ allows safe read-only access

### R3: Wave-Based Execution (CRITICAL)
**Priority**: P0
**Status**: ✅ Implemented

The system MUST support wave-based execution model:
- **R3.1**: Group independent tasks into Wave 1
- **R3.2**: Group tasks depending only on Wave 1 into Wave 2
- **R3.3**: Recursively assign waves based on dependency graph
- **R3.4**: Execute all tasks in Wave N in parallel
- **R3.5**: Proceed to Wave N+1 only after Wave N validates

**Acceptance Criteria**:
- Wave assignment respects dependency order
- All tasks in wave can execute in parallel
- Integration validates before next wave starts
- Failed wave triggers rollback and adjustment

### R4: Agent Type Matching (HIGH)
**Priority**: P1
**Status**: ✅ Implemented

The system MUST match tasks to appropriate agent types:
- **R4.1**: Define agent capabilities (strengths, speed, context window)
- **R4.2**: Analyze task characteristics (complexity, file types, nature)
- **R4.3**: Assign AGENT_TYPE based on matching algorithm
- **R4.4**: Support auto mode for automatic agent selection

**Agent Profiles**:
- **Codex**: Fast, good for refactoring, type hints, unit tests
- **Claude**: Best for architecture, complex logic, multi-file changes
- **GPT-4**: Excellent for algorithms, performance, debugging

**Acceptance Criteria**:
- Complex architecture tasks → Claude
- Simple refactoring/tests → Codex
- Performance optimization → GPT-4
- Auto mode selects appropriate agent

### R5: Enhanced Prompt Format (CRITICAL)
**Priority**: P0
**Status**: ✅ Implemented

The system MUST support multi-agent prompt format:
- **R5.1**: All prompts start with `#! Codex agent prompt` header
- **R5.2**: Include TASK_ID, WAVE, DEPENDS_ON fields
- **R5.3**: Include AGENT_TYPE, COMPLEXITY fields
- **R5.4**: Include SCOPE_TOUCH, SCOPE_READ, SCOPE_FORBID fields
- **R5.5**: Include INTEGRATION_POINTS for dependent tasks
- **R5.6**: All other AP 1.0 fields (TITLE, CONTEXT, CONSTRAINTS, ACCEPTANCE, DELIVERABLES, NOTES)

**Acceptance Criteria**:
- All prompts conform to format specification
- Required fields are validated
- SCOPE_TOUCH is exclusive within wave
- INTEGRATION_POINTS specify contracts

### R6: Integration & Merge Strategy (HIGH)
**Priority**: P1
**Status**: ✅ Implemented

The system MUST safely integrate parallel task results:
- **R6.1**: Merge diffs in dependency order
- **R6.2**: Detect unexpected conflicts (should be impossible)
- **R6.3**: Validate INTEGRATION_POINTS contracts
- **R6.4**: Run quality gates (lint, type, test) on integrated result
- **R6.5**: Rollback entire wave if integration fails

**Acceptance Criteria**:
- Dependency-ordered merge succeeds
- Interface contracts validated
- Quality gates pass on integrated result
- Rollback leaves system in clean state

### R7: Failure Handling & Recovery (HIGH)
**Priority**: P1
**Status**: ✅ Implemented

The system MUST handle task failures gracefully:
- **R7.1**: Detect task failures and scope violations
- **R7.2**: Identify dependent tasks that must be blocked
- **R7.3**: Support granular rollback (only failed dependency chain)
- **R7.4**: Allow retry with adjusted scope or different agent
- **R7.5**: Escalate to Owner when automated recovery fails

**Recovery Options**:
- Re-assign to different agent

### R10: Autonomous Orchestrator Implementation (CRITICAL - NEW)
**Priority**: P0
**Status**: ✅ Implemented (Phases 1 & 2 Complete)

The system MUST provide a working autonomous orchestrator:
- **R10.1**: Complete ANALYTIC PHASE implementation with streaming
- **R10.2**: Complete PLANNING PHASE implementation with scope validation
- **R10.3**: Scope conflict detection algorithm (mathematical guarantee)
- **R10.4**: Real-time progress streaming for UI integration
- **R10.5**: Self-monitoring and status tracking
- **R10.6**: SQLite persistence for state and history
- **R10.7**: Auto-documentation system (Analysis, Plan, Accomplishment reports)
- **R10.8**: Automatic commit message generation
- **R10.9**: Learning system for future agents (updates AGENTS.md)

**Implementation Details**:
- **orchestrator.py** (~900 lines): Base implementation with data structures
- **orchestrator_enhanced.py** (~800 lines): Complete ANALYTIC/PLANNING phases
- **team.json**: Worker configuration
- **docs/** structure: Auto-generated documentation

**Three-Phase Documentation**:
1. **Analysis Report** - Deep understanding of owner request
2. **Coordination Plan** - Scope allocation and wave structure
3. **Accomplishment Report** - What was accomplished (with learnings)

**Acceptance Criteria**:
- Orchestrator autonomously decomposes requests into tasks
- Scope validation detects all conflicts (0 false negatives)
- Real-time streaming works end-to-end
- Documentation auto-generated for each phase
- Commit messages include accomplishment summary
- SQLite tracks complete session history

**Test Results**: ✅ All phases tested and working

### R8: Deterministic Testing Framework (HIGH)
**Priority**: P1
**Status**: ✅ Implemented

The system MUST support automated validation:
- **R8.1**: YAML/JSON test case format with input/expected output
- **R8.2**: 6 automated validation rules
  1. Scope exclusivity
  2. Dependency consistency
  3. Scope coverage
  4. FORBID correctness
  5. Prompt format
  6. Integration points
- **R8.3**: Test categories: MA-BASIC, MA-SEQUENTIAL, MA-COMPLEX, MA-CONFLICT, MA-AGENT-MATCH, MA-FAILURE
- **R8.4**: Regression suite with 10+ test cases
- **R8.5**: Continuous validation before protocol changes

**Acceptance Criteria**:
- Test runner validates all rules
- All test categories covered
- 100% pass rate on regression suite
- New orchestration bugs captured as test cases

### R9: Multi-Agent RESET (HIGH)
**Priority**: P1
**Status**: ✅ Implemented

The system MUST support multi-agent baseline refactoring:
- **R9.1**: Decompose RESET into 3-5 parallel tasks
- **R9.2**: Each RESET task has exclusive scope (src/core/, tests/, config/, etc.)
- **R9.3**: All RESET tasks preserve behavior (no functional changes)
- **R9.4**: Execute all RESET tasks in Wave 1 (parallel)
- **R9.5**: Merge and validate before proceeding to feature tasks

**Typical RESET Tasks**:
- Core module typing and refactoring
- Test suite hardening and determinism
- Logging security and configuration
- UI cleanup and consistency

**Acceptance Criteria**:
- RESET completes in 1/3 the time (vs sequential)
- All quality gates pass
- Behavior preserved (tests pass)
- Clean baseline for feature work

## Advanced Features (Future Enhancements)

### F1: Load Balancing & Task Distribution
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.1)

Add ESTIMATED_DURATION and PRIORITY fields to balance agent workload and execution order.

### F2: Progress Tracking & Real-time Status
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.2)

Agents emit progress events during execution for visibility and stuck detection.

### F3: Partial Rollback & Granular Recovery
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.3)

Roll back only failed dependency chain, keep independent successful work.

### F4: Adaptive Re-planning
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.4)

Orchestrator adjusts plan after each wave based on actual complexity vs estimated.

### F5: Agent Capability Learning
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.5)

Track agent performance metrics to improve future task assignments.

### F6: Cross-Wave Optimization
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.6)

Reorder tasks to maximize parallelism (e.g., split Task 4 into prep + final).

### F7: Dry-Run & Validation Mode
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.7)

Execute orchestration logic without sending to agents; output plan for review.

### F8: ML-Based Conflict Prediction
**Priority**: P3
**Status**: ⏳ Proposed (AP.md Section 10.8)

Predict merge conflicts before execution using semantic similarity and coupling metrics.

### F9: Dynamic Scope Adjustment Protocol
**Priority**: P3
**Status**: ⏳ Proposed (AP.md Section 10.9)

Allow agents to request scope expansion mid-task when needed.

### F10: Quality & Performance Metrics
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.10)

Track session metrics, agent performance, optimization suggestions over time.

### F11: Contract-First Development
**Priority**: P2
**Status**: ⏳ Proposed (AP.md Section 10.11)

Wave 0 defines all interfaces before Wave 1+ implements against frozen contracts.

### F12: Speculative Execution
**Priority**: P3
**Status**: ⏳ Proposed (AP.md Section 10.12)

Start Wave N+1 tasks speculatively before Wave N completes (tradeoff analysis).

## Success Metrics

### Performance Metrics
- **Execution Time**: 3-5× faster for parallel tasks vs sequential
- **Conflict Rate**: 0% (mathematical guarantee)
- **Integration Success**: >95% on first try
- **Agent Utilization**: >80% parallel capacity utilized

### Quality Metrics
- **Test Coverage**: 100% of orchestration logic
- **Regression Pass Rate**: 100% on deterministic test suite
- **Scope Violations**: 0 (validation catches all)
- **Failed Rollbacks**: <1% (clean rollback guaranteed)

### Adoption Metrics
- **Documentation Completeness**: 100% (all sections complete)
- **Example Coverage**: 10+ realistic examples
- **Migration Guide**: Clear AP 1.0 → AP 2.0 path
- **Agent Support**: 3+ agent types (Codex, Claude, GPT-4)

## Non-Functional Requirements

### NFR1: Determinism
All orchestration decisions must be deterministic and reproducible given same input.

### NFR2: Transparency
All task decomposition, scope allocation, and wave assignments must be reviewable by Owner.

### NFR3: Safety
Scope conflict prevention algorithm must be mathematically provable (no edit conflicts possible).

### NFR4: Scalability
Must support 10+ parallel tasks and 5+ execution waves without degradation.

### NFR5: Documentation
All protocol specifications, examples, and guides must be comprehensive and up-to-date.

## Constraints

### C1: Agent Availability
Assumes access to multiple AI coding agents (Codex, Claude, GPT-4 via APIs or chat interfaces).

### C2: Codebase Structure
Works best with modular codebases where independent areas exist (src/core/, tests/, ui/, etc.).

### C3: Owner Involvement
Requires Owner to review and approve multi-agent task plans before execution.

### C4: Merge Capability
Assumes ability to merge multiple diffs and run quality gates on integrated result.

## Dependencies

### D1: AI Agent APIs
- Codex API (OpenAI)
- Claude API (Anthropic)
- GPT-4 API (OpenAI)

### D2: Quality Gate Tools
- Linters (ruff, eslint, etc.)
- Type checkers (mypy, tsc, etc.)
- Test runners (pytest, jest, etc.)

### D3: Version Control
- Git for tracking changes
- Diff/merge tools

## Risks & Mitigations

### Risk 1: Unexpected Scope Conflicts
**Severity**: Low (P3)
**Mitigation**: Mathematical validation algorithm catches all conflicts before execution

### Risk 2: Agent Performance Variance
**Severity**: Medium (P2)
**Mitigation**: Track metrics, adjust agent assignments; retry with different agent

### Risk 3: Complex Dependency Graphs
**Severity**: Medium (P2)
**Mitigation**: Limit to 5 waves; escalate to Owner if too complex; simplify decomposition

### Risk 4: Integration Failures
**Severity**: Medium (P2)
**Mitigation**: Atomic wave rollback; quality gates catch issues; clear INTEGRATION_POINTS

### Risk 5: Adoption Barrier
**Severity**: Medium (P2)
**Mitigation**: Backward compatibility with AP 1.0; gradual migration; comprehensive examples

## Release Plan

### Phase 1: Core Multi-Agent (✅ COMPLETE)
- Multi-agent orchestration (AP.md Section 2)
- Wave-based execution
- Scope conflict prevention
- Enhanced prompt format
- Multi-agent RESET

### Phase 2: Testing & Documentation (✅ COMPLETE)
- Deterministic testing framework (AP.md Section 9)
- Comprehensive documentation (README, AGENTS, summaries)
- 10+ examples in AP.md and AP_continue.md
- Before/after comparison guide

### Phase 3: Implementation (⏳ PENDING)
- Build orchestrator (Python/TypeScript)
- Implement test runner
- Create 10-20 test cases
- Pilot on real codebases

### Phase 4: Advanced Features (⏳ PENDING)
- Implement 3-4 features from Section 10
- Agent capability learning
- Quality metrics tracking
- Adaptive re-planning

## Stakeholders

### Primary Stakeholders
- **Owner**: Approves task plans, reviews results
- **Orchestrator**: Decomposes and coordinates (currently ChatGPT)
- **Workers**: Execute tasks (Codex, Claude, GPT-4)

### Secondary Stakeholders
- **Future Agent Developers**: Build orchestrator implementation
- **Protocol Contributors**: Propose enhancements
- **Adopters**: Use AP protocol in their projects

## Version History

### AP 1.0 (Initial Release)
- Single-agent sequential execution
- Basic scope management
- Worker response format
- Quality gates

### AP 2.0 (Multi-Agent Edition) - October 2024
- Multi-agent orchestration (+95 lines)
- Wave-based execution
- Scope conflict prevention algorithm
- Agent type matching
- Enhanced prompt format (+7 fields)
- Deterministic testing framework (+88 lines)
- Advanced prompt engineering ideas (+170 lines)
- Multi-agent RESET
- 660 lines total (+96% from AP 1.0)

## References

### Core Documents
- `AP.md`: Full protocol specification
- `AP_continue.md`: Quick-start variant
- `README.md`: Project overview
- `AGENTS.md`: Agent guidelines (this document)

### Summary Documents
- `MULTIAGENT_UPGRADE_COMPLETE.md`: Comprehensive upgrade overview
- `BEFORE_AFTER_COMPARISON.md`: Visual comparison
- `AP_MULTIAGENT_SUMMARY.md`: Detailed AP.md changes
- `AP_CONTINUE_MULTIAGENT_SUMMARY.md`: Detailed AP_continue.md changes
