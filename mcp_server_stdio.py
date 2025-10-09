#!/usr/bin/env python3
"""
mcp_server_stdio.py - MCP Server with Stdio Communication

Refactored to use MCPServerStdio pattern like OpenAI Codex Agents SDK.
Direct communication via stdin/stdout instead of log file monitoring.

Architecture:
    Orchestrator → MCPServerStdio → Worker Process (stdin/stdout)
                                  ↓
                              MCP Protocol Messages (JSON)
                                  ↓
                              WebSocket → Dashboard UI

Based on: https://developers.openai.com/codex/guides/agents-sdk/

Version: 2.0.0 (Phase 3 - Refactored with MCPServerStdio)
"""

import asyncio
import json
import os
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from enum import Enum
import websockets

# ============================================================================
# MCP PROTOCOL - Message Types
# ============================================================================

class MCPMessageType(Enum):
    """MCP Protocol message types"""
    # Client → Server
    INITIALIZE = "initialize"
    EXECUTE_TASK = "execute_task"
    CANCEL_TASK = "cancel_task"
    SHUTDOWN = "shutdown"
    LIST_TOOLS = "list_tools"  # NEW: Request list of available tools
    
    # Server → Client
    INITIALIZED = "initialized"
    TASK_STARTED = "task_started"
    TOOL_USE = "tool_use"
    PROGRESS = "progress"
    TASK_COMPLETE = "task_complete"
    TASK_ERROR = "task_error"
    LOG = "log"
    TOOLS_RESPONSE = "tools_response"  # NEW: Response with available tools

@dataclass
class MCPMessage:
    """MCP Protocol message"""
    type: str
    id: str
    timestamp: str
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        return json.dumps({
            'type': self.type,
            'id': self.id,
            'timestamp': self.timestamp,
            'payload': self.payload
        })
    
    @classmethod
    def from_json(cls, data: str) -> 'MCPMessage':
        obj = json.loads(data)
        return cls(
            type=obj['type'],
            id=obj['id'],
            timestamp=obj['timestamp'],
            payload=obj['payload']
        )

# ============================================================================
# WORKER DATA STRUCTURES
# ============================================================================

class MCPWorkerType(Enum):
    """Types of MCP workers"""
    CODEX = "codex"
    CURSOR = "cursor"
    CLAUDE = "claude"
    GPT4 = "gpt4"
    DROID = "droid"

@dataclass
class MCPWorkerConfig:
    """Configuration for MCP worker"""
    worker_id: str
    worker_type: MCPWorkerType
    command: str
    args: List[str]
    env: Dict[str, str]
    max_concurrent_tasks: int = 1
    enabled: bool = True

@dataclass
class MCPTool:
    """Description of an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Optional[str] = None
    examples: List[str] = field(default_factory=list)

@dataclass
class WorkerActivity:
    """Real-time worker activity"""
    worker_id: str
    timestamp: str
    activity_type: str  # "tool_use", "reasoning", "coding", "testing"
    tool_name: Optional[str] = None
    description: str = ""
    file_path: Optional[str] = None
    progress: Optional[int] = None

@dataclass
class WorkerMetrics:
    """Worker performance metrics"""
    worker_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    tools_used: Dict[str, int] = field(default_factory=dict)
    files_modified: List[str] = field(default_factory=list)
    avg_task_duration: float = 0.0
    uptime_seconds: float = 0.0

# ============================================================================
# WEBSOCKET BROADCASTER
# ============================================================================

class WebSocketBroadcaster:
    """
    Broadcasts worker activities to connected UI clients via WebSocket
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: set = set()
        self.server = None
    
    async def start(self):
        """Start WebSocket server"""
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )
        print(f"🌐 WebSocket server started on ws://{self.host}:{self.port}")
    
    async def _handle_client(self, websocket, path):
        """Handle new client connection"""
        self.clients.add(websocket)
        print(f"📱 Client connected: {websocket.remote_address}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'message': 'Connected to AP Orchestrator',
                'timestamp': datetime.now().isoformat()
            }))
            
            # Keep connection alive
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"📱 Client disconnected: {websocket.remote_address}")
    
    async def broadcast_activity(self, activity: WorkerActivity):
        """Broadcast activity to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps({
            'type': 'worker_activity',
            'worker_id': activity.worker_id,
            'timestamp': activity.timestamp,
            'activity_type': activity.activity_type,
            'tool_name': activity.tool_name,
            'description': activity.description,
            'file_path': activity.file_path,
            'progress': activity.progress
        })
        
        # Broadcast to all clients
        websockets.broadcast(self.clients, message)
    
    async def broadcast_metrics(self, metrics: WorkerMetrics):
        """Broadcast worker metrics to dashboard"""
        if not self.clients:
            return
        
        message = json.dumps({
            'type': 'worker_metrics',
            'worker_id': metrics.worker_id,
            'tasks_completed': metrics.tasks_completed,
            'tasks_failed': metrics.tasks_failed,
            'tools_used': metrics.tools_used,
            'files_modified': metrics.files_modified,
            'avg_task_duration': metrics.avg_task_duration,
            'uptime_seconds': metrics.uptime_seconds
        })
        
        websockets.broadcast(self.clients, message)
    
    async def broadcast_error(self, worker_id: str, error: str):
        """Broadcast error from worker"""
        message = json.dumps({
            'type': 'worker_error',
            'worker_id': worker_id,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
        websockets.broadcast(self.clients, message)
    
    async def stop(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

# ============================================================================
# MCP SERVER STDIO - Core Implementation
# ============================================================================

class MCPServerStdio:
    """
    MCP Server with stdio communication
    
    Communicates with worker processes via stdin/stdout using MCP protocol.
    Based on OpenAI Codex Agents SDK pattern.
    """
    
    def __init__(
        self,
        config: MCPWorkerConfig,
        broadcaster: WebSocketBroadcaster
    ):
        self.config = config
        self.broadcaster = broadcaster
        self.process: Optional[subprocess.Popen] = None
        self.metrics = WorkerMetrics(worker_id=config.worker_id)
        self.start_time: Optional[float] = None
        self.running = False
        
        # Task tracking
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.message_id_counter = 0
    
    async def start(self):
        """Start MCP worker process with stdio communication"""
        print(f"🚀 Starting worker: {self.config.worker_id} ({self.config.worker_type.value})")
        
        # Prepare environment
        env = os.environ.copy()
        env.update(self.config.env)
        
        # Expand env vars in command args
        args = [os.path.expandvars(arg) for arg in self.config.args]
        
        try:
            # Spawn MCP server process with stdio pipes
            cmd = [self.config.command] + args
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1  # Line buffered
            )
            
            self.start_time = asyncio.get_event_loop().time()
            self.running = True
            
            # Start message handlers
            asyncio.create_task(self._read_stdout())
            asyncio.create_task(self._read_stderr())
            
            # Send initialization message
            await self._send_message(MCPMessageType.INITIALIZE, {
                'worker_id': self.config.worker_id,
                'worker_type': self.config.worker_type.value,
                'capabilities': self.config.max_concurrent_tasks
            })
            
            print(f"✓ Worker {self.config.worker_id} started (PID: {self.process.pid})")
        
        except Exception as e:
            error = f"Failed to start worker: {e}"
            print(f"✗ {error}")
            await self.broadcaster.broadcast_error(self.config.worker_id, error)
            raise
    
    async def _send_message(self, msg_type: MCPMessageType, payload: Dict):
        """Send MCP message to worker via stdin"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Worker process not started")
        
        self.message_id_counter += 1
        message = MCPMessage(
            type=msg_type.value,
            id=f"{self.config.worker_id}_{self.message_id_counter}",
            timestamp=datetime.now().isoformat(),
            payload=payload
        )
        
        # Write to stdin
        json_msg = message.to_json() + '\n'
        self.process.stdin.write(json_msg)
        self.process.stdin.flush()
    
    async def _read_stdout(self):
        """Read MCP messages from worker stdout"""
        if not self.process or not self.process.stdout:
            return
        
        while self.running:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                # Parse MCP message
                message = MCPMessage.from_json(line.strip())
                await self._handle_message(message)
            
            except json.JSONDecodeError as e:
                # Not a valid MCP message, treat as log
                activity = WorkerActivity(
                    worker_id=self.config.worker_id,
                    timestamp=datetime.now().isoformat(),
                    activity_type='log',
                    description=line.strip()
                )
                await self._on_activity(activity)
            
            except Exception as e:
                print(f"Error reading stdout: {e}")
                break
    
    async def _read_stderr(self):
        """Read errors from worker stderr"""
        if not self.process or not self.process.stderr:
            return
        
        while self.running:
            try:
                line = self.process.stderr.readline()
                if not line:
                    break
                
                error = line.strip()
                await self.broadcaster.broadcast_error(self.config.worker_id, error)
            
            except Exception as e:
                print(f"Error reading stderr: {e}")
                break
    
    async def _handle_message(self, message: MCPMessage):
        """Handle MCP message from worker"""
        msg_type = message.type
        payload = message.payload
        
        if msg_type == MCPMessageType.INITIALIZED.value:
            print(f"✓ Worker {self.config.worker_id} initialized")
        
        elif msg_type == MCPMessageType.TASK_STARTED.value:
            task_id = payload.get('task_id')
            print(f"→ Worker {self.config.worker_id} started task {task_id}")
        
        elif msg_type == MCPMessageType.TOOL_USE.value:
            tool_name = payload.get('tool')
            self.metrics.tools_used[tool_name] = self.metrics.tools_used.get(tool_name, 0) + 1
            
            activity = WorkerActivity(
                worker_id=self.config.worker_id,
                timestamp=message.timestamp,
                activity_type='tool_use',
                tool_name=tool_name,
                description=payload.get('description', ''),
                file_path=payload.get('file')
            )
            await self._on_activity(activity)
        
        elif msg_type == MCPMessageType.PROGRESS.value:
            progress = payload.get('progress', 0)
            activity = WorkerActivity(
                worker_id=self.config.worker_id,
                timestamp=message.timestamp,
                activity_type='progress',
                description=payload.get('message', ''),
                progress=progress
            )
            await self._on_activity(activity)
        
        elif msg_type == MCPMessageType.TASK_COMPLETE.value:
            task_id = payload.get('task_id')
            self.metrics.tasks_completed += 1
            
            files = payload.get('files_modified', [])
            for file in files:
                if file not in self.metrics.files_modified:
                    self.metrics.files_modified.append(file)
            
            print(f"✓ Worker {self.config.worker_id} completed task {task_id}")
        
        elif msg_type == MCPMessageType.TASK_ERROR.value:
            task_id = payload.get('task_id')
            error = payload.get('error', 'Unknown error')
            self.metrics.tasks_failed += 1
            
            await self.broadcaster.broadcast_error(
                self.config.worker_id,
                f"Task {task_id} failed: {error}"
            )
        
        elif msg_type == MCPMessageType.LOG.value:
            log_type = payload.get('level', 'info')
            message_text = payload.get('message', '')
            
            activity_type = {
                'debug': 'log',
                'info': 'log',
                'warning': 'warning',
                'error': 'error'
            }.get(log_type, 'log')
            
            activity = WorkerActivity(
                worker_id=self.config.worker_id,
                timestamp=message.timestamp,
                activity_type=activity_type,
                description=message_text
            )
            await self._on_activity(activity)
        
        elif msg_type == MCPMessageType.TOOLS_RESPONSE.value:
            # Handle TOOLS_RESPONSE from worker
            request_id = payload.get('request_id')
            tools_data = payload.get('tools', [])
            
            # Find pending request and resolve future
            if hasattr(self, '_pending_requests') and request_id in self._pending_requests:
                future = self._pending_requests[request_id]
                if not future.done():
                    future.set_result(tools_data)
                    print(f"✓ Worker {self.config.worker_id} listed {len(tools_data)} tools")
    
    async def _on_activity(self, activity: WorkerActivity):
        """Handle new activity from worker"""
        # Update metrics
        if self.start_time:
            self.metrics.uptime_seconds = (
                asyncio.get_event_loop().time() - self.start_time
            )
        
        # Broadcast to WebSocket
        await self.broadcaster.broadcast_activity(activity)
        
        # Periodically broadcast metrics
        if len(self.metrics.tools_used) % 10 == 0 and len(self.metrics.tools_used) > 0:
            await self.broadcaster.broadcast_metrics(self.metrics)
    
    async def execute_task(self, task: Dict) -> Dict:
        """
        Execute task on worker
        
        Returns:
            Dict with result: {'success': bool, 'files_modified': List[str], 'error': Optional[str]}
        """
        task_id = task.get('task_id', f"task_{self.message_id_counter}")
        
        # Send execute task message
        await self._send_message(MCPMessageType.EXECUTE_TASK, {
            'task_id': task_id,
            'task': task
        })
        
        # Wait for completion (simplified - in real implementation,
        # this would wait for TASK_COMPLETE message)
        # For now, simulate by waiting
        await asyncio.sleep(5)
        
        return {
            'success': True,
            'task_id': task_id,
            'files_modified': task.get('scope_touch', []),
            'worker_id': self.config.worker_id
        }
    
    async def list_tools(self, timeout: float = 10.0) -> List[MCPTool]:
        """
        Request list of available tools from worker
        
        Returns:
            List of MCPTool objects describing available tools
        
        Raises:
            TimeoutError: If worker doesn't respond within timeout
        """
        # Create future for response
        response_future = asyncio.Future()
        request_id = f"list_tools_{self.message_id_counter}"
        
        # Store future for response handler
        if not hasattr(self, '_pending_requests'):
            self._pending_requests = {}
        self._pending_requests[request_id] = response_future
        
        # Send LIST_TOOLS request
        await self._send_message(MCPMessageType.LIST_TOOLS, {
            'request_id': request_id
        })
        
        try:
            # Wait for TOOLS_RESPONSE
            tools_data = await asyncio.wait_for(response_future, timeout=timeout)
            
            # Parse into MCPTool objects
            tools = []
            for tool_data in tools_data:
                tools.append(MCPTool(
                    name=tool_data.get('name', 'unknown'),
                    description=tool_data.get('description', ''),
                    parameters=tool_data.get('parameters', {}),
                    returns=tool_data.get('returns'),
                    examples=tool_data.get('examples', [])
                ))
            
            return tools
        
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Worker {self.config.worker_id} didn't respond to LIST_TOOLS within {timeout}s"
            )
        finally:
            # Clean up pending request
            self._pending_requests.pop(request_id, None)
    
    async def stop(self):
        """Stop worker process"""
        self.running = False
        
        if self.process:
            # Send shutdown message
            try:
                await self._send_message(MCPMessageType.SHUTDOWN, {})
                await asyncio.sleep(0.5)  # Give time to shutdown gracefully
            except:
                pass
            
            # Terminate process
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        print(f"✓ Worker {self.config.worker_id} stopped")

# ============================================================================
# WORKER POOL MANAGER
# ============================================================================

class WorkerPoolManager:
    """
    Manages pool of MCP workers using stdio communication
    """
    
    def __init__(
        self,
        team_config: Dict,
        websocket_broadcaster: WebSocketBroadcaster
    ):
        self.team_config = team_config
        self.broadcaster = websocket_broadcaster
        self.workers: Dict[str, MCPServerStdio] = {}
    
    async def start_workers(self):
        """Start all enabled workers from team.json"""
        for worker_cfg in self.team_config.get('workers', []):
            if not worker_cfg.get('enabled', True):
                continue
            
            # Create MCP config
            mcp_cfg = worker_cfg.get('mcp_config', {})
            config = MCPWorkerConfig(
                worker_id=worker_cfg['id'],
                worker_type=MCPWorkerType(worker_cfg['agent_type']),
                command=mcp_cfg.get('command', 'python'),
                args=mcp_cfg.get('args', []),
                env=mcp_cfg.get('env', {}),
                max_concurrent_tasks=worker_cfg.get('max_concurrent_tasks', 1),
                enabled=worker_cfg.get('enabled', True)
            )
            
            # Create and start MCP server
            try:
                server = MCPServerStdio(config, self.broadcaster)
                await server.start()
                self.workers[config.worker_id] = server
            except Exception as e:
                print(f"✗ Failed to start worker {config.worker_id}: {e}")
    
    async def dispatch_task(self, worker_id: str, task: Dict) -> Dict:
        """Dispatch task to specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")
        
        return await self.workers[worker_id].execute_task(task)
    
    async def stop_all(self):
        """Stop all workers"""
        for worker in self.workers.values():
            await worker.stop()

# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo MCPServerStdio"""
    print("🧪 MCPServerStdio Demo")
    print("=" * 60)
    print("Using OpenAI Codex Agents SDK pattern")
    print("=" * 60)
    
    # Start WebSocket broadcaster
    broadcaster = WebSocketBroadcaster()
    await broadcaster.start()
    
    # Load team config
    with open('team.json') as f:
        team_config = json.load(f)
    
    # Create worker pool
    pool = WorkerPoolManager(team_config, broadcaster)
    
    # Start workers
    await pool.start_workers()
    
    if not pool.workers:
        print("\n⚠️  No workers available (all disabled in team.json)")
        print("    This is expected - the system gracefully handles no workers.")
        print("\n✓ MCPServerStdio refactoring complete!")
        print("\n📚 To enable workers:")
        print("   1. Set 'enabled': true in team.json")
        print("   2. Install MCP tools (npx, python workers)")
        print("   3. Run orchestrator_enhanced.py")
        await broadcaster.stop()
        return
    
    print(f"\n🌐 WebSocket running on ws://localhost:8765")
    print("📊 Open dashboard to see worker activity")
    print("\nPress Ctrl+C to stop...\n")
    
    try:
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        await pool.stop_all()
        await broadcaster.stop()

if __name__ == "__main__":
    asyncio.run(demo())
