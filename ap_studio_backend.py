#!/usr/bin/env python3
"""
ap_studio_backend.py - AP Studio FastAPI Backend

FastAPI backend with:
- REST API for CRUD operations
- WebSocket for real-time brainstorming & orchestration
- Brainstorm Helper Agent integration
- Worker management
- Version management with Git

Version: 1.0.0
Date: October 9, 2025
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Local imports
from ap_studio_db import APStudioDB
from brainstorm_agent import BrainstormHelperAgent
from version_manager import VersionManager
from orchestration_launcher import OrchestrationLauncher


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ProjectCreate(BaseModel):
    name: str
    description: str = ""

class VersionCreate(BaseModel):
    project_id: int
    version: str

class BrainstormMessage(BaseModel):
    session_id: int
    message: str

class WorkerAdd(BaseModel):
    worker_id: str
    agent_type: str
    capabilities: List[str]
    mcp_config: Dict[str, Any]
    max_concurrent: int = 1

class OrchestrationStart(BaseModel):
    version_id: int


# ============================================================================
# WEBSOCKET MANAGER
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            'brainstorm': [],
            'orchestration': [],
            'workers': []
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept connection"""
        await websocket.accept()
        self.active_connections[channel].append(websocket)
        print(f"✓ WebSocket connected to {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove connection"""
        if websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
            print(f"✗ WebSocket disconnected from {channel}")
    
    async def broadcast(self, message: Dict, channel: str):
        """Broadcast message to all connections in channel"""
        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected
        for conn in disconnected:
            self.disconnect(conn, channel)
    
    async def send_personal(self, message: Dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass


# ============================================================================
# LIFESPAN CONTEXT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    print("🚀 AP Studio Backend starting...")
    
    # Initialize database
    app.state.db = APStudioDB("ap_studio.db")
    print("✓ Database initialized")
    
    # Initialize version manager
    app.state.version_manager = VersionManager()
    print("✓ Version manager initialized")
    
    # Initialize brainstorm agent
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        app.state.brainstorm_agent = BrainstormHelperAgent(api_key=api_key)
        print("✓ Brainstorm agent initialized")
    else:
        print("⚠️  OPENAI_API_KEY not set - brainstorming will be limited")
        app.state.brainstorm_agent = None
    
    # Initialize WebSocket manager
    app.state.ws_manager = ConnectionManager()
    print("✓ WebSocket manager initialized")
    
    # Initialize orchestration launcher
    app.state.orchestration_launcher = OrchestrationLauncher(app.state.db)
    print("✓ Orchestration launcher initialized")
    
    yield
    
    # Shutdown
    print("🛑 AP Studio Backend shutting down...")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="AP Studio API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST API ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AP Studio API",
        "version": "1.0.0",
        "status": "running"
    }


# ----------------------------------------------------------------------------
# PROJECTS
# ----------------------------------------------------------------------------

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    projects = app.state.db.list_projects()
    return {"projects": projects}


@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """Create new project"""
    try:
        project_id = app.state.db.create_project(
            name=project.name,
            description=project.description
        )
        return {
            "success": True,
            "project_id": project_id,
            "project": app.state.db.get_project(project_id)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Get project by ID"""
    project = app.state.db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Include versions
    versions = app.state.db.list_versions(project_id)
    project['versions'] = versions
    
    return {"project": project}


# ----------------------------------------------------------------------------
# VERSIONS
# ----------------------------------------------------------------------------

@app.get("/api/versions/{version_id}")
async def get_version(version_id: int):
    """Get version details"""
    version = app.state.db.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"version": version}


@app.get("/api/versions/{version_id}/prd")
async def get_version_prd(version_id: int):
    """Get PRD content for version"""
    version = app.state.db.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {
        "prd_content": version['prd_content'],
        "version": version['version']
    }


# ----------------------------------------------------------------------------
# WORKERS
# ----------------------------------------------------------------------------

@app.get("/api/workers")
async def list_workers():
    """List all workers"""
    workers = app.state.db.list_workers()
    return {"workers": workers}


@app.post("/api/workers")
async def add_worker(worker: WorkerAdd):
    """Add new worker"""
    try:
        worker_id = app.state.db.add_worker(
            worker_id=worker.worker_id,
            agent_type=worker.agent_type,
            capabilities=worker.capabilities,
            mcp_config=worker.mcp_config,
            max_concurrent=worker.max_concurrent
        )
        
        # Broadcast worker added
        await app.state.ws_manager.broadcast({
            'type': 'worker_added',
            'worker': app.state.db.get_worker(worker.worker_id)
        }, 'workers')
        
        return {"success": True, "worker_id": worker_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/workers/{worker_id}")
async def get_worker(worker_id: str):
    """Get worker details"""
    worker = app.state.db.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"worker": worker}


# ----------------------------------------------------------------------------
# ORCHESTRATIONS
# ----------------------------------------------------------------------------

@app.get("/api/orchestrations/active")
async def get_active_orchestrations():
    """Get active orchestrations"""
    orchestrations = app.state.db.get_active_orchestrations()
    return {"orchestrations": orchestrations}


# ============================================================================
# WEBSOCKET ROUTES
# ============================================================================

@app.websocket("/ws/brainstorm")
async def websocket_brainstorm(websocket: WebSocket):
    """
    WebSocket for brainstorming sessions
    
    Messages:
    - client → server: {"type": "start", "project_name": "..."}
    - client → server: {"type": "message", "session_id": 123, "content": "..."}
    - client → server: {"type": "save_prd", "session_id": 123}
    - server → client: {"type": "response", "content": "...", "prd_content": "..."}
    """
    await app.state.ws_manager.connect(websocket, 'brainstorm')
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')
            
            if msg_type == 'start':
                # Start new brainstorm session
                project_name = data.get('project_name')
                
                # Create project if not exists
                project = app.state.db.get_project_by_name(project_name)
                if not project:
                    project_id = app.state.db.create_project(project_name)
                    project = app.state.db.get_project(project_id)
                
                # Create version
                versions = app.state.db.list_versions(project['id'])
                next_version = f"0.{len(versions) + 1:02d}"
                
                version_path = f"projects/{project_name}/v{next_version}"
                version_id = app.state.db.create_version(
                    project_id=project['id'],
                    version=next_version,
                    path=version_path
                )
                
                # Create brainstorm session
                session_id = app.state.db.create_brainstorm_session(version_id)
                
                # Get initial message from agent
                if app.state.brainstorm_agent:
                    initial_msg = await app.state.brainstorm_agent.start_session(project_name)
                else:
                    initial_msg = f"Ahoj! Začnime prácu na projekte {project_name}. Aký je cieľ projektu?"
                
                # Save assistant message
                app.state.db.add_brainstorm_message(session_id, 'assistant', initial_msg)
                
                # Send response
                await app.state.ws_manager.send_personal({
                    'type': 'session_started',
                    'session_id': session_id,
                    'version_id': version_id,
                    'project_id': project['id'],
                    'version': next_version,
                    'message': initial_msg,
                    'prd_content': ''
                }, websocket)
            
            elif msg_type == 'message':
                # Process user message
                session_id = data.get('session_id')
                user_message = data.get('content')
                
                # Save user message
                app.state.db.add_brainstorm_message(session_id, 'user', user_message)
                
                # Get session & version
                session = app.state.db.get_brainstorm_session(session_id)
                version = app.state.db.get_version(session['version_id'])
                current_prd = version['prd_content'] or ""
                
                # Get agent response
                if app.state.brainstorm_agent:
                    response, updated_prd = await app.state.brainstorm_agent.process_message(
                        user_message,
                        current_prd
                    )
                else:
                    response = f"Rozumiem: {user_message}. (Brainstorm agent not available)"
                    updated_prd = current_prd + f"\n\n## User Input\n{user_message}"
                
                # Save assistant message
                app.state.db.add_brainstorm_message(session_id, 'assistant', response)
                
                # Update PRD
                app.state.db.update_version_prd(session['version_id'], updated_prd)
                
                # Send response
                await app.state.ws_manager.send_personal({
                    'type': 'response',
                    'message': response,
                    'prd_content': updated_prd
                }, websocket)
            
            elif msg_type == 'save_prd':
                # Save PRD manually
                session_id = data.get('session_id')
                prd_content = data.get('prd_content')
                
                session = app.state.db.get_brainstorm_session(session_id)
                app.state.db.update_version_prd(session['version_id'], prd_content)
                
                await app.state.ws_manager.send_personal({
                    'type': 'prd_saved',
                    'success': True
                }, websocket)
    
    except WebSocketDisconnect:
        app.state.ws_manager.disconnect(websocket, 'brainstorm')
    except Exception as e:
        print(f"WebSocket error: {e}")
        app.state.ws_manager.disconnect(websocket, 'brainstorm')


@app.websocket("/ws/orchestration")
async def websocket_orchestration(websocket: WebSocket):
    """
    WebSocket for orchestration monitoring
    
    Messages:
    - client → server: {"type": "start", "version_id": 123}
    - server → client: Streaming orchestration updates
    """
    await app.state.ws_manager.connect(websocket, 'orchestration')
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')
            
            if msg_type == 'start':
                version_id = data.get('version_id')
                
                # WebSocket callback for streaming updates
                async def ws_callback(message):
                    await app.state.ws_manager.send_personal(message, websocket)
                
                # Start orchestration (async task)
                asyncio.create_task(
                    app.state.orchestration_launcher.start_orchestration(
                        version_id,
                        ws_callback
                    )
                )
    
    except WebSocketDisconnect:
        app.state.ws_manager.disconnect(websocket, 'orchestration')
    except Exception as e:
        print(f"WebSocket error: {e}")
        app.state.ws_manager.disconnect(websocket, 'orchestration')


@app.websocket("/ws/workers")
async def websocket_workers(websocket: WebSocket):
    """
    WebSocket for worker monitoring (reuse existing pattern from dashboard.html)
    """
    await app.state.ws_manager.connect(websocket, 'workers')
    
    try:
        # Send initial worker list
        workers = app.state.db.list_workers(enabled_only=True)
        await app.state.ws_manager.send_personal({
            'type': 'worker_list',
            'workers': workers
        }, websocket)
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        app.state.ws_manager.disconnect(websocket, 'workers')


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🌲 AP Studio Backend 🌲                        ║
║                                                              ║
║  FastAPI + WebSocket + Brainstorm Agent                     ║
║  Version: 1.0.0                                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

