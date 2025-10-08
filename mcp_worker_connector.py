#!/usr/bin/env python3
"""
mcp_worker_connector.py - MCP Worker Connection & Monitoring

Spawns worker processes (Codex, Cursor, Factory's Droid) with MCP servers
and monitors their activity in real-time through log files and websockets.

Architecture:
    Orchestrator → WorkerMCPConnection → Spawned MCP Process
                                       ↓
                                   Log Monitor (async file watcher)
                                       ↓
                                   WebSocket → Dashboard UI

Supports:
- Codex: ~/.codex/log/codex-tui.log
- Cursor: ~/.cursor/logs/main.log (if available)  
- Factory Droid: droid process with custom log output

Version: 1.0.0 (Phase 3 - Worker Execution)
"""

import asyncio
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, AsyncIterator, Callable
from enum import Enum
import aiofiles
import websockets
# Note: watchdog is optional - we use asyncio file monitoring instead
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# ============================================================================
# WORKER CONNECTION TYPES
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
    log_path: Optional[str] = None
    max_concurrent_tasks: int = 1
    enabled: bool = True

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
# LOG MONITOR (Async File Watcher)
# ============================================================================

class AsyncLogMonitor:
    """
    Asynchronously monitors log files for changes
    Parses activity and streams to websocket
    """
    
    def __init__(
        self,
        log_path: Path,
        worker_id: str,
        callback: Callable[[WorkerActivity], None]
    ):
        self.log_path = log_path
        self.worker_id = worker_id
        self.callback = callback
        self.last_position = 0
        self.running = False
    
    async def start(self):
        """Start monitoring log file"""
        self.running = True
        
        # Create log file if doesn't exist
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()
        
        # Get initial position
        self.last_position = self.log_path.stat().st_size
        
        # Monitor loop
        while self.running:
            await self._check_for_changes()
            await asyncio.sleep(0.1)  # Check every 100ms
    
    async def _check_for_changes(self):
        """Check if log file has new content"""
        try:
            current_size = self.log_path.stat().st_size
            
            if current_size > self.last_position:
                async with aiofiles.open(self.log_path, 'r') as f:
                    await f.seek(self.last_position)
                    new_content = await f.read()
                    self.last_position = current_size
                    
                    # Parse new content
                    await self._parse_and_emit(new_content)
        
        except Exception as e:
            print(f"Error monitoring log: {e}")
    
    async def _parse_and_emit(self, content: str):
        """Parse log content and emit activities"""
        for line in content.strip().split('\n'):
            if not line:
                continue
            
            activity = self._parse_line(line)
            if activity:
                await self.callback(activity)
    
    def _parse_line(self, line: str) -> Optional[WorkerActivity]:
        """
        Parse log line into WorkerActivity
        
        Supported formats:
        - Codex: [timestamp] TOOL: tool_name - description
        - Codex: [timestamp] REASONING: thinking about X
        - Codex: [timestamp] CODING: editing file.py
        - Generic: [timestamp] TYPE: description
        """
        try:
            # Try to parse structured log
            if '[' in line and ']' in line:
                timestamp_end = line.index(']')
                timestamp = line[1:timestamp_end]
                rest = line[timestamp_end+1:].strip()
                
                # Parse activity type
                if ':' in rest:
                    activity_type, description = rest.split(':', 1)
                    activity_type = activity_type.strip().lower()
                    description = description.strip()
                    
                    # Extract tool name if tool_use
                    tool_name = None
                    if activity_type == 'tool':
                        if '-' in description:
                            tool_name, description = description.split('-', 1)
                            tool_name = tool_name.strip()
                            description = description.strip()
                    
                    # Extract file path if present
                    file_path = None
                    if 'file:' in description.lower():
                        # Extract file path from description
                        for word in description.split():
                            if '/' in word or '.' in word:
                                file_path = word.strip('.,;:')
                                break
                    
                    return WorkerActivity(
                        worker_id=self.worker_id,
                        timestamp=timestamp,
                        activity_type=activity_type,
                        tool_name=tool_name,
                        description=description,
                        file_path=file_path
                    )
            
            # Fallback: generic activity
            return WorkerActivity(
                worker_id=self.worker_id,
                timestamp=datetime.now().isoformat(),
                activity_type='unknown',
                description=line[:100]  # Truncate
            )
        
        except Exception as e:
            return None
    
    def stop(self):
        """Stop monitoring"""
        self.running = False

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
# MCP WORKER CONNECTION
# ============================================================================

class WorkerMCPConnection:
    """
    Manages MCP worker process lifecycle
    Spawns process, monitors logs, streams to WebSocket
    """
    
    def __init__(
        self,
        config: MCPWorkerConfig,
        websocket_broadcaster: WebSocketBroadcaster
    ):
        self.config = config
        self.broadcaster = websocket_broadcaster
        self.process: Optional[subprocess.Popen] = None
        self.log_monitor: Optional[AsyncLogMonitor] = None
        self.metrics = WorkerMetrics(worker_id=config.worker_id)
        self.start_time: Optional[float] = None
    
    async def start(self):
        """Start MCP worker process"""
        print(f"🚀 Starting worker: {self.config.worker_id} ({self.config.worker_type.value})")
        
        # Prepare environment
        env = os.environ.copy()
        env.update(self.config.env)
        
        # Expand env vars in command args
        args = [
            os.path.expandvars(arg)
            for arg in self.config.args
        ]
        
        # Spawn MCP server process
        try:
            # Special handling for Codex
            if self.config.worker_type == MCPWorkerType.CODEX:
                # Codex with mcp-server parameter
                cmd = ["codex", "--mcp-server"] + args
                self.process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Monitor Codex log
                log_path = Path.home() / ".codex/log/codex-tui.log"
                self.log_monitor = AsyncLogMonitor(
                    log_path,
                    self.config.worker_id,
                    self._on_activity
                )
            
            # Cursor (if available)
            elif self.config.worker_type == MCPWorkerType.CURSOR:
                cmd = ["cursor", "--mcp"] + args
                self.process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                log_path = Path.home() / ".cursor/logs/main.log"
                self.log_monitor = AsyncLogMonitor(
                    log_path,
                    self.config.worker_id,
                    self._on_activity
                )
            
            # Factory's Droid
            elif self.config.worker_type == MCPWorkerType.DROID:
                cmd = ["droid", "--mcp-mode"] + args
                self.process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                log_path = Path.home() / ".droid/activity.log"
                self.log_monitor = AsyncLogMonitor(
                    log_path,
                    self.config.worker_id,
                    self._on_activity
                )
            
            # Generic MCP worker (Claude, GPT-4)
            else:
                cmd = [self.config.command] + args
                self.process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Use custom log path if provided
                if self.config.log_path:
                    log_path = Path(self.config.log_path)
                    self.log_monitor = AsyncLogMonitor(
                        log_path,
                        self.config.worker_id,
                        self._on_activity
                    )
            
            self.start_time = asyncio.get_event_loop().time()
            
            # Start log monitoring
            if self.log_monitor:
                asyncio.create_task(self.log_monitor.start())
            
            print(f"✓ Worker {self.config.worker_id} started (PID: {self.process.pid})")
            
            # Monitor stdout/stderr in background
            asyncio.create_task(self._monitor_stdout())
            asyncio.create_task(self._monitor_stderr())
        
        except Exception as e:
            error = f"Failed to start worker: {e}"
            print(f"✗ {error}")
            await self.broadcaster.broadcast_error(self.config.worker_id, error)
            raise
    
    async def _monitor_stdout(self):
        """Monitor worker stdout"""
        if not self.process or not self.process.stdout:
            return
        
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            
            # Parse MCP messages from stdout
            try:
                msg = json.loads(line.decode())
                await self._handle_mcp_message(msg)
            except:
                # Not JSON, treat as log
                activity = WorkerActivity(
                    worker_id=self.config.worker_id,
                    timestamp=datetime.now().isoformat(),
                    activity_type='stdout',
                    description=line.decode().strip()
                )
                await self._on_activity(activity)
    
    async def _monitor_stderr(self):
        """Monitor worker stderr"""
        if not self.process or not self.process.stderr:
            return
        
        while True:
            line = self.process.stderr.readline()
            if not line:
                break
            
            error = line.decode().strip()
            await self.broadcaster.broadcast_error(self.config.worker_id, error)
    
    async def _handle_mcp_message(self, msg: Dict):
        """Handle MCP protocol message"""
        msg_type = msg.get('type')
        
        if msg_type == 'tool_use':
            tool_name = msg.get('tool')
            self.metrics.tools_used[tool_name] = self.metrics.tools_used.get(tool_name, 0) + 1
            
            activity = WorkerActivity(
                worker_id=self.config.worker_id,
                timestamp=datetime.now().isoformat(),
                activity_type='tool_use',
                tool_name=tool_name,
                description=msg.get('description', ''),
                file_path=msg.get('file')
            )
            await self._on_activity(activity)
        
        elif msg_type == 'file_edit':
            file_path = msg.get('file')
            if file_path not in self.metrics.files_modified:
                self.metrics.files_modified.append(file_path)
            
            activity = WorkerActivity(
                worker_id=self.config.worker_id,
                timestamp=datetime.now().isoformat(),
                activity_type='coding',
                description=f"Editing {file_path}",
                file_path=file_path
            )
            await self._on_activity(activity)
    
    async def _on_activity(self, activity: WorkerActivity):
        """Handle new activity from worker"""
        # Update metrics
        self.metrics.uptime_seconds = (
            asyncio.get_event_loop().time() - self.start_time
            if self.start_time else 0
        )
        
        # Broadcast to WebSocket
        await self.broadcaster.broadcast_activity(activity)
        
        # Periodically broadcast metrics
        if len(self.metrics.tools_used) % 10 == 0:  # Every 10 tool uses
            await self.broadcaster.broadcast_metrics(self.metrics)
    
    async def send_task(self, task: Dict):
        """Send task to worker via MCP"""
        if not self.process:
            raise RuntimeError("Worker not started")
        
        # Send task as MCP message
        msg = json.dumps({
            'type': 'execute_task',
            'task': task
        }) + '\n'
        
        self.process.stdin.write(msg.encode())
        self.process.stdin.flush()
    
    async def stop(self):
        """Stop worker process"""
        if self.log_monitor:
            self.log_monitor.stop()
        
        if self.process:
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
    Manages pool of MCP workers
    Distributes tasks, monitors activity, streams to WebSocket
    """
    
    def __init__(
        self,
        team_config: Dict,
        websocket_broadcaster: WebSocketBroadcaster
    ):
        self.team_config = team_config
        self.broadcaster = websocket_broadcaster
        self.workers: Dict[str, WorkerMCPConnection] = {}
    
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
                log_path=mcp_cfg.get('log_path'),
                max_concurrent_tasks=worker_cfg.get('max_concurrent_tasks', 1),
                enabled=worker_cfg.get('enabled', True)
            )
            
            # Create and start connection
            connection = WorkerMCPConnection(config, self.broadcaster)
            await connection.start()
            
            self.workers[config.worker_id] = connection
    
    async def dispatch_task(self, worker_id: str, task: Dict):
        """Dispatch task to specific worker"""
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found")
        
        await self.workers[worker_id].send_task(task)
    
    async def stop_all(self):
        """Stop all workers"""
        for worker in self.workers.values():
            await worker.stop()

# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo MCP worker monitoring"""
    print("🧪 MCP Worker Connector Demo")
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
    
    print("\n🌐 WebSocket running on ws://localhost:8765")
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

