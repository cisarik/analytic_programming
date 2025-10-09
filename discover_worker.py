#!/usr/bin/env python3
"""
discover_worker.py - CLI Tool pre MCP Worker Capability Discovery

Interaktívny nástroj pre automatické objavovanie capabilities workerov:
1. Pripojí sa k MCP serveru
2. Získa zoznam tools
3. Analyzuje cez LLM API
4. Zobrazí results s potvrdením
5. Updatne team.json (s backup)

Usage:
    python discover_worker.py --worker-id claude-main
    python discover_worker.py --worker-id claude-main --auto-approve
    python discover_worker.py --list-workers
    python discover_worker.py --rediscover-all

Version: 1.0.0
Author: Analytic Programming Team
Date: October 9, 2025
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Optional

# Import discovery system
from mcp_capability_discovery import (
    MCPCapabilityDiscoverer,
    DiscoveryResult,
    format_discovery_result
)
from mcp_server_stdio import (
    MCPServerStdio,
    MCPWorkerConfig,
    MCPWorkerType,
    WebSocketBroadcaster
)

# ============================================================================
# CLI UI FUNCTIONS
# ============================================================================

def print_banner():
    """Vytlačí úvodný banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🔍 MCP Worker Capability Discovery Tool                 ║
║                                                              ║
║     Automaticky objavuje schopnosti MCP serverov            ║
║     pomocou LLM analýzy dostupných tools                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def print_section(title: str):
    """Vytlačí section header"""
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print('═' * 64)

async def list_workers(team_config_path: Path):
    """Vypíše zoznam dostupných workerov z team.json"""
    if not team_config_path.exists():
        print(f"✗ team.json not found at: {team_config_path}")
        return
    
    with open(team_config_path, 'r') as f:
        config = json.load(f)
    
    print_section("📋 Available Workers")
    
    for worker in config.get('workers', []):
        worker_id = worker.get('id', 'unknown')
        agent_type = worker.get('agent_type', 'unknown')
        enabled = worker.get('enabled', False)
        capabilities = worker.get('capabilities', [])
        
        status = "✓ enabled " if enabled else "✗ disabled"
        
        print(f"\n  {status} {worker_id} ({agent_type})")
        print(f"    Capabilities: {', '.join(capabilities) if capabilities else '(none)'}")
        
        mcp_config = worker.get('mcp_config', {})
        command = mcp_config.get('command', 'N/A')
        print(f"    Command: {command}")
    
    print()

def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Interaktívny yes/no prompt"""
    suffix = " [Y/n]: " if default else " [y/N]: "
    
    while True:
        response = input(question + suffix).strip().lower()
        
        if not response:
            return default
        
        if response in ['y', 'yes', 'ano']:
            return True
        elif response in ['n', 'no', 'nie']:
            return False
        else:
            print("  ⚠️  Zadaj 'y' alebo 'n'")

async def discover_single_worker(
    worker_id: str,
    discoverer: MCPCapabilityDiscoverer,
    team_config: dict,
    auto_approve: bool = False,
    dry_run: bool = False
) -> bool:
    """
    Objaví capabilities pre jedného workera
    
    Returns:
        True ak boli capabilities updatnuté, False inak
    """
    print_section(f"🔍 Discovering: {worker_id}")
    
    # Nájdi worker config
    worker_config = None
    for worker in team_config.get('workers', []):
        if worker.get('id') == worker_id:
            worker_config = worker
            break
    
    if not worker_config:
        print(f"✗ Worker {worker_id} not found in team.json")
        return False
    
    # Vytvor MCP config
    mcp_cfg = worker_config.get('mcp_config', {})
    config = MCPWorkerConfig(
        worker_id=worker_id,
        worker_type=MCPWorkerType(worker_config['agent_type']),
        command=mcp_cfg.get('command', 'python'),
        args=mcp_cfg.get('args', []),
        env=mcp_cfg.get('env', {}),
        max_concurrent_tasks=worker_config.get('max_concurrent_tasks', 1),
        enabled=worker_config.get('enabled', True)
    )
    
    # Spusti MCP server
    broadcaster = WebSocketBroadcaster()
    server = MCPServerStdio(config, broadcaster)
    
    try:
        print("  → Starting MCP server...")
        await server.start()
        
        # Wait for initialization
        await asyncio.sleep(2)
        
        # Discover capabilities
        result = await discoverer.discover_worker_capabilities(
            worker_id=worker_id,
            mcp_server=server,
            worker_description=f"{worker_config.get('agent_type')} worker"
        )
        
        # Zobraz results
        print("\n" + format_discovery_result(result))
        
        # Prompt pre potvrdenie (ak nie auto-approve)
        if dry_run:
            print("  ℹ️  DRY RUN - no changes will be made")
            return False
        
        if not auto_approve:
            if not prompt_yes_no("\n  💾 Update team.json with these capabilities?", default=True):
                print("  ℹ️  Skipped update")
                return False
        
        # Update team.json
        print("\n  → Updating team.json...")
        success = await discoverer.update_team_config(
            worker_id=worker_id,
            capabilities=result.analysis.capabilities,
            backup=True
        )
        
        if success:
            print("  ✓ Capabilities updated successfully!")
            return True
        else:
            print("  ✗ Failed to update capabilities")
            return False
    
    except Exception as e:
        print(f"  ✗ Error during discovery: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Shutdown server
        print("  → Stopping MCP server...")
        await server.stop()

async def rediscover_all_workers(
    discoverer: MCPCapabilityDiscoverer,
    team_config: dict,
    auto_approve: bool = False,
    only_enabled: bool = True
) -> int:
    """
    Objaví capabilities pre všetkých workerov
    
    Returns:
        Počet úspešne updatnutých workerov
    """
    print_section("🔄 Re-discovering All Workers")
    
    workers = team_config.get('workers', [])
    
    if only_enabled:
        workers = [w for w in workers if w.get('enabled', False)]
        print(f"  → Processing {len(workers)} enabled workers\n")
    else:
        print(f"  → Processing {len(workers)} workers (including disabled)\n")
    
    updated_count = 0
    
    for worker in workers:
        worker_id = worker.get('id')
        
        success = await discover_single_worker(
            worker_id=worker_id,
            discoverer=discoverer,
            team_config=team_config,
            auto_approve=auto_approve
        )
        
        if success:
            updated_count += 1
        
        # Pauza medzi workermi
        if len(workers) > 1:
            await asyncio.sleep(2)
    
    print_section(f"✓ Complete: {updated_count}/{len(workers)} workers updated")
    
    return updated_count

# ============================================================================
# MAIN CLI
# ============================================================================

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Worker Capability Discovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover single worker
  python discover_worker.py --worker-id claude-main
  
  # Auto-approve (no confirmation)
  python discover_worker.py --worker-id gpt4-main --auto-approve
  
  # Dry run (no changes)
  python discover_worker.py --worker-id codex-fast --dry-run
  
  # List all workers
  python discover_worker.py --list-workers
  
  # Re-discover all enabled workers
  python discover_worker.py --rediscover-all
  
  # Use different LLM provider
  python discover_worker.py --worker-id claude-main --llm-provider claude --llm-model claude-3-opus
        """
    )
    
    # Actions
    parser.add_argument(
        '--worker-id',
        type=str,
        help='Worker ID to discover capabilities for'
    )
    parser.add_argument(
        '--list-workers',
        action='store_true',
        help='List all available workers from team.json'
    )
    parser.add_argument(
        '--rediscover-all',
        action='store_true',
        help='Re-discover capabilities for all workers'
    )
    
    # Options
    parser.add_argument(
        '--team-config',
        type=Path,
        default=Path('team.json'),
        help='Path to team.json (default: team.json)'
    )
    parser.add_argument(
        '--auto-approve',
        action='store_true',
        help='Automatically approve changes without prompting'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform discovery but don\'t update team.json'
    )
    parser.add_argument(
        '--only-enabled',
        action='store_true',
        default=True,
        help='Only process enabled workers (default: True)'
    )
    
    # LLM options
    parser.add_argument(
        '--llm-provider',
        type=str,
        choices=['openai', 'claude'],
        default='openai',
        help='LLM provider for analysis (default: openai)'
    )
    parser.add_argument(
        '--llm-model',
        type=str,
        default='gpt-4',
        help='LLM model name (default: gpt-4)'
    )
    parser.add_argument(
        '--llm-api-key',
        type=str,
        help='LLM API key (or use OPENAI_API_KEY / ANTHROPIC_API_KEY env)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Load team.json
    if not args.team_config.exists():
        print(f"✗ team.json not found at: {args.team_config}")
        print("  Create team.json first or use --team-config to specify path")
        sys.exit(1)
    
    with open(args.team_config, 'r') as f:
        team_config = json.load(f)
    
    # Handle --list-workers
    if args.list_workers:
        await list_workers(args.team_config)
        sys.exit(0)
    
    # Check for required action
    if not args.worker_id and not args.rediscover_all:
        print("✗ Specify --worker-id or --rediscover-all or --list-workers")
        parser.print_help()
        sys.exit(1)
    
    # Create discoverer
    try:
        discoverer = MCPCapabilityDiscoverer(
            llm_provider=args.llm_provider,
            llm_api_key=args.llm_api_key,
            llm_model=args.llm_model,
            team_config_path=args.team_config
        )
    except ValueError as e:
        print(f"✗ {e}")
        print(f"\n  Set {args.llm_provider.upper()}_API_KEY environment variable")
        print(f"  or use --llm-api-key option")
        sys.exit(1)
    
    # Handle actions
    try:
        if args.rediscover_all:
            updated = await rediscover_all_workers(
                discoverer=discoverer,
                team_config=team_config,
                auto_approve=args.auto_approve,
                only_enabled=args.only_enabled
            )
            sys.exit(0 if updated > 0 else 1)
        
        elif args.worker_id:
            success = await discover_single_worker(
                worker_id=args.worker_id,
                discoverer=discoverer,
                team_config=team_config,
                auto_approve=args.auto_approve,
                dry_run=args.dry_run
            )
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

