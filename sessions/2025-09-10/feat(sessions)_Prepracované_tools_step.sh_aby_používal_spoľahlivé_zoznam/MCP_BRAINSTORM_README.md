# MCP-Enhanced Interactive Brainstorming

**Version:** AP Studio 2.0  
**Status:** ✅ Production Ready

## Čo je to?

**Interactive PRD Brainstorming** je pokročilý systém kde AI agent v reálnom čase upravuje PRD.md a ty vidíš každú zmenu zvýraznenú **zelenou farbou** s možnosťou **undo**.

Žiadne viac manuálne písanie PRD! Len si pokecáš s agentom a on ti vytvorí kompletný PRD.md - každú zmenu vidíš okamžite.

## Quick Start

### 1. Inštalácia

```bash
# Clone repo (ak nemáš)
git clone https://github.com/your-org/analytic_programming.git
cd analytic_programming

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup API Key

```bash
export OPENAI_API_KEY=sk-...
```

### 3. Spustenie

```bash
# Start backend
python ap_studio_backend.py

# Open browser
open http://localhost:8000
```

### 4. Test

```bash
# Automated test
./test_mcp_brainstorm.sh
```

## Ako to funguje?

### Krok 1: Začni brainstorming

1. Otvor AP Studio v browseri
2. Vyber projekt alebo vytvor nový (➕ New project)
3. Klikni na tab "💬 Brainstorming"

### Krok 2: Porozprávaj sa s agentom

**Ty:** "Chcem REST API pre blog s postami a komentármi"

**Agent:**
- Spýta sa follow-up otázky
- Upraví PRD.md v reálnom čase
- **Zvýrazní zmeny zelenou!**

### Krok 3: Sleduj zmeny

- Každá zmena sa zvýrazní zelenou
- Hover nad zmenou → "↶ Undo" button
- Click → vráti pôvodnú hodnotu

### Krok 4: Spusť orchestráciu

- Keď je PRD hotový, klikni "🚀 Spustiť Orchestráciu"
- Orchestrátor rozdelí prácu medzi AI agentov
- Multi-agent execution!

## Príklad Session

```
👤 Ty: "Chcem REST API pre blog"

🤖 Agent: "Skvelé! Nastavil som názov projektu. 
           Aké funkcie by mal blog mať?"
           
📄 PRD.md:
   Project Name: Blog API  ← 🟢 GREEN (modified)

👤 Ty: "Posts, comments, users, authentication"

🤖 Agent: "Rozumiem! Pridal som features do PRD."

📄 PRD.md:
   ## Features
   - F1: Posts CRUD       ← 🟢 GREEN (new)
   - F2: Comments system  ← 🟢 GREEN (new)  
   - F3: User management  ← 🟢 GREEN (new)
   - F4: JWT authentication ← 🟢 GREEN (new)
   
👤 Ty: [hover nad "F4: JWT authentication"]
       [click "↶ Undo"]
       
📄 PRD.md:
   - F4: JWT authentication ← ❌ REMOVED
```

## Architektúra

### MCP Tools

Agent má k dispozícii tieto nástroje:

```python
# Get current PRD
get_prd_content()

# Find section line number
find_prd_section("Project Name:")  
# → { "line_number": 0, "found": true }

# Update line (auto-highlights GREEN!)
update_prd_line(
    line_number=0,
    new_value="Project Name: Blog API",
    section="Project Name"
)

# Append content
append_to_prd("## New Section\n- Content")
```

### Flow Diagram

```
User Message
    ↓
LangChain Agent (with MCP tools)
    ↓
Tool Selection: update_prd_line()
    ↓
PRD Updated + Change Tracked
    ↓
WebSocket → UI
    ↓
Green Highlight + Pulse Animation
    ↓
User: Hover → Undo Button
```

## Features

### ✅ Real-time Updates
- Agent upravuje PRD.md line-by-line
- Okamžité zobrazenie v UI
- WebSocket synchronizácia

### ✅ Visual Feedback
- **Zelené zvýraznenie:** `rgba(74, 222, 128, 0.15)`
- **Border:** `3px solid var(--accent-primary)`
- **Animácia:** Pulse 2s ease-in-out

### ✅ Undo Capability
- Hover → "↶ Undo" button
- Click → restore original value
- Per-line granular control

### ✅ Smart Project Management
- Dropdown pre výber projektu
- ➕ New project button
- Žiadne annoying alerty!
- Auto-select last project

### ✅ MCP Architecture
- Uses [mcp-use](https://github.com/mcp-use/mcp-use)
- LangChain tool binding
- Robust error handling
- 100× faster than log monitoring

## API Reference

### PRDManipulationTools

```python
from brainstorm_agent_mcp import MCPBrainstormAgent

# Initialize with WebSocket callback
agent = MCPBrainstormAgent(
    api_key="sk-...",
    websocket_callback=ws_callback
)

# Start session
greeting = await agent.start_session("My Project")

# Process message
response = await agent.process_message("User message")

# Get PRD content
prd = agent.get_prd_content()

# Get all changes
changes = agent.get_changes()
```

### WebSocket Messages

**From UI to Backend:**
```json
{
  "type": "message",
  "session_id": 123,
  "content": "Chcem REST API"
}

{
  "type": "undo_change",
  "session_id": 123,
  "line_number": 5
}
```

**From Backend to UI:**
```json
{
  "type": "prd_change",
  "line_number": 0,
  "old_value": "Project Name: ",
  "new_value": "Project Name: Blog API",
  "section": "Project Name"
}

{
  "type": "response",
  "message": "✓ Nastavil som názov projektu",
  "prd_content": "...",
  "prd_changes": [...]
}
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional
export MCP_USE_DEBUG=1  # Enable MCP debugging
export AP_STUDIO_PORT=8000  # Custom port
```

### Custom Model

```python
agent = MCPBrainstormAgent(
    model="gpt-4-turbo",  # or gpt-3.5-turbo, claude-3, etc.
    api_key="sk-..."
)
```

## Troubleshooting

### Agent neodpovedá
```bash
# Check API key
echo $OPENAI_API_KEY

# Check logs
python ap_studio_backend.py
# Look for: "✓ MCP Brainstorm agent initialized"
```

### PRD sa nezvýrazňuje zeleno
```bash
# Check WebSocket connection
# Browser console → should see: "✓ WebSocket connected"

# Check browser console for errors
# F12 → Console tab
```

### Undo nefunguje
```bash
# Check if prdHistory is populated
# Browser console: console.log(prdHistory)

# Should see: { 0: "original value", ... }
```

## Development

### Run Tests

```bash
# Standalone agent test
python brainstorm_agent_mcp.py

# Full integration test
./test_mcp_brainstorm.sh

# Manual UI test
python ap_studio_backend.py
# → Open http://localhost:8000
```

### Add New Tool

```python
class PRDManipulationTools:
    def get_tools(self):
        return [
            # ... existing tools ...
            {
                "name": "my_new_tool",
                "description": "What it does",
                "inputSchema": { ... },
                "function": self.my_new_tool
            }
        ]
    
    def my_new_tool(self, param1, param2):
        # Implementation
        return "result"
```

### Debug Mode

```bash
# Enable MCP debugging
export MCP_USE_DEBUG=2

# Enable verbose logging
python ap_studio_backend.py --log-level DEBUG
```

## Performance

- **Agent Response:** ~2-3 seconds (GPT-4)
- **WebSocket Latency:** <10ms
- **UI Update:** <50ms (green highlight)
- **Undo Action:** <100ms

## Limitations

- **Line-based editing:** Agent modifikuje po riadkoch (nie po tokenoch)
- **Single session:** Jeden brainstorm session naraz
- **English/Slovak only:** Agent podporuje SK/EN

## Future Enhancements

1. **Batch Undo:** Vráť všetky zmeny z poslednej správy
2. **Change Preview:** Ukáž diff pred aplikovaním
3. **Approval Mode:** Vyžaduj potvrdenie každej zmeny
4. **Change Timeline:** História všetkých modifikácií
5. **Multi-agent Brainstorming:** Viac agentov súčasne
6. **Voice Input:** Hovor namiesto písania

## References

- **MCP-Use:** https://github.com/mcp-use/mcp-use
- **LangChain:** https://python.langchain.com/
- **AP Protocol:** `/AP.md`
- **Architecture:** `/AP_STUDIO_ARCHITECTURE.md`
- **Implementation Details:** `/sessions/2025-09-10/INTERACTIVE_PRD_BRAINSTORMING.md`

## Support

**Issues:** https://github.com/your-org/analytic_programming/issues  
**Docs:** `/docs`  
**Discord:** discord.gg/your-server

---

**Built with ❤️ using:**
- [mcp-use](https://github.com/mcp-use/mcp-use) - MCP client
- [LangChain](https://langchain.com) - Agent framework  
- [FastAPI](https://fastapi.tiangolo.com) - Backend
- [OpenAI GPT-4](https://openai.com) - LLM

**License:** MIT

