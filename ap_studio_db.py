#!/usr/bin/env python3
"""
ap_studio_db.py - AP Studio Database Layer

SQLite database for AP Studio:
- Projects & Versions
- Brainstorming sessions & messages
- Workers registry
- Orchestrations tracking
- Issues & Features

Version: 1.0.0
Date: October 9, 2025
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class APStudioDB:
    """AP Studio Database Manager"""
    
    def __init__(self, db_path: str = "ap_studio.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    path TEXT NOT NULL,
                    git_repo_path TEXT,
                    prd_content TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, version)
                )
            """)
            
            # Brainstorming sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brainstorm_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                )
            """)
            
            # Brainstorm messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brainstorm_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES brainstorm_sessions(id)
                )
            """)
            
            # Workers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id TEXT UNIQUE NOT NULL,
                    agent_type TEXT NOT NULL,
                    capabilities TEXT,
                    mcp_config TEXT,
                    max_concurrent INTEGER DEFAULT 1,
                    enabled BOOLEAN DEFAULT 1,
                    status TEXT DEFAULT 'offline',
                    last_seen TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Orchestrations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orchestrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'running',
                    phase TEXT,
                    current_wave INTEGER,
                    total_waves INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    analysis_report TEXT,
                    coordination_plan TEXT,
                    accomplishment_report TEXT,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                )
            """)
            
            # Issues
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                )
            """)
            
            # Features
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'planned',
                    priority TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                )
            """)
            
            # Worker tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worker_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orchestration_id INTEGER NOT NULL,
                    worker_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    wave INTEGER NOT NULL,
                    title TEXT,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER,
                    files_modified TEXT,
                    error_message TEXT,
                    FOREIGN KEY (orchestration_id) REFERENCES orchestrations(id)
                )
            """)
            
            conn.commit()
    
    # ========================================================================
    # PROJECTS
    # ========================================================================
    
    def create_project(self, name: str, description: str = "") -> int:
        """Create new project"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description) VALUES (?, ?)",
                (name, description)
            )
            return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """Get project by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_projects(self) -> List[Dict]:
        """List all projects"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # VERSIONS
    # ========================================================================
    
    def create_version(
        self,
        project_id: int,
        version: str,
        path: str,
        git_repo_path: Optional[str] = None,
        prd_content: str = ""
    ) -> int:
        """Create new version"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO versions 
                (project_id, version, path, git_repo_path, prd_content)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, version, path, git_repo_path, prd_content))
            return cursor.lastrowid
    
    def get_version(self, version_id: int) -> Optional[Dict]:
        """Get version by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM versions WHERE id = ?", (version_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_versions(self, project_id: int) -> List[Dict]:
        """List all versions for a project"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM versions WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_version_prd(self, version_id: int, prd_content: str):
        """Update PRD content for version"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE versions SET prd_content = ? WHERE id = ?",
                (prd_content, version_id)
            )
    
    def update_version_status(self, version_id: int, status: str):
        """Update version status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE versions SET status = ? WHERE id = ?",
                (status, version_id)
            )
    
    # ========================================================================
    # BRAINSTORMING
    # ========================================================================
    
    def create_brainstorm_session(self, version_id: int) -> int:
        """Create new brainstorm session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO brainstorm_sessions (version_id) VALUES (?)",
                (version_id,)
            )
            return cursor.lastrowid
    
    def get_brainstorm_session(self, session_id: int) -> Optional[Dict]:
        """Get brainstorm session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM brainstorm_sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_brainstorm_message(
        self,
        session_id: int,
        role: str,
        content: str
    ) -> int:
        """Add message to brainstorm session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO brainstorm_messages (session_id, role, content)
                VALUES (?, ?, ?)
            """, (session_id, role, content))
            return cursor.lastrowid
    
    def get_brainstorm_messages(self, session_id: int) -> List[Dict]:
        """Get all messages for session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM brainstorm_messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def complete_brainstorm_session(self, session_id: int):
        """Mark session as completed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE brainstorm_sessions 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (session_id,))
    
    # ========================================================================
    # WORKERS
    # ========================================================================
    
    def add_worker(
        self,
        worker_id: str,
        agent_type: str,
        capabilities: List[str],
        mcp_config: Dict,
        max_concurrent: int = 1
    ) -> int:
        """Add new worker"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workers 
                (worker_id, agent_type, capabilities, mcp_config, max_concurrent)
                VALUES (?, ?, ?, ?, ?)
            """, (
                worker_id,
                agent_type,
                json.dumps(capabilities),
                json.dumps(mcp_config),
                max_concurrent
            ))
            return cursor.lastrowid
    
    def get_worker(self, worker_id: str) -> Optional[Dict]:
        """Get worker by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM workers WHERE worker_id = ?",
                (worker_id,)
            )
            row = cursor.fetchone()
            if row:
                worker = dict(row)
                worker['capabilities'] = json.loads(worker['capabilities']) if worker['capabilities'] else []
                worker['mcp_config'] = json.loads(worker['mcp_config']) if worker['mcp_config'] else {}
                return worker
            return None
    
    def list_workers(self, enabled_only: bool = False) -> List[Dict]:
        """List all workers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM workers"
            if enabled_only:
                query += " WHERE enabled = 1"
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query)
            workers = []
            for row in cursor.fetchall():
                worker = dict(row)
                worker['capabilities'] = json.loads(worker['capabilities']) if worker['capabilities'] else []
                worker['mcp_config'] = json.loads(worker['mcp_config']) if worker['mcp_config'] else {}
                workers.append(worker)
            return workers
    
    def update_worker_status(self, worker_id: str, status: str):
        """Update worker status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE workers 
                SET status = ?, last_seen = CURRENT_TIMESTAMP
                WHERE worker_id = ?
            """, (status, worker_id))
    
    # ========================================================================
    # ORCHESTRATIONS
    # ========================================================================
    
    def create_orchestration(self, version_id: int) -> int:
        """Create new orchestration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orchestrations (version_id) VALUES (?)",
                (version_id,)
            )
            return cursor.lastrowid
    
    def update_orchestration_status(
        self,
        orchestration_id: int,
        status: str,
        phase: Optional[str] = None,
        current_wave: Optional[int] = None,
        total_waves: Optional[int] = None
    ):
        """Update orchestration status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orchestrations 
                SET status = ?, phase = ?, current_wave = ?, total_waves = ?
                WHERE id = ?
            """, (status, phase, current_wave, total_waves, orchestration_id))
    
    def get_active_orchestrations(self) -> List[Dict]:
        """Get all active orchestrations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orchestrations 
                WHERE status = 'running'
                ORDER BY started_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # TODO: Add missing database methods for complete orchestration management
    # - get_orchestration(orchestration_id: int) -> Optional[Dict]
    # - get_orchestrations(version_id=None, status=None, limit=50, offset=0) -> List[Dict]
    # - get_orchestration_with_details(orchestration_id: int) -> Dict  # Include version, workers, files
    # - delete_orchestration(orchestration_id: int) -> bool
    # - get_orchestration_metrics(version_id: int) -> Dict  # Total runs, success rate, avg duration
    # - get_project_versions(project_id: int) -> List[Dict]  # All versions of project
    # - search_projects(query: str) -> List[Dict]  # Search by name/description


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Test database
    db = APStudioDB("test_ap_studio.db")
    
    print("✓ Database initialized")
    
    # Create test project
    project_id = db.create_project("Test Project", "Testing AP Studio DB")
    print(f"✓ Created project: {project_id}")
    
    # Create version
    version_id = db.create_version(
        project_id=project_id,
        version="0.01",
        path="projects/test-project/v0.01",
        prd_content="# Test PRD\n\nTest content"
    )
    print(f"✓ Created version: {version_id}")
    
    # Create brainstorm session
    session_id = db.create_brainstorm_session(version_id)
    print(f"✓ Created brainstorm session: {session_id}")
    
    # Add messages
    db.add_brainstorm_message(session_id, "assistant", "Ahoj! Aký projekt chceš vytvoriť?")
    db.add_brainstorm_message(session_id, "user", "Chcem REST API")
    print("✓ Added messages")
    
    # List projects
    projects = db.list_projects()
    print(f"✓ Projects: {len(projects)}")
    
    print("\n✅ Database test complete!")

