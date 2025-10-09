#!/usr/bin/env python3
"""
seed_workers.py - Seed database with test workers

Creates sample workers in database for testing Workers UI
"""

from ap_studio_db import APStudioDB

def seed_workers():
    """Seed database with test workers"""
    db = APStudioDB("ap_studio.db")
    
    print("🌱 Seeding test workers...")
    
    workers = [
        {
            "worker_id": "claude-main",
            "agent_type": "claude",
            "capabilities": ["complex_logic", "architecture", "deep_analysis", "refactoring"],
            "mcp_config": {
                "command": "npx",
                "args": ["-y", "@anthropic-ai/claude-mcp"],
                "env": {"ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"}
            },
            "max_concurrent": 3
        },
        {
            "worker_id": "gpt4-main",
            "agent_type": "gpt4",
            "capabilities": ["algorithms", "debugging", "testing", "performance"],
            "mcp_config": {
                "command": "python",
                "args": ["workers/openai_worker.py"],
                "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"}
            },
            "max_concurrent": 2
        },
        {
            "worker_id": "codex-fast",
            "agent_type": "codex",
            "capabilities": ["refactoring", "type_hints", "python", "quick_fixes"],
            "mcp_config": {
                "command": "python",
                "args": ["workers/codex_worker.py"],
                "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"}
            },
            "max_concurrent": 5
        }
    ]
    
    for worker_data in workers:
        try:
            db.add_worker(
                worker_id=worker_data["worker_id"],
                agent_type=worker_data["agent_type"],
                capabilities=worker_data["capabilities"],
                mcp_config=worker_data["mcp_config"],
                max_concurrent=worker_data["max_concurrent"]
            )
            print(f"  ✓ Added worker: {worker_data['worker_id']}")
        except Exception as e:
            print(f"  ✗ Failed to add {worker_data['worker_id']}: {e}")
    
    print("\n✅ Workers seeded successfully!")
    print("\nTest Workers UI:")
    print("  1. Start backend: python ap_studio_backend.py")
    print("  2. Open UI: open ap_studio.html")
    print("  3. Click 'Workers' tab")


if __name__ == "__main__":
    seed_workers()

