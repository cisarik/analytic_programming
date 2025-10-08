# AP 2.0: Multi-Agent Edition - Summary of Changes

## Overview
Transformed AP from single-agent (Codex only) to multi-agent orchestration supporting parallel execution across multiple coding agents (Codex, Claude, GPT-4, etc.) with conflict-free scope management.

## Key Design Principles

### 1. Wave-Based Execution
- **Wave N**: All tasks execute in parallel (exclusive scopes guaranteed)
- **Sequential waves**: Wave N+1 starts only after Wave N completes
- **Dependency tracking**: Tasks explicitly declare dependencies via `DEPENDS_ON`

### 2. Exclusive Scope Allocation
**Algorithm**:
```
For each task T in wave W:
  T.SCOPE_TOUCH = {files T may edit}
  T.SCOPE_READ = {files T may read only}
  T.SCOPE_FORBID = GLOBAL_FORBID ∪ (⋃ other tasks' SCOPE_TOUCH in wave W)

Validation: T1.SCOPE_TOUCH ∩ T2.SCOPE_TOUCH = ∅ (no conflicts)
```

**Result**: Mathematically guaranteed no edit conflicts within a wave

### 3. Agent Type Matching
- Each agent declares capabilities (strengths, speed, context window)
- Orchestrator assigns tasks based on:
  - Task complexity
  - Required skills (refactoring, algorithms, architecture)
  - Agent availability and load

## Major Additions to AP.md

### Section 2: Multi-Agent Orchestration (NEW - 95 lines)
- **2.1** Task decomposition & dependency graph building
- **2.2** Scope conflict prevention algorithm (mathematical proof of exclusivity)
- **2.3** Agent types & capability matching system
- **2.4** Wave execution protocol (parallel within wave, sequential across waves)
- **2.5** Integration & merge strategy
- **2.6** Failure handling & recovery (granular rollback)

### Section 3: Enhanced Prompt Format
**New fields**:
- `TASK_ID`: Unique identifier for cross-referencing
- `WAVE`: Execution wave number
- `DEPENDS_ON`: Task IDs this depends on
- `AGENT_TYPE`: codex|claude|gpt4|auto
- `COMPLEXITY`: low|medium|high
- `SCOPE_READ`: Read-only file access
- `INTEGRATION_POINTS`: Contracts with other tasks

**Example**: 3 tasks (2 parallel in Wave 1, 1 integration in Wave 2) with detailed prompts

### Section 9: Deterministic Testing System (NEW - 88 lines)
Complete framework for testing orchestration logic:
- **Test structure**: YAML/JSON with input (codebase + request) and expected output (task graph)
- **Validation rules**: 6 automated checks (scope exclusivity, dependency consistency, etc.)
- **Test categories**: MA-BASIC, MA-SEQUENTIAL, MA-COMPLEX, MA-CONFLICT, MA-AGENT-MATCH, MA-FAILURE
- **Pseudo-code**: Test runner implementation
- **Regression suite**: Continuous validation of orchestration decisions

### Section 10: Advanced Prompt Engineering (NEW - 170 lines)
12 sophisticated ideas for future enhancements:

1. **Load balancing**: ESTIMATED_DURATION and PRIORITY fields
2. **Progress tracking**: Real-time agent status updates
3. **Partial rollback**: Minimal dependency-aware rollback (not full wave)
4. **Adaptive re-planning**: Adjust plan after each wave based on reality
5. **Agent capability learning**: Track metrics to improve future assignments
6. **Cross-wave optimization**: Reorder tasks for maximum parallelism
7. **Dry-run mode**: Validate plan without execution
8. **ML conflict prediction**: Predict merge conflicts using semantic similarity
9. **Dynamic scope adjustment**: Mid-task scope expansion protocol
10. **Quality metrics**: Track success rates, durations, optimization suggestions
11. **Contract-first development**: Wave 0 defines all interfaces (eliminates integration issues)
12. **Speculative execution**: Start Wave N+1 tasks before Wave N completes (tradeoff: wasted work vs latency)

### Section 11: Multi-Agent Lifecycle (Updated)
7-step workflow:
1. Owner states objective
2. Orchestrator decomposes → task graph, scopes, waves
3. Owner reviews plan
4. Wave execution (parallel)
5. Integration & validation (quality gates)
6. Owner review
7. Iterate until complete

### Section 8: Updated Boot Prompt
Workers now understand:
- Multi-agent awareness (other agents working in parallel)
- Exclusive scope guarantee
- Integration points with other tasks
- When to request scope expansion

## Version
- **AP 2.0 (Multi-Agent Edition)**
- Backward compatible with AP 1.0 (single-agent mode for simple tasks)

## Benefits

### Performance
- **Parallelism**: N agents work simultaneously (N× speedup for independent tasks)
- **Load distribution**: Work spread across multiple agents
- **Optimized wave structure**: Minimal sequential dependencies

### Safety
- **Zero conflicts**: Mathematical guarantee via exclusive scopes
- **Atomic waves**: All-or-nothing execution per wave
- **Granular rollback**: Only failed dependency chains, not entire wave
- **Contract enforcement**: INTEGRATION_POINTS verify interfaces

### Scalability
- **Horizontal scaling**: Add more agents → more parallel capacity
- **Agent specialization**: Match task to best-suited agent
- **Large codebases**: Decompose into 10+ parallel tasks

### Quality
- **Deterministic testing**: Validate orchestration logic
- **Metrics tracking**: Learn from performance data
- **Continuous improvement**: Adaptive re-planning, capability learning

## Implementation Path

### Phase 1: Core Multi-Agent (MVP)
- Implement sections 2.1-2.4 (decomposition, scopes, waves, execution)
- Basic agent registry (codex, claude, gpt4)
- Simple wave-based execution
- Scope conflict validator

### Phase 2: Testing & Validation
- Implement section 9 (deterministic testing)
- Create initial test suite (10-20 test cases)
- Validate on real codebases

### Phase 3: Advanced Features
- Implement 2-3 ideas from section 10 (e.g., dry-run mode, progress tracking, partial rollback)
- Agent capability learning
- Quality metrics

### Phase 4: Optimization
- Adaptive re-planning
- Cross-wave optimization
- Speculative execution (if metrics support it)

## Files Modified
- **AP.md**: 337 → 660 lines (+323 lines, 96% growth)
  - Comprehensive multi-agent orchestration system
  - Deterministic testing framework
  - 12 advanced prompt engineering ideas

## Next Steps (Recommendations)

1. **Update AP_continue.md**: Align RESET prompt with multi-agent format
2. **Create test suite**: Implement 5-10 test cases from section 9.4
3. **Build orchestrator**: Python/TypeScript implementation of decomposition algorithm
4. **Agent registry**: Define capability profiles for codex, claude, gpt4
5. **Pilot project**: Test on real codebase with 3-5 parallel tasks
6. **Metrics dashboard**: Track orchestration quality over time

## Questions for Owner

1. **Priority**: Which advanced features (section 10) are most valuable?
2. **Agents**: Which agent types do you want to support initially? (codex, claude, gpt4, others?)
3. **Testing**: Should I implement the test framework (section 9) in Python?
4. **AP_continue.md**: Should I update it for multi-agent RESET prompts?
5. **Integration**: How will orchestrator send tasks to multiple agents? (APIs, chat interfaces, CLI?)
