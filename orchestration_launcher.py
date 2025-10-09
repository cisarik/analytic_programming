#!/usr/bin/env python3
"""
orchestration_launcher.py - Orchestration Launcher for AP Studio

Connects AP Studio UI with orchestrator_enhanced.py:
- Starts orchestration from version PRD.md
- Streams real-time progress via WebSocket
- Updates database with results

Version: 1.0.0
Date: October 9, 2025
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, AsyncIterator

# Import orchestrator
from orchestrator_enhanced import EnhancedOrchestrator

# Import database
from ap_studio_db import APStudioDB


class OrchestrationLauncher:
    """
    Launches and monitors orchestration runs
    """
    
    def __init__(self, db: APStudioDB):
        self.db = db
        self.active_orchestrations = {}  # orchestration_id -> orchestrator
    
    async def start_orchestration(
        self,
        version_id: int,
        websocket_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Start orchestration for a version
        
        Args:
            version_id: Version ID from database
            websocket_callback: Async function to send WebSocket messages
        
        Returns:
            Dict with orchestration status
        """
        # Get version from DB
        version = self.db.get_version(version_id)
        if not version:
            return {
                'success': False,
                'error': 'Version not found',
                'version_id': version_id
            }
        
        # Get PRD content
        prd_content = version['prd_content']
        if not prd_content:
            return {
                'success': False,
                'error': 'PRD.md is empty. Complete brainstorming first.',
                'version_id': version_id
            }
        
        # Create orchestration record
        orch_id = self.db.create_orchestration(version_id)
        
        # Send initial message
        if websocket_callback:
            await websocket_callback({
                'type': 'orchestration_started',
                'orchestration_id': orch_id,
                'version_id': version_id,
                'version': version['version'],
                'phase': 'initializing'
            })
        
        try:
            # Initialize orchestrator
            orchestrator = EnhancedOrchestrator()
            self.active_orchestrations[orch_id] = orchestrator
            
            # Update status
            self.db.update_orchestration_status(
                orch_id,
                status='running',
                phase='analytic'
            )
            
            # Mock owner request from PRD
            owner_request = f"""
Based on this PRD, implement the described features:

{prd_content}

Please analyze, plan, and execute the implementation.
"""
            
            # Stream orchestration phases
            async for update in self._stream_orchestration(
                orchestrator,
                owner_request,
                orch_id,
                websocket_callback
            ):
                # Update database
                if 'phase' in update:
                    self.db.update_orchestration_status(
                        orch_id,
                        status='running',
                        phase=update['phase'],
                        current_wave=update.get('wave'),
                        total_waves=update.get('total_waves')
                    )
            
            # Mark complete
            self.db.update_orchestration_status(
                orch_id,
                status='completed',
                phase='complete'
            )
            
            if websocket_callback:
                await websocket_callback({
                    'type': 'orchestration_complete',
                    'orchestration_id': orch_id,
                    'success': True
                })
            
            return {
                'success': True,
                'orchestration_id': orch_id,
                'version_id': version_id
            }
        
        except Exception as e:
            # Mark failed
            self.db.update_orchestration_status(
                orch_id,
                status='failed',
                phase='error'
            )
            
            if websocket_callback:
                await websocket_callback({
                    'type': 'orchestration_error',
                    'orchestration_id': orch_id,
                    'error': str(e)
                })
            
            return {
                'success': False,
                'error': str(e),
                'orchestration_id': orch_id
            }
        
        finally:
            # Cleanup
            self.active_orchestrations.pop(orch_id, None)
    
    async def _stream_orchestration(
        self,
        orchestrator: EnhancedOrchestrator,
        owner_request: str,
        orch_id: int,
        websocket_callback: Optional[callable]
    ) -> AsyncIterator[Dict]:
        """
        Stream orchestration progress
        
        Yields progress updates from:
        - ANALYTIC phase
        - PLANNING phase
        - EXECUTION phase
        """
        try:
            # Phase 1: ANALYTIC
            if websocket_callback:
                await websocket_callback({
                    'type': 'phase_update',
                    'orchestration_id': orch_id,
                    'phase': 'analytic',
                    'progress': 0,
                    'message': 'Analyzing codebase...'
                })
            
            analysis_result = None
            async for update in orchestrator.run_analytic_phase(owner_request, uploaded_files=[]):
                yield {'phase': 'analytic', **update}
                
                # Capture analysis result (from AnalysisReport)
                if 'report' in update:
                    from orchestrator import AnalysisReport
                    # Convert dict back to AnalysisReport
                    report_dict = update['report']
                    analysis_result = AnalysisReport(**report_dict)
                
                if websocket_callback:
                    await websocket_callback({
                        'type': 'phase_update',
                        'orchestration_id': orch_id,
                        'phase': 'analytic',
                        'progress': update.get('status', {}).get('progress_percent', 0),
                        'message': update.get('status', {}).get('message', ''),
                        'update': update
                    })
            
            # Phase 2: PLANNING
            if websocket_callback:
                await websocket_callback({
                    'type': 'phase_update',
                    'orchestration_id': orch_id,
                    'phase': 'planning',
                    'progress': 0,
                    'message': 'Creating coordination plan...'
                })
            
            plan_result = None
            async for update in orchestrator.run_planning_phase(analysis_result):
                yield {'phase': 'planning', **update}
                
                # Capture plan result (from CoordinationPlan)
                if 'plan' in update:
                    from orchestrator import CoordinationPlan
                    # Convert dict back to CoordinationPlan
                    plan_dict = update['plan']
                    plan_result = CoordinationPlan(**plan_dict)
                
                if websocket_callback:
                    await websocket_callback({
                        'type': 'phase_update',
                        'orchestration_id': orch_id,
                        'phase': 'planning',
                        'progress': update.get('status', {}).get('progress_percent', 0),
                        'message': update.get('status', {}).get('message', ''),
                        'update': update
                    })
            
            # Phase 3: EXECUTION
            if websocket_callback:
                await websocket_callback({
                    'type': 'phase_update',
                    'orchestration_id': orch_id,
                    'phase': 'execution',
                    'progress': 0,
                    'message': 'Starting worker execution...'
                })
            
            async for update in orchestrator.run_execution_phase(plan_result):
                yield {'phase': 'execution', **update}
                
                # Extract wave info
                wave = update.get('wave')
                total_waves = update.get('total_waves')
                
                if websocket_callback:
                    await websocket_callback({
                        'type': 'phase_update',
                        'orchestration_id': orch_id,
                        'phase': 'execution',
                        'wave': wave,
                        'total_waves': total_waves,
                        'progress': update.get('status', {}).get('progress_percent', 0),
                        'message': update.get('status', {}).get('message', ''),
                        'update': update
                    })
        
        except Exception as e:
            print(f"Orchestration stream error: {e}")
            raise
    
    def get_orchestration_status(self, orch_id: int) -> Optional[Dict]:
        """Get current status of orchestration"""
        # Check if running
        if orch_id in self.active_orchestrations:
            orchestrator = self.active_orchestrations[orch_id]
            return {
                'running': True,
                'status': orchestrator.current_status.__dict__ if hasattr(orchestrator, 'current_status') else {}
            }
        
        # Check database
        # TODO: Query orchestrations table
        # - Add get_orchestration() method to APStudioDB
        # - Return status, phase, waves, timestamps
        # - Include worker activity summary
        return None
    
    async def cancel_orchestration(self, orch_id: int) -> bool:
        """Cancel running orchestration"""
        if orch_id in self.active_orchestrations:
            # TODO: Implement graceful cancellation
            # - Stop worker execution (send CANCEL message via MCP)
            # - Rollback partial changes (Git reset)
            # - Notify via WebSocket (orchestration_cancelled event)
            # - Cleanup resources (close worker connections)
            self.active_orchestrations.pop(orch_id)
            
            self.db.update_orchestration_status(
                orch_id,
                status='cancelled',
                phase='cancelled'
            )
            
            return True
        
        return False


# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo orchestration launcher"""
    print("🚀 Orchestration Launcher Demo")
    print("=" * 60)
    
    # Initialize
    import time
    db = APStudioDB("test_orchestration.db")
    launcher = OrchestrationLauncher(db)
    
    # Create test project & version (unique name)
    project_name = f"Test Project {int(time.time())}"
    project_id = db.create_project(project_name, "Demo orchestration")
    version_id = db.create_version(
        project_id=project_id,
        version="0.01",
        path="test_projects/test/v0.01",
        prd_content="""# Test Project

## Overview
Simple REST API for testing orchestration.

## Requirements
- R1: User authentication
- R2: CRUD operations for posts

## Architecture
- Backend: FastAPI
- Database: SQLite
"""
    )
    
    print(f"✓ Created test version: {version_id}")
    
    # Mock WebSocket callback
    async def ws_callback(message):
        print(f"  → WebSocket: {message['type']}")
        if 'message' in message:
            print(f"     {message['message']}")
    
    # Start orchestration
    print("\n🎭 Starting orchestration...")
    result = await launcher.start_orchestration(version_id, ws_callback)
    
    print(f"\n✅ Result: {result}")


if __name__ == "__main__":
    asyncio.run(demo())

