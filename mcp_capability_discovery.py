#!/usr/bin/env python3
"""
mcp_capability_discovery.py - Automatic MCP Worker Capability Discovery

Automaticky objavuje schopnosti (capabilities) MCP serverov pomocou:
1. Zoznam dostupných tools cez MCP Protocol
2. LLM analýza tools → capability tags
3. Automatická aktualizácia team.json s user potvrdením

Version: 1.0.0
Author: Analytic Programming Team
Date: October 9, 2025
"""

import asyncio
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import aiofiles

# Import z MCP server stdio
from mcp_server_stdio import MCPServerStdio, MCPTool, MCPWorkerConfig, MCPWorkerType

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class CapabilityAnalysis:
    """Výsledok LLM analýzy worker capabilities"""
    worker_id: str
    worker_type: str
    capabilities: List[str]
    reasoning: str
    suggested_use_cases: List[str]
    strengths: List[str]
    limitations: List[str]
    confidence_score: float  # 0.0 - 1.0
    analysis_timestamp: str

@dataclass
class DiscoveryResult:
    """Komplexný výsledok capability discovery procesu"""
    worker_id: str
    tools_count: int
    tools: List[MCPTool]
    analysis: CapabilityAnalysis
    previous_capabilities: List[str]
    changes_detected: bool

# ============================================================================
# LLM CAPABILITY DISCOVERY PROMPT
# ============================================================================

CAPABILITY_DISCOVERY_PROMPT = """Analyzuj nasledujúci MCP server a urč jeho schopnosti (capabilities).

**MCP Server Info:**
- Name: {worker_name}
- Type: {worker_type}
- Description: {worker_description}

**Dostupné Tools ({tools_count} total):**
{tools_list}

**Detailné informácie o tools:**
{tool_details}

**Úloha:**
Na základe dostupných tools urči 3-7 capability tagov, ktoré najlepšie vystihujú 
silné stránky tohto workera. Použi tieto kategórie:

**Coding Capabilities:**
- refactoring, type_hints, code_generation, syntax_fixes
- python, javascript, typescript, rust, go, java, cpp
- multi_file_changes, quick_fixes, complex_logic

**Analysis Capabilities:**
- deep_analysis, debugging, performance, testing
- architecture, design_patterns, code_review

**Domain Expertise:**
- web_dev, backend, frontend, database, security
- ml_ai, data_science, algorithms, systems

**Special Tools:**
- file_operations, search, git_operations, terminal
- documentation, migration, integration, automation

**Formát odpovede (JSON):**
{{
  "capabilities": ["tag1", "tag2", "tag3"],
  "reasoning": "Krátke vysvetlenie prečo tieto capabilities (2-3 vety)",
  "suggested_use_cases": ["use case 1", "use case 2"],
  "strengths": ["strength 1", "strength 2"],
  "limitations": ["limitation 1", "limitation 2"],
  "confidence_score": 0.85
}}

Buď špecifický a praktický. Capabilities by mali pomôcť orchestrátorovi rozhodnúť,
ktoré úlohy prideliť tomuto workerovi.

Pravidlá:
1. Capabilities musia byť lowercase, underscore_separated
2. Max 7 capabilities (prioritizuj najdôležitejšie)
3. Confidence score: 0.0-1.0 (na základe tool clarity)
4. Reasoning musí byť konkrétny (mention specific tools)
"""

# ============================================================================
# MCP CAPABILITY DISCOVERER
# ============================================================================

class MCPCapabilityDiscoverer:
    """
    Automaticky objavuje capabilities MCP serverov pomocou LLM analýzy
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4",
        team_config_path: Path = Path("team.json")
    ):
        """
        Args:
            llm_provider: "openai" alebo "claude"
            llm_api_key: API key pre LLM (alebo z env)
            llm_model: Model name (gpt-4, gpt-3.5-turbo, claude-3-opus)
            team_config_path: Cesta k team.json
        """
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key or os.getenv(
            "OPENAI_API_KEY" if llm_provider == "openai" else "ANTHROPIC_API_KEY"
        )
        self.llm_model = llm_model
        self.team_config_path = team_config_path
        
        if not self.llm_api_key:
            raise ValueError(f"Missing API key for {llm_provider}")
    
    async def discover_worker_capabilities(
        self,
        worker_id: str,
        mcp_server: MCPServerStdio,
        worker_description: str = ""
    ) -> DiscoveryResult:
        """
        Hlavná metóda - objavenie capabilities pre workera
        
        Args:
            worker_id: ID workera z team.json
            mcp_server: Running MCP server instance
            worker_description: Voliteľný popis workera
        
        Returns:
            DiscoveryResult s kompletnou analýzou
        """
        print(f"\n🔍 Discovering capabilities for worker: {worker_id}")
        
        # 1. Získaj zoznam tools
        print(f"  → Requesting tool list from worker...")
        try:
            tools = await mcp_server.list_tools(timeout=15.0)
            print(f"  ✓ Worker has {len(tools)} tools")
        except TimeoutError:
            print(f"  ✗ Worker didn't respond - may not support LIST_TOOLS")
            # Fallback: prázdny zoznam (LLM použije len worker_type)
            tools = []
        
        # 2. Načítaj predchádzajúce capabilities
        previous_caps = await self._get_previous_capabilities(worker_id)
        
        # 3. Analyzuj pomocou LLM
        print(f"  → Analyzing tools with {self.llm_provider} {self.llm_model}...")
        analysis = await self.analyze_with_llm(
            worker_name=worker_id,
            worker_type=mcp_server.config.worker_type.value,
            tools=tools,
            worker_description=worker_description
        )
        print(f"  ✓ Analysis complete (confidence: {analysis.confidence_score:.2f})")
        
        # 4. Detekuj zmeny
        changes = set(analysis.capabilities) != set(previous_caps)
        
        return DiscoveryResult(
            worker_id=worker_id,
            tools_count=len(tools),
            tools=tools,
            analysis=analysis,
            previous_capabilities=previous_caps,
            changes_detected=changes
        )
    
    async def list_worker_tools(
        self,
        mcp_server: MCPServerStdio
    ) -> List[MCPTool]:
        """
        Získa zoznam tools z MCP servera
        
        Returns:
            List MCPTool objektov
        """
        return await mcp_server.list_tools()
    
    async def analyze_with_llm(
        self,
        worker_name: str,
        worker_type: str,
        tools: List[MCPTool],
        worker_description: str = ""
    ) -> CapabilityAnalysis:
        """
        Analyzuje tools pomocou LLM API a vráti capability analysis
        
        Args:
            worker_name: Názov workera
            worker_type: Typ workera (codex, claude, gpt4, etc.)
            tools: Zoznam MCPTool objektov
            worker_description: Voliteľný popis
        
        Returns:
            CapabilityAnalysis s navrhnutými capabilities
        """
        # Priprav tools list
        tools_list = "\n".join(f"  • {tool.name}: {tool.description}" for tool in tools)
        if not tools_list:
            tools_list = "  (No tools reported - worker may not support LIST_TOOLS)"
        
        # Priprav tool details
        tool_details = ""
        for tool in tools[:20]:  # Limit pre token usage
            params_str = json.dumps(tool.parameters, indent=2) if tool.parameters else "{}"
            tool_details += f"\n### {tool.name}\n"
            tool_details += f"Description: {tool.description}\n"
            tool_details += f"Parameters: {params_str}\n"
            if tool.returns:
                tool_details += f"Returns: {tool.returns}\n"
        
        if not tool_details:
            tool_details = "(No detailed tool information available)"
        
        # Vytvor prompt
        prompt = CAPABILITY_DISCOVERY_PROMPT.format(
            worker_name=worker_name,
            worker_type=worker_type,
            worker_description=worker_description or f"MCP worker of type {worker_type}",
            tools_count=len(tools),
            tools_list=tools_list,
            tool_details=tool_details
        )
        
        # Zavolaj LLM API
        if self.llm_provider == "openai":
            response = await self._call_openai_api(prompt)
        elif self.llm_provider == "claude":
            response = await self._call_claude_api(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        # Parse JSON response
        try:
            result = json.loads(response)
            
            return CapabilityAnalysis(
                worker_id=worker_name,
                worker_type=worker_type,
                capabilities=result.get('capabilities', []),
                reasoning=result.get('reasoning', ''),
                suggested_use_cases=result.get('suggested_use_cases', []),
                strengths=result.get('strengths', []),
                limitations=result.get('limitations', []),
                confidence_score=result.get('confidence_score', 0.5),
                analysis_timestamp=datetime.now().isoformat()
            )
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse LLM response as JSON: {e}")
            print(f"Response: {response[:200]}")
            
            # Fallback: základné capabilities na základe worker_type
            return self._fallback_capabilities(worker_name, worker_type)
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Zavolá OpenAI API pre capability analýzu"""
        try:
            # Lazy import (nemusí byť nainštalované)
            import openai
            openai.api_key = self.llm_api_key
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing code tools and determining AI agent capabilities. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
        
        except ImportError:
            print("⚠️ openai package not installed. Install: pip install openai")
            raise
        except Exception as e:
            print(f"✗ OpenAI API error: {e}")
            raise
    
    async def _call_claude_api(self, prompt: str) -> str:
        """Zavolá Claude API pre capability analýzu"""
        try:
            # Lazy import
            import anthropic
            client = anthropic.Anthropic(api_key=self.llm_api_key)
            
            response = await asyncio.to_thread(
                client.messages.create,
                model=self.llm_model,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
        
        except ImportError:
            print("⚠️ anthropic package not installed. Install: pip install anthropic")
            raise
        except Exception as e:
            print(f"✗ Claude API error: {e}")
            raise
    
    def _fallback_capabilities(
        self,
        worker_name: str,
        worker_type: str
    ) -> CapabilityAnalysis:
        """Fallback capabilities ak LLM analýza zlyhá"""
        capability_map = {
            'codex': ['refactoring', 'type_hints', 'quick_fixes', 'python'],
            'claude': ['complex_logic', 'architecture', 'deep_analysis', 'refactoring'],
            'gpt4': ['algorithms', 'debugging', 'testing', 'performance'],
            'cursor': ['code_generation', 'refactoring', 'multi_file_changes'],
            'droid': ['automation', 'integration', 'code_generation']
        }
        
        caps = capability_map.get(worker_type, ['general_coding'])
        
        return CapabilityAnalysis(
            worker_id=worker_name,
            worker_type=worker_type,
            capabilities=caps,
            reasoning=f"Fallback capabilities based on worker type: {worker_type}",
            suggested_use_cases=[f"Tasks suitable for {worker_type}"],
            strengths=[f"Standard {worker_type} capabilities"],
            limitations=["Unable to analyze specific tools"],
            confidence_score=0.3,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    async def _get_previous_capabilities(self, worker_id: str) -> List[str]:
        """Načíta predchádzajúce capabilities z team.json"""
        if not self.team_config_path.exists():
            return []
        
        async with aiofiles.open(self.team_config_path, 'r') as f:
            content = await f.read()
            config = json.loads(content)
        
        for worker in config.get('workers', []):
            if worker.get('id') == worker_id:
                return worker.get('capabilities', [])
        
        return []
    
    async def update_team_config(
        self,
        worker_id: str,
        capabilities: List[str],
        backup: bool = True
    ) -> bool:
        """
        Aktualizuje capabilities v team.json
        
        Args:
            worker_id: ID workera
            capabilities: Nové capabilities
            backup: Či vytvoriť backup pred zmenou
        
        Returns:
            True ak úspešné, False inak
        """
        try:
            # Načítaj aktuálny config
            async with aiofiles.open(self.team_config_path, 'r') as f:
                content = await f.read()
                config = json.loads(content)
            
            # Backup
            if backup:
                backup_path = self.team_config_path.parent / f"team.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                async with aiofiles.open(backup_path, 'w') as f:
                    await f.write(content)
                print(f"  💾 Backup saved: {backup_path}")
            
            # Update capabilities
            updated = False
            for worker in config.get('workers', []):
                if worker.get('id') == worker_id:
                    old_caps = worker.get('capabilities', [])
                    worker['capabilities'] = capabilities
                    updated = True
                    print(f"  ✓ Updated capabilities for {worker_id}")
                    print(f"    Old: {old_caps}")
                    print(f"    New: {capabilities}")
                    break
            
            if not updated:
                print(f"  ✗ Worker {worker_id} not found in team.json")
                return False
            
            # Zapíš späť
            async with aiofiles.open(self.team_config_path, 'w') as f:
                await f.write(json.dumps(config, indent=2))
            
            print(f"  ✓ team.json updated successfully")
            return True
        
        except Exception as e:
            print(f"  ✗ Failed to update team.json: {e}")
            return False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_discovery_result(result: DiscoveryResult) -> str:
    """Formatuje DiscoveryResult pre user-friendly zobrazenie"""
    analysis = result.analysis
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║  🔍 MCP Worker Capability Discovery Results                  ║
╠══════════════════════════════════════════════════════════════╣
║  Worker ID: {result.worker_id:<49} ║
║  Worker Type: {analysis.worker_type:<47} ║
║  Tools Count: {result.tools_count:<47} ║
║  Confidence: {analysis.confidence_score:.2f}                                       ║
╠══════════════════════════════════════════════════════════════╣

📋 DISCOVERED CAPABILITIES ({len(analysis.capabilities)}):
"""
    
    for cap in analysis.capabilities:
        output += f"  ✓ {cap}\n"
    
    output += f"\n💡 REASONING:\n  {analysis.reasoning}\n"
    
    output += f"\n🎯 SUGGESTED USE CASES:\n"
    for uc in analysis.suggested_use_cases:
        output += f"  • {uc}\n"
    
    output += f"\n💪 STRENGTHS:\n"
    for strength in analysis.strengths:
        output += f"  + {strength}\n"
    
    output += f"\n⚠️  LIMITATIONS:\n"
    for limitation in analysis.limitations:
        output += f"  - {limitation}\n"
    
    if result.changes_detected:
        output += f"\n🔄 CHANGES DETECTED:\n"
        output += f"  Previous: {result.previous_capabilities}\n"
        output += f"  New:      {analysis.capabilities}\n"
    else:
        output += f"\n✓ No changes from previous capabilities\n"
    
    output += "\n" + "═" * 64 + "\n"
    
    return output

# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo MCPCapabilityDiscoverer"""
    print("🚀 MCP Capability Discovery Demo\n")
    
    # Simulovaný MCP server s mock tools
    from mcp_server_stdio import WebSocketBroadcaster
    
    mock_config = MCPWorkerConfig(
        worker_id="test-worker",
        worker_type=MCPWorkerType.CODEX,
        command="echo",
        args=["mock"],
        env={}
    )
    
    broadcaster = WebSocketBroadcaster()
    # Note: V reálnom použití by sme najprv spustili broadcaster.start()
    
    # V demo režime nevytvárame skutočný proces
    # server = MCPServerStdio(mock_config, broadcaster)
    # await server.start()
    
    print("✓ Demo complete. Use discover_worker.py CLI tool for real discovery.\n")

if __name__ == "__main__":
    asyncio.run(demo())

