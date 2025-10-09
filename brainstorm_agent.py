#!/usr/bin/env python3
"""
brainstorm_agent.py - Brainstorm Helper Agent

Interaktívny LLM agent pre tvorbu PRD.md:
- Reads AP.md (understands orchestration)
- Conversational interface
- Smart questions based on project type
- Real-time PRD.md generation

Version: 1.0.0
Date: October 9, 2025
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Tuple, Optional
from openai import OpenAI


class BrainstormHelperAgent:
    """
    Brainstorm Helper Agent pre PRD.md creation
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Initialize OpenAI client (new API)
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Load AP protocol
        self.ap_protocol = self._load_ap_protocol()
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
    
    def _load_ap_protocol(self) -> str:
        """Load AP.md protocol"""
        ap_path = Path("AP.md")
        if ap_path.exists():
            return ap_path.read_text()
        return "Analytic Programming Protocol (not loaded)"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for agent"""
        return f"""Si Brainstorm Helper Agent pre Analytic Programming.

**Tvoja úloha:**
1. Pomôcť userovi vytvoriť PRD.md (Product Requirements Document)
2. Pýtať sa smart questions o projekte
3. Postupne budovať PRD.md v markdown formáte
4. Pripraviť projekt na orchestráciu (multi-agent execution)

**Kontext - AP Protocol:**
{self.ap_protocol[:2000]}...

**Kľúčové princípy:**
- PRD.md bude použitý orchestrátorom pre task decomposition
- Orchestrátor rozdelí prácu medzi multiple AI agents (Claude, GPT-4, Codex)
- Potrebuješ identifikovať: features, requirements, architecture, constraints
- Musíš byť konverzačný, friendly, a helpful

**Formát PRD.md:**
```markdown
# Project Name

## Overview
Brief description

## Requirements
- R1: Functional requirement
- R2: Non-functional requirement

## Features
- F1: Feature description
- F2: Feature description

## Architecture
- Technology stack
- System design

## Constraints
- Performance requirements
- Security requirements

## Acceptance Criteria
- How to validate success
```

**Tvoje správanie:**
- Vítaj usera warm & friendly
- Pýtaj sa open-ended questions
- Postupne dopĺňaj PRD.md
- Po každej odpovedi updatni PRD.md
- Vysvetli čo si pridal do PRD
- Navrhni ďalší krok

**Dôležité:**
- Vždy vráť JSON s: response, updated_prd, completion_percentage
- PRD.md musí byť valid markdown
- Buď stručný ale informatívny (max 3-4 vety)
"""
    
    async def start_session(self, project_name: str) -> str:
        """
        Start brainstorming session
        
        Returns: Initial greeting message
        """
        prompt = f"""
Začíname nový projekt: "{project_name}"

Privítaj usera a spýtaj sa na typ projektu / hlavný cieľ.
Buď friendly, stručný (2-3 vety).
"""
        
        response = await self._call_llm(prompt, include_prd=False)
        return response
    
    async def process_message(
        self,
        user_message: str,
        current_prd: str
    ) -> Tuple[str, str]:
        """
        Process user message
        
        Args:
            user_message: User's message
            current_prd: Current PRD.md content
        
        Returns:
            (assistant_response, updated_prd)
        """
        prompt = f"""
User message: "{user_message}"

Current PRD.md:
```markdown
{current_prd if current_prd else "# {project_name}\n\n(prázdne - začíname)"}
```

**Úloha:**
1. Odpovedz userovi (conversational, 2-3 vety)
2. Updatni PRD.md na základe nových informácií
3. Opýtaj sa follow-up otázku (ak potrebné)

**Vráť JSON:**
{{
    "response": "Tvoja odpoveď userovi",
    "updated_prd": "Kompletný updatnutý PRD.md (markdown)",
    "next_question": "Optional follow-up question",
    "completion_percentage": 0-100
}}

**Pravidlá:**
- Zachovaj existujúci obsah PRD, len pridaj nové
- Používaj markdown formatting
- Buď špecifický a konkrétny
- Completion je 100% keď sú: Overview, Requirements, Features, Architecture
"""
        
        response_json = await self._call_llm(prompt, include_prd=True)
        
        try:
            data = json.loads(response_json)
            assistant_response = data.get('response', '')
            updated_prd = data.get('updated_prd', current_prd)
            next_question = data.get('next_question', '')
            
            # Append next question to response if exists
            if next_question:
                assistant_response += f"\n\n{next_question}"
            
            return assistant_response, updated_prd
        
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return JSON
            return (
                f"Rozumiem: {user_message}",
                current_prd + f"\n\n## User Input\n{user_message}"
            )
    
    async def _call_llm(
        self,
        prompt: str,
        include_prd: bool = False
    ) -> str:
        """
        Call OpenAI API
        
        Args:
            prompt: User prompt
            include_prd: Whether to expect JSON response with PRD
        
        Returns:
            LLM response (string or JSON string)
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use new OpenAI API (1.0.0+)
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000 if include_prd else 500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"LLM API error: {e}")
            if include_prd:
                return json.dumps({
                    "response": f"(API error: {e})",
                    "updated_prd": "",
                    "completion_percentage": 0
                })
            return f"Ospravedlňujem sa, mám problém s API: {e}"


# ============================================================================
# DEMO / TESTING
# ============================================================================

async def demo():
    """Demo brainstorm agent"""
    agent = BrainstormHelperAgent()
    
    # Start session
    print("=" * 60)
    print("DEMO: Brainstorm Helper Agent")
    print("=" * 60)
    
    greeting = await agent.start_session("Blog API")
    print(f"\nAgent: {greeting}")
    
    # Simulate conversation
    user_messages = [
        "Chcem REST API pre blog s postami a komentármi",
        "Python FastAPI, PostgreSQL databáza",
        "Potrebujem authentication a authorization"
    ]
    
    current_prd = ""
    
    for msg in user_messages:
        print(f"\nUser: {msg}")
        response, current_prd = await agent.process_message(msg, current_prd)
        print(f"Agent: {response}")
        print(f"\n--- PRD.md (excerpt) ---\n{current_prd[:200]}...\n")
    
    print("\n✓ Demo complete")


if __name__ == "__main__":
    asyncio.run(demo())

