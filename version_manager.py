#!/usr/bin/env python3
"""
version_manager.py - Version Management with Git

Manages versioned directories and git repos:
- Creates version directories (v0.01, v0.02, ...)
- Initializes Git repo per version
- Commits PRD.md and other artifacts
- Supports AP_continue.md workflow

Version: 1.0.0
Date: October 9, 2025
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import subprocess


class VersionManager:
    """
    Version Manager for AP Studio
    
    Manages:
    - Version directories
    - Git repositories
    - PRD.md files
    - Issues & Features
    """
    
    def __init__(self, projects_root: str = "projects"):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(exist_ok=True)
    
    def create_version(
        self,
        project_name: str,
        version: str,
        prd_content: str = ""
    ) -> Path:
        """
        Create new version directory with git repo
        
        Args:
            project_name: Project name
            version: Version string (e.g., "0.01")
            prd_content: PRD.md content
        
        Returns:
            Path to version directory
        """
        # Create version directory
        version_dir = self.projects_root / project_name / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repo
        self._init_git_repo(version_dir)
        
        # Create .gitignore
        gitignore_path = version_dir / ".gitignore"
        gitignore_path.write_text("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local config
.env
*.local

# Temp files
*.tmp
*.log
""".strip())
        
        # Create PRD.md
        prd_path = version_dir / "PRD.md"
        if prd_content:
            prd_path.write_text(prd_content)
        else:
            prd_path.write_text(f"# {project_name}\n\n## Overview\n\n(To be filled)")
        
        # Create issues.json
        issues_path = version_dir / "issues.json"
        issues_path.write_text(json.dumps([], indent=2))
        
        # Create features.json
        features_path = version_dir / "features.json"
        features_path.write_text(json.dumps([], indent=2))
        
        # Create docs directory
        docs_dir = version_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "analyses").mkdir(exist_ok=True)
        (docs_dir / "plans").mkdir(exist_ok=True)
        (docs_dir / "accomplishments").mkdir(exist_ok=True)
        
        # Initial commit
        self._git_commit(
            version_dir,
            message=f"Initial commit: {project_name} v{version}",
            files=[".gitignore", "PRD.md", "issues.json", "features.json"]
        )
        
        print(f"✓ Created version: {version_dir}")
        return version_dir
    
    def update_prd(
        self,
        version_dir: Path,
        prd_content: str,
        commit_message: str = "Update PRD.md"
    ):
        """Update PRD.md and commit"""
        prd_path = version_dir / "PRD.md"
        prd_path.write_text(prd_content)
        
        self._git_commit(
            version_dir,
            message=commit_message,
            files=["PRD.md"]
        )
        
        print(f"✓ Updated PRD: {version_dir}")
    
    def add_issue(
        self,
        version_dir: Path,
        issue_type: str,
        title: str,
        description: str = "",
        priority: str = "medium"
    ):
        """Add issue to issues.json"""
        issues_path = version_dir / "issues.json"
        
        # Load existing issues
        if issues_path.exists():
            issues = json.loads(issues_path.read_text())
        else:
            issues = []
        
        # Add new issue
        issues.append({
            "id": len(issues) + 1,
            "type": issue_type,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "open",
            "created_at": datetime.now().isoformat()
        })
        
        # Save
        issues_path.write_text(json.dumps(issues, indent=2))
        
        # Commit
        self._git_commit(
            version_dir,
            message=f"Add issue: {title}",
            files=["issues.json"]
        )
    
    def add_feature(
        self,
        version_dir: Path,
        title: str,
        description: str = "",
        priority: str = "medium"
    ):
        """Add feature to features.json"""
        features_path = version_dir / "features.json"
        
        # Load existing features
        if features_path.exists():
            features = json.loads(features_path.read_text())
        else:
            features = []
        
        # Add new feature
        features.append({
            "id": len(features) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "planned",
            "created_at": datetime.now().isoformat()
        })
        
        # Save
        features_path.write_text(json.dumps(features, indent=2))
        
        # Commit
        self._git_commit(
            version_dir,
            message=f"Add feature: {title}",
            files=["features.json"]
        )
    
    def get_version_info(self, version_dir: Path) -> Dict:
        """Get version information"""
        return {
            "path": str(version_dir),
            "version": version_dir.name,
            "git_repo": str(version_dir / ".git"),
            "prd_exists": (version_dir / "PRD.md").exists(),
            "issues_count": len(self._load_json(version_dir / "issues.json")),
            "features_count": len(self._load_json(version_dir / "features.json")),
            "last_commit": self._get_last_commit(version_dir)
        }
    
    def _init_git_repo(self, path: Path):
        """Initialize git repository"""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=path,
                check=True,
                capture_output=True
            )
            
            # Configure git
            subprocess.run(
                ["git", "config", "user.name", "AP Studio"],
                cwd=path,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", "apstudio@analytic-programming.local"],
                cwd=path,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Git init error: {e}")
    
    def _git_commit(
        self,
        path: Path,
        message: str,
        files: Optional[List[str]] = None
    ):
        """Commit changes to git"""
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=path,
                        check=True,
                        capture_output=True
                    )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=path,
                    check=True,
                    capture_output=True
                )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=path,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # Might fail if no changes
            pass
    
    def _get_last_commit(self, path: Path) -> Optional[str]:
        """Get last commit message"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def _load_json(self, path: Path) -> List:
        """Load JSON file"""
        if path.exists():
            return json.loads(path.read_text())
        return []


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Test version manager
    vm = VersionManager("test_projects")
    
    print("=" * 60)
    print("DEMO: Version Manager")
    print("=" * 60)
    
    # Create version
    version_dir = vm.create_version(
        project_name="test-blog",
        version="0.01",
        prd_content="# Blog API\n\n## Overview\nREST API for blogging"
    )
    
    # Add issue
    vm.add_issue(
        version_dir,
        issue_type="bug",
        title="Fix authentication",
        description="Auth not working properly"
    )
    
    # Add feature
    vm.add_feature(
        version_dir,
        title="Comments system",
        description="Add comments to posts"
    )
    
    # Get info
    info = vm.get_version_info(version_dir)
    print("\nVersion info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Demo complete")

