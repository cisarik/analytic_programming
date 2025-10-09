#!/usr/bin/env python3
"""
brainstorm_agent_mcp.py - MCP-Enhanced Brainstorm Agent

Interactive PRD.md editor with real-time UI updates:
- Uses mcp-use for robust tool calling
- Direct PRD.md line manipulation
- WebSocket communication with UI
- Green highlight for changes with undo capability

Version: 2.0.0 (MCP Edition)
Date: October 9, 2025

TODO:
- [ ] Add context file loading (AGENTS.md, README.md) on session start
- [ ] Implement batch undo (undo all changes from last message)
- [ ] Add approval mode (require user confirmation for each change)
- [ ] Support for updating TODOs.md, BUGs.md, FEATURES.md
- [ ] Add change preview before applying
- [ ] Implement collaborative editing (multi-user sessions)
- [ ] Add voice input support
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from mcp_use.client import MCPClient
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from dotenv import load_dotenv

load_dotenv()


@dataclass
class PRDChange:
    """Represents a change to PRD.md"""
    line_number: int
    old_value: str
    new_value: str
    section: str  # e.g., "Project Name", "Requirements", "Features"


class PRDManipulationTools:
    """
    Custom MCP tools for PRD.md manipulation
    
    These tools allow the agent to:
    1. Read current PRD content
    2. Update specific lines
    3. Notify UI of changes for highlighting
    """
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        self.prd_content: str = ""
        self.prd_lines: List[str] = []
        self.changes: List[PRDChange] = []
        self.websocket_callback = websocket_callback
    
    def get_tools(self) -> List[Dict]:
        """Return tool definitions for MCP"""
        return [
            {
                "name": "get_prd_content",
                "description": "Získaj aktuálny obsah PRD.md",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "function": self.get_prd_content
            },
            {
                "name": "update_prd_line",
                "description": """Aktualizuj konkrétny riadok v PRD.md. 
                Zmena sa automaticky zvýrazní v UI zelenou farbou.
                User môže zmenu zrušiť pomocou undo buttonu.""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "line_number": {
                            "type": "integer",
                            "description": "Číslo riadku (0-based index)"
                        },
                        "new_value": {
                            "type": "string",
                            "description": "Nový obsah riadku"
                        },
                        "section": {
                            "type": "string",
                            "description": "Sekcia PRD (napr. 'Project Name', 'Requirements')"
                        }
                    },
                    "required": ["line_number", "new_value", "section"]
                },
                "function": self.update_prd_line
            },
            {
                "name": "find_prd_section",
                "description": """Nájdi číslo riadku pre konkrétnu sekciu PRD.md.
                Používaj pred update_prd_line aby si zistil kde updatovať.""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "section_name": {
                            "type": "string",
                            "description": "Názov sekcie (napr. 'Project Name:', '## Requirements')"
                        }
                    },
                    "required": ["section_name"]
                },
                "function": self.find_prd_section
            },
            {
                "name": "append_to_prd",
                "description": """Pridaj nový obsah na koniec PRD.md.
                Použij pri pridávaní nových sekcií alebo requirements.""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Obsah na pridanie (markdown)"
                        }
                    },
                    "required": ["content"]
                },
                "function": self.append_to_prd
            }
        ]
    
    def get_prd_content(self) -> str:
        """Get current PRD content"""
        return self.prd_content or "# Nový projekt\n\n(prázdne - začíname brainstorming)"
    
    def update_prd_line(self, line_number: int, new_value: str, section: str) -> str:
        """Update specific PRD line with UI notification"""
        if not self.prd_lines:
            self.prd_lines = self.prd_content.split('\n') if self.prd_content else []
        
        # Ensure line exists
        while len(self.prd_lines) <= line_number:
            self.prd_lines.append("")
        
        old_value = self.prd_lines[line_number]
        self.prd_lines[line_number] = new_value
        self.prd_content = '\n'.join(self.prd_lines)
        
        # Track change
        change = PRDChange(
            line_number=line_number,
            old_value=old_value,
            new_value=new_value,
            section=section
        )
        self.changes.append(change)
        
        # Notify UI via WebSocket
        if self.websocket_callback:
            asyncio.create_task(self.websocket_callback({
                "type": "prd_change",
                "line_number": line_number,
                "old_value": old_value,
                "new_value": new_value,
                "section": section
            }))
        
        return f"✓ Updatovaný riadok {line_number} v sekcii '{section}'"
    
    def find_prd_section(self, section_name: str) -> Dict:
        """Find line number for a section"""
        if not self.prd_lines:
            self.prd_lines = self.prd_content.split('\n') if self.prd_content else []
        
        for idx, line in enumerate(self.prd_lines):
            if section_name.lower() in line.lower():
                return {
                    "line_number": idx,
                    "content": line,
                    "found": True
                }
        
        return {
            "found": False,
            "message": f"Sekcia '{section_name}' nebola nájdená"
        }
    
    def append_to_prd(self, content: str) -> str:
        """Append content to PRD"""
        if not self.prd_lines:
            self.prd_lines = self.prd_content.split('\n') if self.prd_content else []
        
        # Add content
        new_lines = content.split('\n')
        start_line = len(self.prd_lines)
        self.prd_lines.extend(new_lines)
        self.prd_content = '\n'.join(self.prd_lines)
        
        # Notify UI for each new line
        if self.websocket_callback:
            for idx, line in enumerate(new_lines):
                line_num = start_line + idx
                asyncio.create_task(self.websocket_callback({
                    "type": "prd_change",
                    "line_number": line_num,
                    "old_value": "",
                    "new_value": line,
                    "section": "new"
                }))
        
        return f"✓ Pridaných {len(new_lines)} riadkov do PRD"


class MCPBrainstormAgent:
    """
    MCP-enhanced Brainstorm Agent
    
    Uses mcp-use library for robust tool calling and
    direct PRD.md manipulation with UI synchronization
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        websocket_callback: Optional[Callable] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            api_key=self.api_key,
            temperature=0.7
        )
        
        # Initialize PRD tools
        self.prd_tools = PRDManipulationTools(websocket_callback)
        
        # Load AP protocol
        self.ap_protocol = self._load_ap_protocol()
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        # Conversation history
        self.messages = []
    
    def _load_ap_protocol(self) -> str:
        """Load AP.md protocol"""
        ap_path = Path("AP.md")
        if ap_path.exists():
            return ap_path.read_text()
        return "Analytic Programming Protocol (not loaded)"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt"""
        return f"""Si MCP-enhanced Brainstorm Agent pre Analytic Programming.

**Tvoja úloha:**
1. Pomôcť userovi vytvoriť PRD.md interaktívne
2. Používať TOOLS pre manipuláciu PRD.md
3. Každá zmena sa automaticky zvýrazní v UI zelenou
4. User môže zrušiť tvoje zmeny pomocou undo button

**Dostupné TOOLS:**
- get_prd_content(): Získaj aktuálny PRD
- find_prd_section(section_name): Nájdi riadok sekcie
- update_prd_line(line_number, new_value, section): Updatuj riadok (zvýrazní sa zeleno!)
- append_to_prd(content): Pridaj nový obsah

**Workflow:**
1. User ti povie info o projekte
2. Ty použiješ find_prd_section() aby si našiel kde updatovať
3. Použiješ update_prd_line() na update (UI sa automaticky zvýrazní!)
4. Potvrdíš userovi čo si zmenil

**Príklad - Update názvu projektu:**
User: "Projekt sa bude volať 'Blog API'"
1. find_prd_section("Project Name:") -> line 0
2. update_prd_line(0, "Project Name: Blog API", "Project Name")
3. Odpoveď: "✓ Nastavil som názov projektu na 'Blog API' (vidíš zvýraznenie?)"

**Kľúčové princípy:**
- VŽDY používaj tools pre zmeny PRD
- Každá zmena sa MUSÍ zvýrazniť v UI
- Buď friendly & conversational
- Pýtaj sa follow-up otázok
- Vysvetľuj čo si zmenil

**AP Protocol Context:**
{self.ap_protocol[:1500]}...

**PRD.md Template:**
```markdown
Project Name: [názov projektu]

## Overview
[popis projektu]

## Requirements
- R1: [functional requirement]
- R2: [non-functional requirement]

## Features
- F1: [feature description]

## Architecture
- [technology stack]
- [system design]

## Constraints
- [performance, security, etc.]
```

**Správanie:**
- Vždy potvrď zmeny userovi
- Pýtaj sa jednu otázku naraz
- Buď stručný (2-3 vety)
- Používaj emoji pre lepší UX 🎯
"""
    
    async def start_session(self, project_name: str = "Nový projekt") -> str:
        """Start brainstorming session"""
        # Initialize PRD with template
        initial_prd = f"""Project Name: {project_name}

## Overview
(Opíš hlavný účel projektu)

## Requirements
- R1: (Funkčný requirement)

## Features
- F1: (Feature description)

## Architecture
- Technology stack: (TBD)

## Constraints
- Performance: (TBD)
"""
        self.prd_tools.prd_content = initial_prd
        self.prd_tools.prd_lines = initial_prd.split('\n')
        
        # Initial greeting
        greeting = f"""👋 Ahoj! Som tvoj Brainstorm Helper.

Začíname projekt "{project_name}". 

Vidíš PRD.md vpravo? Budeme ho spoločne vytvárať - každú moju zmenu uvidíš zvýraznenú zelenou! Ak sa ti niečo nepáči, môžeš to vrátiť pomocou "Undo" buttonu.

🎯 Povedz mi: Čo má tento projekt robiť? (hlavný cieľ)"""
        
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": greeting}
        ]
        
        return greeting
    
    async def process_message(self, user_message: str) -> str:
        """
        Process user message with tool calling
        
        Agent will automatically use tools to update PRD
        and notify UI of changes
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})
        
        # Create LLM with tools
        tools_schema = self.prd_tools.get_tools()
        llm_with_tools = self.llm.bind_tools([
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            for tool in tools_schema
        ])
        
        # Get LLM response (may include tool calls)
        response = await llm_with_tools.ainvoke(self.messages)
        
        # Process tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # IMPORTANT: Add assistant message WITH tool_calls first!
            # OpenAI API requires: assistant(with tool_calls) -> tool -> assistant(final)
            self.messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"])  # Must be JSON string!
                        }
                    }
                    for tc in response.tool_calls
                ]
            })
            
            # Execute tools and add results
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Execute tool
                tool_func = next(
                    (t["function"] for t in tools_schema if t["name"] == tool_name),
                    None
                )
                
                if tool_func:
                    result = tool_func(**tool_args)
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": str(result)
                    })
            
            # Get final response after tool execution
            final_response = await self.llm.ainvoke(self.messages)
            assistant_message = final_response.content
            
            # Add final assistant message
            self.messages.append({"role": "assistant", "content": assistant_message})
        else:
            # No tool calls - simple response
            assistant_message = response.content
            self.messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def get_prd_content(self) -> str:
        """Get current PRD content"""
        return self.prd_tools.prd_content
    
    def get_changes(self) -> List[PRDChange]:
        """Get all PRD changes"""
        return self.prd_tools.changes


# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo MCP brainstorm agent"""
    print("=" * 70)
    print("DEMO: MCP-Enhanced Brainstorm Agent")
    print("=" * 70)
    
    # WebSocket callback simulation
    async def ws_callback(data):
        print(f"\n📡 WebSocket → UI: {json.dumps(data, indent=2)}")
    
    agent = MCPBrainstormAgent(websocket_callback=ws_callback)
    
    # Start session
    greeting = await agent.start_session("Blog API")
    print(f"\n🤖 Agent: {greeting}")
    
    # Simulate conversation
    user_messages = [
        "Chcem REST API pre blog - články, komentáre, používatelia",
        "Python FastAPI, PostgreSQL databáza",
        "Potrebujem authentication pomocou JWT tokens"
    ]
    
    for msg in user_messages:
        print(f"\n👤 User: {msg}")
        response = await agent.process_message(msg)
        print(f"\n🤖 Agent: {response}")
        
        # Show current PRD
        prd = agent.get_prd_content()
        print(f"\n📄 PRD.md:\n{'-' * 50}")
        print(prd[:300] + "..." if len(prd) > 300 else prd)
        print("-" * 50)
    
    # Show all changes
    print(f"\n\n📝 Total changes: {len(agent.get_changes())}")
    for change in agent.get_changes():
        print(f"  Line {change.line_number} ({change.section}): '{change.old_value}' → '{change.new_value}'")
    
    print("\n✓ Demo complete")


if __name__ == "__main__":
    asyncio.run(demo())

