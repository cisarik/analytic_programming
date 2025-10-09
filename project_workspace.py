#!/usr/bin/env python3
"""
project_workspace.py - Project Workspace Manager

Manages project directory structure:
~/.ap/projects/<project_name>/
  ├── AGENTS.md          # Agent configuration
  ├── README.md          # Project overview
  ├── PRD.md            # Product requirements
  ├── TODOs.md          # Tasks & todos
  ├── BUGs.md           # Known issues
  ├── FEATURES.md       # Feature specs
  └── .git/             # Version control

Version: 1.0.0
Date: October 9, 2025

TODO:
- [ ] Add custom file templates support
- [ ] Implement file search across all MD files
- [ ] Add drag & drop for reordering TODOs/BUGs
- [ ] Support for inline editing in UI
- [ ] Add export to PDF/DOCX
- [ ] Implement multi-device sync
- [ ] Add keyboard shortcuts for navigation
- [ ] Support for collaborative editing (multiple users)
- [ ] Add file diff view (compare versions)
- [ ] Implement auto-backup system
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectFile:
    """Represents a project markdown file"""
    name: str
    path: Path
    content: str
    loaded: bool = False
    icon: str = "📄"


class ProjectWorkspace:
    """
    Project Workspace Manager
    
    Creates and manages project directories with markdown files
    for brainstorming, orchestration, and project management
    """
    
    # Template files with default content
    TEMPLATES = {
        "AGENTS.md": """# Agents Configuration

## Project Context
- **Project Name:** {project_name}
- **Created:** {created_date}
- **Last Updated:** {updated_date}

## Agent Knowledge Base
This document is loaded by brainstorming agent on session start.

### Project Overview
(To be filled during brainstorming)

### Key Decisions
- Decision 1: (TBD)
- Decision 2: (TBD)

### Architecture Notes
- Tech stack: (TBD)
- Design patterns: (TBD)

### Constraints
- Performance: (TBD)
- Security: (TBD)
- Budget: (TBD)

---
*This file is auto-loaded by brainstorming agent*
""",
        
        "README.md": """# {project_name}

**Status:** 🚧 In Development  
**Created:** {created_date}

## Overview
(Project description - to be filled during brainstorming)

## Quick Start
(Setup instructions - TBD)

## Documentation
- [PRD.md](PRD.md) - Product Requirements
- [TODOs.md](TODOs.md) - Tasks & Todos
- [BUGs.md](BUGs.md) - Known Issues
- [AGENTS.md](AGENTS.md) - Agent Configuration

## Status
- [ ] Brainstorming complete
- [ ] PRD finalized
- [ ] Orchestration ready
- [ ] Implementation started
""",
        
        "PRD.md": """# {project_name} - Product Requirements Document

**Version:** 1.0.0  
**Created:** {created_date}  
**Last Updated:** {updated_date}

## Project Name
{project_name}

## Overview
(Project description)

## Requirements
- R1: (Functional requirement)
- R2: (Non-functional requirement)

## Features
- F1: (Feature description)
- F2: (Feature description)

## Architecture
- Technology stack: (TBD)
- System design: (TBD)

## Constraints
- Performance: (TBD)
- Security: (TBD)
- Scalability: (TBD)

## Acceptance Criteria
- Criterion 1: (TBD)
- Criterion 2: (TBD)

---
*Click on any section to send to brainstorming agent*
""",
        
        "TODOs.md": """# {project_name} - Tasks & TODOs

**Last Updated:** {updated_date}

## 🎯 Current Sprint

### High Priority
- [ ] TODO-1: (Task description)
- [ ] TODO-2: (Task description)

### Medium Priority
- [ ] TODO-3: (Task description)

### Low Priority
- [ ] TODO-4: (Task description)

## 📋 Backlog
- [ ] BACKLOG-1: (Future task)
- [ ] BACKLOG-2: (Future task)

## ✅ Completed
- [x] DONE-1: (Completed task)

---
*Click on any TODO to send to brainstorming agent*
""",
        
        "BUGs.md": """# {project_name} - Known Issues

**Last Updated:** {updated_date}

## 🔴 Critical
- [ ] BUG-1: (Critical bug description)

## 🟠 High Priority
- [ ] BUG-2: (High priority bug)

## 🟡 Medium Priority
- [ ] BUG-3: (Medium priority bug)

## 🟢 Low Priority
- [ ] BUG-4: (Low priority bug)

## ✅ Resolved
- [x] BUG-0: (Resolved bug)

---
*Click on any BUG to send to brainstorming agent*
""",
        
        "FEATURES.md": """# {project_name} - Feature Specifications

**Last Updated:** {updated_date}

## 📦 Planned Features

### Feature 1: (Name)
**Status:** 🔵 Planned  
**Priority:** High

**Description:**
(Feature description)

**Requirements:**
- Requirement 1
- Requirement 2

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

---

### Feature 2: (Name)
**Status:** 🟡 In Progress  
**Priority:** Medium

(Feature spec)

---

## ✅ Completed Features
- [x] Feature 0: (Completed feature)

---
*Click on any feature to send to brainstorming agent*
"""
    }
    
    def __init__(self, base_dir: str = "~/.ap/projects"):
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(self, project_name: str) -> Path:
        """
        Create new project workspace
        
        Args:
            project_name: Project name (used for directory)
        
        Returns:
            Path to project directory
        """
        # Sanitize project name for directory
        safe_name = self._sanitize_name(project_name)
        project_dir = self.base_dir / safe_name
        
        if project_dir.exists():
            raise ValueError(f"Project '{project_name}' already exists")
        
        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create template files
        created_date = datetime.now().strftime("%Y-%m-%d")
        updated_date = created_date
        
        for filename, template in self.TEMPLATES.items():
            file_path = project_dir / filename
            content = template.format(
                project_name=project_name,
                created_date=created_date,
                updated_date=updated_date
            )
            file_path.write_text(content)
        
        # Initialize git repo
        try:
            import subprocess
            subprocess.run(
                ["git", "init"],
                cwd=project_dir,
                capture_output=True,
                check=True
            )
            
            # Create .gitignore
            gitignore = project_dir / ".gitignore"
            gitignore.write_text("*.pyc\n__pycache__/\n.DS_Store\n")
            
            # Initial commit
            subprocess.run(
                ["git", "add", "."],
                cwd=project_dir,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial project setup"],
                cwd=project_dir,
                capture_output=True,
                check=True
            )
        except Exception as e:
            print(f"⚠️  Git init failed: {e}")
        
        return project_dir
    
    def get_project_dir(self, project_name: str) -> Optional[Path]:
        """Get project directory path"""
        safe_name = self._sanitize_name(project_name)
        project_dir = self.base_dir / safe_name
        
        if project_dir.exists():
            return project_dir
        return None
    
    def list_projects(self) -> List[str]:
        """List all projects"""
        if not self.base_dir.exists():
            return []
        
        projects = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                projects.append(item.name)
        
        return sorted(projects)
    
    def get_project_files(self, project_name: str) -> List[ProjectFile]:
        """
        Get all markdown files in project
        
        Returns list of ProjectFile objects with metadata
        """
        project_dir = self.get_project_dir(project_name)
        if not project_dir:
            return []
        
        files = []
        icons = {
            "README.md": "📖",
            "PRD.md": "📝",
            "AGENTS.md": "🤖",
            "TODOs.md": "📋",
            "BUGs.md": "🐛",
            "FEATURES.md": "⚡"
        }
        
        for md_file in project_dir.glob("*.md"):
            if md_file.name.startswith('.'):
                continue
            
            files.append(ProjectFile(
                name=md_file.name,
                path=md_file,
                content=md_file.read_text(),
                icon=icons.get(md_file.name, "📄")
            ))
        
        # Sort by priority
        priority_order = ["README.md", "AGENTS.md", "PRD.md", "FEATURES.md", "TODOs.md", "BUGs.md"]
        files.sort(key=lambda f: priority_order.index(f.name) if f.name in priority_order else 99)
        
        return files
    
    def get_context_files(self, project_name: str) -> Dict[str, str]:
        """
        Get files that should be loaded as agent context
        
        Returns dict: {filename: content}
        """
        project_dir = self.get_project_dir(project_name)
        if not project_dir:
            return {}
        
        # Files to load as context (for agent)
        context_files = ["AGENTS.md", "README.md", "PRD.md"]
        
        context = {}
        for filename in context_files:
            file_path = project_dir / filename
            if file_path.exists():
                context[filename] = file_path.read_text()
        
        return context
    
    def update_file(self, project_name: str, filename: str, content: str):
        """Update project file content"""
        project_dir = self.get_project_dir(project_name)
        if not project_dir:
            raise ValueError(f"Project '{project_name}' not found")
        
        file_path = project_dir / filename
        
        # Update "Last Updated" timestamp
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Last Updated:' in line:
                lines[i] = f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}"
                break
        
        file_path.write_text('\n'.join(lines))
        
        # Git commit
        self._git_commit(project_dir, f"Update {filename}")
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name for directory"""
        # Replace spaces with hyphens, remove special chars
        safe = name.lower().replace(' ', '-')
        safe = ''.join(c for c in safe if c.isalnum() or c == '-')
        return safe
    
    def _git_commit(self, project_dir: Path, message: str):
        """Git commit changes"""
        try:
            import subprocess
            subprocess.run(
                ["git", "add", "."],
                cwd=project_dir,
                capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_dir,
                capture_output=True
            )
        except Exception:
            pass  # Git operations are optional


# ============================================================================
# DEMO / TESTING
# ============================================================================

def demo():
    """Demo project workspace"""
    print("=" * 60)
    print("DEMO: Project Workspace Manager")
    print("=" * 60)
    
    workspace = ProjectWorkspace()
    
    # Create project
    print("\n📁 Creating project 'Blog API'...")
    project_dir = workspace.create_project("Blog API")
    print(f"✓ Created: {project_dir}")
    
    # List files
    print("\n📄 Project files:")
    files = workspace.get_project_files("Blog API")
    for file in files:
        print(f"  {file.icon} {file.name} ({len(file.content)} bytes)")
    
    # Get context
    print("\n🤖 Agent context files:")
    context = workspace.get_context_files("Blog API")
    for filename, content in context.items():
        print(f"  ✅ {filename} ({len(content)} bytes)")
    
    # List all projects
    print("\n📂 All projects:")
    projects = workspace.list_projects()
    for project in projects:
        print(f"  - {project}")
    
    print("\n✓ Demo complete")


if __name__ == "__main__":
    demo()

