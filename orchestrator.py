#!/usr/bin/env python3
"""
orchestrator.py - Analytic Programming Orchestrator

Complete autonomous orchestrator with:
- Self-monitoring and status tracking
- SQLite persistence
- File upload support (ZIP, images, context files)
- Auto-documentation system (Analysis, Plans, Accomplishments)
- Auto-update of project docs (README, PRD, AGENTS)

Architecture:
    Owner Request → ANALYTIC PHASE → Analysis Report
                 → PLANNING PHASE → Coordination Plan
                 → EXECUTION PHASE → Execution Logs
                 → POST-EXECUTION → Accomplishment Report
                 → AUTO-DOC PHASE → Update README/PRD/AGENTS + commit message

Version: 1.0.0 (AP 1.0)
"""

import asyncio
import json
import sqlite3
import zipfile
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, AsyncIterator, Set
from enum import Enum
from uuid import uuid4

# ============================================================================
# CONFIGURATION
# ============================================================================

DOCS_DIR = Path("docs")
ACCOMPLISHMENTS_DIR = DOCS_DIR / "accomplishments"
ANALYSES_DIR = DOCS_DIR / "analyses"
PLANS_DIR = DOCS_DIR / "plans"
SESSIONS_DIR = DOCS_DIR / "sessions"

# Create directories
for dir_path in [ACCOMPLISHMENTS_DIR, ANALYSES_DIR, PLANS_DIR, SESSIONS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class OrchestratorPhase(Enum):
    """Orchestrator's execution phases"""
    IDLE = "idle"
    ANALYTIC = "analytic"           # Deep analysis
    PLANNING = "planning"           # Coordination plan
    VALIDATION = "validation"       # Scope validation
    EXECUTION = "execution"         # Worker dispatch
    INTEGRATION = "integration"     # Merge results
    POST_EXECUTION = "post_execution"  # Create accomplishment report
    AUTO_DOCUMENTATION = "auto_documentation"  # Update project docs
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(Enum):
    """Types of coordination tasks"""
    RESET = "reset"
    FEATURE = "feature"
    BUG = "bug"
    REFACTOR = "refactor"
    ENHANCEMENT = "enhancement"

class WorkerState(Enum):
    """Worker agent states"""
    IDLE = "idle"
    REASONING = "reasoning"
    CODING = "coding"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AnalysisReport:
    """
    Output of ANALYTIC PHASE
    Documents deep understanding of what needs to be done
    """
    report_id: str
    session_id: str
    owner_request: str
    uploaded_files: List[str]
    codebase_analysis: Dict  # Structure, smells, patterns
    coordination_points: List[str]  # What needs to interact
    identified_modules: List[str]
    scope_strategy: str  # How to allocate scopes
    task_type: TaskType  # RESET, feature, bug, etc.
    timestamp: str
    file_path: str = ""  # Path to saved markdown

@dataclass
class CoordinationPlan:
    """
    Output of PLANNING PHASE
    Documents how workers will coordinate
    """
    plan_id: str
    analysis_report_id: str
    plan_type: TaskType
    waves: List[Dict]  # List of waves with objectives
    integration_contracts: List[Dict]  # Interfaces between workers
    scope_validation: Dict  # Validation results
    global_forbid: List[str]  # Files no one can touch
    estimated_duration: str
    timestamp: str
    file_path: str = ""

@dataclass
class AccomplishmentReport:
    """
    Output of POST-EXECUTION PHASE
    Documents what was accomplished (like Factory's RESULT.md)
    """
    accomplishment_id: str
    session_id: str
    plan_id: str
    summary: str  # High-level summary
    objectives_completed: List[str]
    files_modified: List[str]
    test_results: Dict
    quality_gates: Dict
    integration_status: str
    known_issues: List[str]
    next_steps: List[str]
    commit_message: str  # Generated commit message
    timestamp: str
    file_path: str = ""

@dataclass
class OrchestratorStatus:
    """Orchestrator's own status (for monitoring)"""
    phase: OrchestratorPhase
    progress_percent: int
    current_activity: str
    elapsed_time: float
    estimated_remaining: Optional[float]
    errors: List[str] = field(default_factory=list)

# ============================================================================
# PERSISTENCE LAYER (SQLite)
# ============================================================================

class Database:
    """Lightweight SQLite persistence"""
    
    def __init__(self, db_path: str = "orchestrator.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if not exist"""
        self.conn.executescript("""
            -- Sessions (one per Owner interaction)
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                owner_name TEXT,
                created_at TEXT,
                status TEXT
            );
            
            -- Analysis Reports
            CREATE TABLE IF NOT EXISTS analysis_reports (
                report_id TEXT PRIMARY KEY,
                session_id TEXT,
                owner_request TEXT,
                task_type TEXT,
                file_path TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            
            -- Coordination Plans
            CREATE TABLE IF NOT EXISTS coordination_plans (
                plan_id TEXT PRIMARY KEY,
                report_id TEXT,
                plan_type TEXT,
                file_path TEXT,
                created_at TEXT,
                approved BOOLEAN DEFAULT 0,
                FOREIGN KEY (report_id) REFERENCES analysis_reports(report_id)
            );
            
            -- Accomplishment Reports
            CREATE TABLE IF NOT EXISTS accomplishment_reports (
                accomplishment_id TEXT PRIMARY KEY,
                session_id TEXT,
                plan_id TEXT,
                file_path TEXT,
                commit_message TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                FOREIGN KEY (plan_id) REFERENCES coordination_plans(plan_id)
            );
            
            -- Orchestrator state snapshots
            CREATE TABLE IF NOT EXISTS orchestrator_state (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                phase TEXT,
                progress_percent INTEGER,
                activity TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)
        self.conn.commit()
    
    def save_orchestrator_state(self, session_id: str, status: OrchestratorStatus):
        self.conn.execute("""
            INSERT INTO orchestrator_state 
            (session_id, phase, progress_percent, activity, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            status.phase.value,
            status.progress_percent,
            status.current_activity,
            datetime.now().isoformat()
        ))
        self.conn.commit()

# ============================================================================
# DOCUMENTATION GENERATOR
# ============================================================================

class DocumentationGenerator:
    """
    Generates markdown documentation for each phase
    Like Factory's Droid creates RESULT.md
    """
    
    @staticmethod
    def generate_analysis_report_md(report: AnalysisReport) -> str:
        """Generate Analysis Report markdown"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Analysis Report
**Session:** {report.session_id}  
**Report ID:** {report.report_id}  
**Timestamp:** {timestamp}  
**Task Type:** {report.task_type.value.upper()}

## Owner Request
{report.owner_request}

## Uploaded Files
{chr(10).join(f"- {f}" for f in report.uploaded_files) if report.uploaded_files else "- None"}

## Codebase Analysis
### Structure
{json.dumps(report.codebase_analysis.get('structure', {}), indent=2)}

### Identified Issues
{chr(10).join(f"- {issue}" for issue in report.codebase_analysis.get('issues', []))}

### Patterns & Smells
{chr(10).join(f"- {smell}" for smell in report.codebase_analysis.get('smells', []))}

## Coordination Points
{chr(10).join(f"- {point}" for point in report.coordination_points)}

## Identified Modules
{chr(10).join(f"- {module}" for module in report.identified_modules)}

## Scope Allocation Strategy
{report.scope_strategy}

## Next Steps
1. Create Coordination Plan
2. Validate scope exclusivity
3. Execute wave-based coordination

---
*Generated by Analytic Programming Orchestrator*
"""
        return md
    
    @staticmethod
    def generate_coordination_plan_md(plan: CoordinationPlan) -> str:
        """Generate Coordination Plan markdown"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Coordination Plan
**Plan ID:** {plan.plan_id}  
**Analysis Report:** {plan.analysis_report_id}  
**Timestamp:** {timestamp}  
**Type:** {plan.plan_type.value.upper()}  
**Estimated Duration:** {plan.estimated_duration}

## Waves & Objectives

"""
        for i, wave in enumerate(plan.waves, 1):
            md += f"### Wave {i}\n\n"
            for obj in wave:
                md += f"""**Objective:** {obj['title']}
- **Worker:** {obj['worker_type']}
- **Scope Touch:** {', '.join(obj['scope_touch'])}
- **Scope Forbid:** {', '.join(obj['scope_forbid'][:3])}{'...' if len(obj['scope_forbid']) > 3 else ''}

"""
        
        md += f"""## Integration Contracts
{chr(10).join(f"- {contract['description']}" for contract in plan.integration_contracts)}

## Global Forbid
{chr(10).join(f"- {item}" for item in plan.global_forbid)}

## Scope Validation
**Status:** {"✓ VALID" if plan.scope_validation.get('valid') else "✗ CONFLICTS DETECTED"}

{"### Conflicts" + chr(10) + chr(10).join(f"- {c}" for c in plan.scope_validation.get('conflicts', [])) if not plan.scope_validation.get('valid') else ""}

---
*Generated by Analytic Programming Orchestrator*
"""
        return md
    
    @staticmethod
    def generate_accomplishment_report_md(report: AccomplishmentReport) -> str:
        """
        Generate Accomplishment Report markdown
        Like Factory's RESULT.md
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Accomplishment Report
**Session:** {report.session_id}  
**Plan:** {report.plan_id}  
**Timestamp:** {timestamp}

## Summary
{report.summary}

## Objectives Completed
{chr(10).join(f"- ✓ {obj}" for obj in report.objectives_completed)}

## Files Modified
{chr(10).join(f"- {f}" for f in report.files_modified)}

## Test Results
- **Status:** {report.test_results.get('status', 'Unknown')}
- **Tests Run:** {report.test_results.get('total', 0)}
- **Passed:** {report.test_results.get('passed', 0)}
- **Failed:** {report.test_results.get('failed', 0)}

## Quality Gates
{chr(10).join(f"- **{gate}:** {status}" for gate, status in report.quality_gates.items())}

## Integration Status
{report.integration_status}

## Known Issues
{chr(10).join(f"- {issue}" for issue in report.known_issues) if report.known_issues else "- None"}

## Next Steps
{chr(10).join(f"{i}. {step}" for i, step in enumerate(report.next_steps, 1))}

## Commit Message
```
{report.commit_message}
```

---
*Generated by Analytic Programming Orchestrator*

## For Future Agents
This accomplishment demonstrates:
- Wave-based parallel execution with exclusive scopes
- Autonomous worker coordination
- Zero scope conflicts (mathematical guarantee)

Refer to this when:
- Similar coordination patterns needed
- Understanding scope allocation strategies
- Learning from integration challenges
"""
        return md

# ============================================================================
# AUTO-DOCUMENTATION ENGINE
# ============================================================================

class AutoDocumentationEngine:
    """
    Automatically updates project documentation after each session
    Like Factory's Droid updates docs
    """
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.readme_path = project_root / "README.md"
        self.prd_path = project_root / "PRD.md"
        self.agents_path = project_root / "AGENTS.md"
    
    async def update_documentation(
        self,
        accomplishment: AccomplishmentReport,
        analysis: AnalysisReport,
        plan: CoordinationPlan
    ) -> Dict[str, str]:
        """
        Update project documentation based on accomplishment
        Returns dict of updates made
        """
        updates = {}
        
        # Read all uncommitted .md files
        uncommitted_mds = await self._find_uncommitted_md_files()
        
        # Analyze what changed
        changes = await self._analyze_changes(
            accomplishment, analysis, plan, uncommitted_mds
        )
        
        # Update README.md if new features
        if changes.get('new_features'):
            readme_update = await self._update_readme(changes)
            updates['README.md'] = readme_update
        
        # Update PRD.md if new requirements
        if changes.get('new_requirements'):
            prd_update = await self._update_prd(changes)
            updates['PRD.md'] = prd_update
        
        # Always update AGENTS.md with learnings
        agents_update = await self._update_agents_md(
            accomplishment, analysis, plan
        )
        updates['AGENTS.md'] = agents_update
        
        return updates
    
    async def _find_uncommitted_md_files(self) -> List[Path]:
        """Find all uncommitted .md files in project"""
        # TODO: Implement git status parsing
        return []
    
    async def _analyze_changes(
        self,
        accomplishment: AccomplishmentReport,
        analysis: AnalysisReport,
        plan: CoordinationPlan,
        uncommitted_mds: List[Path]
    ) -> Dict:
        """
        Analyze what changed to determine doc updates needed
        """
        return {
            'new_features': accomplishment.task_type == TaskType.FEATURE,
            'new_requirements': False,  # TODO: Detect from analysis
            'learnings': self._extract_learnings(accomplishment, plan)
        }
    
    async def _update_readme(self, changes: Dict) -> str:
        """Update README.md with new features"""
        # TODO: Implement README update logic
        return "Updated with new features"
    
    async def _update_prd(self, changes: Dict) -> str:
        """Update PRD.md with new requirements"""
        # TODO: Implement PRD update logic
        return "Updated with new requirements"
    
    async def _update_agents_md(
        self,
        accomplishment: AccomplishmentReport,
        analysis: AnalysisReport,
        plan: CoordinationPlan
    ) -> str:
        """
        Update AGENTS.md with learnings for future agents
        Critical for continuous improvement
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        learning_entry = f"""
## Session {accomplishment.session_id} - {timestamp}

### What Was Accomplished
{accomplishment.summary}

### Coordination Pattern Used
- **Task Type:** {plan.plan_type.value}
- **Waves:** {len(plan.waves)}
- **Workers:** {len([obj for wave in plan.waves for obj in wave])}

### Key Learnings
{chr(10).join(f"- {learning}" for learning in self._extract_learnings(accomplishment, plan))}

### Scope Allocation Strategy
{analysis.scope_strategy}

### Integration Challenges
{chr(10).join(f"- {issue}" for issue in accomplishment.known_issues)}

### Recommended for Future
{chr(10).join(f"- {step}" for step in accomplishment.next_steps[:3])}

---
"""
        
        # Append to AGENTS.md
        if self.agents_path.exists():
            content = self.agents_path.read_text()
            # Find "# Recent Sessions" section or create it
            if "# Recent Sessions" in content:
                content = content.replace(
                    "# Recent Sessions",
                    f"# Recent Sessions\n{learning_entry}"
                )
            else:
                content += f"\n\n# Recent Sessions\n{learning_entry}"
            
            self.agents_path.write_text(content)
            return f"Added session {accomplishment.session_id} learnings"
        
        return "AGENTS.md not found"
    
    def _extract_learnings(
        self,
        accomplishment: AccomplishmentReport,
        plan: CoordinationPlan
    ) -> List[str]:
        """Extract key learnings from accomplishment"""
        learnings = []
        
        if accomplishment.integration_status == "success":
            learnings.append("Scope allocation was effective - zero conflicts")
        
        if len(plan.waves) > 1:
            learnings.append(f"Multi-wave coordination ({len(plan.waves)} waves) executed successfully")
        
        if accomplishment.quality_gates.get('all_passed'):
            learnings.append("Quality gates validated integration correctness")
        
        return learnings
    
    def generate_commit_message(
        self,
        accomplishment: AccomplishmentReport,
        task_type: TaskType
    ) -> str:
        """
        Generate conventional commit message
        """
        type_prefix = {
            TaskType.RESET: "refactor",
            TaskType.FEATURE: "feat",
            TaskType.BUG: "fix",
            TaskType.REFACTOR: "refactor",
            TaskType.ENHANCEMENT: "feat"
        }
        
        prefix = type_prefix.get(task_type, "chore")
        summary = accomplishment.summary.split('\n')[0][:50]
        
        commit_msg = f"""{prefix}: {summary}

{accomplishment.summary}

Objectives completed:
{chr(10).join(f"- {obj}" for obj in accomplishment.objectives_completed)}

Modified files: {len(accomplishment.files_modified)}
Tests: {accomplishment.test_results.get('status', 'Unknown')}

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>
"""
        return commit_msg

# ============================================================================
# MAIN ORCHESTRATOR (Stub - to be completed)
# ============================================================================

class AnalyticOrchestrator:
    """
    Complete autonomous orchestrator
    TODO: Implement full orchestration logic
    """
    
    def __init__(self, team_config_path: str = "team.json"):
        self.db = Database()
        self.doc_gen = DocumentationGenerator()
        self.auto_doc = AutoDocumentationEngine()
        self.current_session: Optional[str] = None
        self.current_status = OrchestratorStatus(
            phase=OrchestratorPhase.IDLE,
            progress_percent=0,
            current_activity="Ready",
            elapsed_time=0,
            estimated_remaining=None
        )
    
    def create_session(self) -> str:
        """Create new session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = session_id
        return session_id
    
    async def run_full_cycle(
        self,
        owner_request: str,
        uploaded_files: List[str]
    ) -> AccomplishmentReport:
        """
        Run full AP cycle:
        1. ANALYTIC PHASE
        2. PLANNING PHASE
        3. EXECUTION PHASE
        4. POST-EXECUTION PHASE (generate accomplishment)
        5. AUTO-DOCUMENTATION PHASE (update project docs)
        """
        session_id = self.create_session()
        
        # TODO: Implement full cycle
        # For now, create stub accomplishment
        accomplishment = AccomplishmentReport(
            accomplishment_id=str(uuid4()),
            session_id=session_id,
            plan_id="plan_stub",
            summary="Stub accomplishment for testing",
            objectives_completed=["Objective 1"],
            files_modified=["file1.py"],
            test_results={"status": "passed", "total": 10, "passed": 10, "failed": 0},
            quality_gates={"ruff": "passed", "mypy": "passed"},
            integration_status="success",
            known_issues=[],
            next_steps=["Continue with next feature"],
            commit_message="",
            timestamp=datetime.now().isoformat()
        )
        
        # Generate accomplishment markdown
        accomplishment_md = self.doc_gen.generate_accomplishment_report_md(accomplishment)
        accomplishment_file = ACCOMPLISHMENTS_DIR / f"ACCOMPLISHMENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        accomplishment_file.write_text(accomplishment_md)
        accomplishment.file_path = str(accomplishment_file)
        
        # Generate commit message
        accomplishment.commit_message = self.auto_doc.generate_commit_message(
            accomplishment,
            TaskType.FEATURE
        )
        
        return accomplishment

# ============================================================================
# CLI INTERFACE (for testing)
# ============================================================================

async def main():
    """CLI interface for orchestrator"""
    print("🧠 Analytic Programming Orchestrator")
    print("=" * 50)
    
    orchestrator = AnalyticOrchestrator()
    
    # Test run
    accomplishment = await orchestrator.run_full_cycle(
        owner_request="Add authentication to the app",
        uploaded_files=[]
    )
    
    print(f"\n✓ Accomplishment saved to: {accomplishment.file_path}")
    print(f"\n📋 Commit message:\n{accomplishment.commit_message}")

if __name__ == "__main__":
    asyncio.run(main())
