# Project Workspace - Interactive MD Files

**Version:** AP Studio 2.0  
**Status:** ✅ Implemented

## Čo je to?

**Project Workspace** je súborový systém pre projekty kde každý projekt má vlastný adresár `~/.ap/projects/<project_name>/` s markdown súbormi ktoré agent číta a user môže interaktívne klikať na sekcie aby ich poslal do chatu.

**Kľúčová funkcia:** **KLIKNI A POŠLI DO CHATU** - už netreba nič vypisovať!

## Architektúra

### Directory Structure

```
~/.ap/projects/
  └── blog-api/              # Project directory
      ├── AGENTS.md          # ✅ Agent context (auto-loaded)
      ├── README.md          # ✅ Project overview (auto-loaded)
      ├── PRD.md            # ✅ Requirements (auto-loaded)
      ├── TODOs.md          # Tasks & todos
      ├── BUGs.md           # Known issues
      ├── FEATURES.md       # Feature specs
      └── .git/             # Version control
```

### File Types

| File | Icon | Auto-loaded | Klikateľné sekcie |
|------|------|-------------|-------------------|
| **README.md** | 📖 | ✅ Yes | - |
| **AGENTS.md** | 🤖 | ✅ Yes | - |
| **PRD.md** | 📝 | ✅ Yes | Features (F1, F2...), Requirements (R1, R2...) |
| **TODOs.md** | 📋 | No | All TODO items |
| **BUGs.md** | 🐛 | No | All BUG items |
| **FEATURES.md** | ⚡ | No | All features |

### UI Components

**1. File Selector Dropdown**
```
📂 Project Context...
  ✅ 🤖 AGENTS.md        ← Auto-loaded (green checkmark)
  ✅ 📖 README.md        ← Auto-loaded
  ✅ 📝 PRD.md          ← Auto-loaded
     📋 TODOs.md
     🐛 BUGs.md
     ⚡ FEATURES.md
```

**2. File Tabs**
```
[📝 PRD.md]  [📋 TODOs.md]  [🐛 BUGs.md]  [✕]
    ↑            ↑              ↑
  active       open           open
```

**3. Clickable Content**
```markdown
## Features
- F1: User authentication  ← KLIK → pošle do chatu!
- F2: Post creation        ← KLIK → pošle do chatu!

## TODOs
- [ ] TODO-1: Implement login  ← KLIK → pošle do chatu!
- [ ] TODO-2: Add tests         ← KLIK → pošle do chatu!
```

## Workflow

### 1. Vytvorenie Projektu

```javascript
// User: Click "➕ New project"
createNewProject()
  → POST /api/projects { name: "Blog API" }
  → Backend: Creates ~/.ap/projects/blog-api/
  → Backend: Generates template files
  → Backend: Git init
```

**Vytvorené súbory:**
- `AGENTS.md` - Agent configuration & context
- `README.md` - Project overview
- `PRD.md` - Product requirements (template)
- `TODOs.md` - Empty todos
- `BUGs.md` - Empty bugs
- `FEATURES.md` - Empty features

### 2. Session Start

```javascript
// Auto-load project context
switchProject("Blog API")
  → GET /api/projects/blog-api/files
  → Returns: {
      files: [
        { name: "AGENTS.md", loaded: true, ... },
        { name: "README.md", loaded: true, ... },
        { name: "PRD.md", loaded: true, ... },
        { name: "TODOs.md", loaded: false, ... }
      ]
    }
  → UI: Shows ✅ for loaded files
```

### 3. Open File

```javascript
// User: Selects "TODOs.md" → Click "Open"
openSelectedFile()
  → Adds tab: [📋 TODOs.md]
  → Loads content with clickable items
  → User sees TODO list
```

### 4. Click to Send

```javascript
// User: Click on "TODO-1: Implement login"
sendToChat("TODO-1: Implement login")
  → Fills chat input
  → Shows confirm: "📤 Poslať do chatu?"
  → User: Yes
  → Message sent to agent
  → Agent responds with implementation plan
```

## Template Files

### AGENTS.md (Agent Context)

```markdown
# Agents Configuration

## Project Context
- **Project Name:** Blog API
- **Created:** 2025-10-09
- **Last Updated:** 2025-10-09

## Agent Knowledge Base
This document is loaded by brainstorming agent on session start.

### Project Overview
(To be filled during brainstorming)

### Key Decisions
- Decision 1: (TBD)
- Decision 2: (TBD)

### Architecture Notes
- Tech stack: (TBD)
- Design patterns: (TBD)

### Constraints
- Performance: (TBD)
- Security: (TBD)
- Budget: (TBD)

---
*This file is auto-loaded by brainstorming agent*
```

### TODOs.md (Clickable Tasks)

```markdown
# Blog API - Tasks & TODOs

**Last Updated:** 2025-10-09

## 🎯 Current Sprint

### High Priority
- [ ] TODO-1: User authentication        ← KLIK!
- [ ] TODO-2: Post CRUD endpoints        ← KLIK!

### Medium Priority
- [ ] TODO-3: Comment system             ← KLIK!

### Low Priority
- [ ] TODO-4: Email notifications        ← KLIK!

## 📋 Backlog
- [ ] BACKLOG-1: Social login            ← KLIK!
- [ ] BACKLOG-2: Analytics dashboard     ← KLIK!

## ✅ Completed
- [x] DONE-1: Project setup

---
*Click on any TODO to send to brainstorming agent*
```

### BUGs.md (Clickable Bugs)

```markdown
# Blog API - Known Issues

**Last Updated:** 2025-10-09

## 🔴 Critical
- [ ] BUG-1: Login fails on Firefox      ← KLIK!

## 🟠 High Priority
- [ ] BUG-2: Slow post loading           ← KLIK!

## 🟡 Medium Priority
- [ ] BUG-3: Comment sorting wrong       ← KLIK!

## 🟢 Low Priority
- [ ] BUG-4: UI spacing issue            ← KLIK!

## ✅ Resolved
- [x] BUG-0: Database connection

---
*Click on any BUG to send to brainstorming agent*
```

## API Reference

### GET /api/projects/{project_name}/files

**Response:**
```json
{
  "files": [
    {
      "name": "AGENTS.md",
      "icon": "🤖",
      "content": "...",
      "loaded": true,
      "size": 1234
    },
    {
      "name": "TODOs.md",
      "icon": "📋",
      "content": "...",
      "loaded": false,
      "size": 567
    }
  ],
  "context_files": ["AGENTS.md", "README.md", "PRD.md"]
}
```

### POST /api/projects

**Request:**
```json
{
  "name": "Blog API",
  "description": "REST API for blog"
}
```

**Side Effects:**
- Creates database entry
- Creates `~/.ap/projects/blog-api/` directory
- Generates template MD files
- Initializes git repository

## JavaScript API

### File Management

```javascript
// Load project files
await loadProjectFiles(projectName)

// Open file in new tab
openSelectedFile()

// Switch active tab
switchFileTab(filename)

// Close tab
closeFileTab(event, filename)
```

### Click-to-Chat

```javascript
// Send text to chat (with confirm)
sendToChat(text)

// Auto-fill chat input
chatInput.value = text
chatInput.focus()
```

### Markdown Rendering

```javascript
// Render with clickable sections
renderClickableMarkdown(content, filename)

// Patterns:
// - TODOs: <li>...</li> → <li class="md-clickable">
// - Features: <li>F\d+:...</li> → <li class="md-clickable">
// - Bugs: <li>BUG-\d+:...</li> → <li class="md-clickable">
```

## Usage Examples

### Example 1: Start New Project

```
1. User: Click "➕ New project"
2. User: Enter "E-commerce API"
3. Backend: Creates ~/.ap/projects/e-commerce-api/
4. UI: Shows project in dropdown
5. UI: Auto-loads AGENTS.md, README.md, PRD.md (✅)
```

### Example 2: Work on TODO

```
1. User: Select "TODOs.md" → Click "Open"
2. UI: Opens tab [📋 TODOs.md]
3. User: Sees TODO list with clickable items
4. User: Click "TODO-1: Implement payment"
5. UI: Fills chat: "TODO-1: Implement payment"
6. User: Confirm send
7. Agent: "OK, rozumiem. Ako chceš implementovať payment?"
8. User continues brainstorming...
```

### Example 3: Report Bug

```
1. User: Open "BUGs.md"
2. User: Click "BUG-3: Checkout fails on mobile"
3. Chat: Pre-filled with bug description
4. User: Send
5. Agent: "Vidím bug. Potrebujem viac info..."
6. User: Provides details
7. Agent: Updates PRD.md with fix plan
```

## Benefits

### For Users
- **Zero Typing:** Klikni a pošli - hotovo!
- **Context Awareness:** Agent má loaded files (✅)
- **Visual Organization:** Tabs, colors, icons
- **Fast Navigation:** Dropdown + tabs
- **Session Continuity:** Všetko uložené v `~/.ap/`

### For Developers
- **File-based State:** Všetko v MD súboroch
- **Git Integration:** Version control built-in
- **Extensible:** Pridaj nový MD file type
- **API-driven:** REST + WebSocket
- **Template System:** Easy scaffolding

## Advanced Features

### Auto-update Timestamps

```python
def update_file(project_name, filename, content):
    # Auto-update "Last Updated: ..." line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Last Updated:' in line:
            lines[i] = f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}"
    
    # Save with git commit
    file_path.write_text('\n'.join(lines))
    git_commit(f"Update {filename}")
```

### Smart Patterns

```javascript
// Detect TODO item
/<li>\s*\[\s*\]\s*(TODO-\d+:.*?)<\/li>/

// Detect Feature
/<li>(F\d+:.*?)<\/li>/

// Detect Bug
/<li>\s*\[\s*\]\s*(BUG-\d+:.*?)<\/li>/

// Detect Requirement
/<li>(R\d+:.*?)<\/li>/
```

### Context Files

Files auto-loaded by agent:
1. **AGENTS.md** - Agent configuration & decisions
2. **README.md** - Project overview
3. **PRD.md** - Requirements & features

Why these 3?
- Agent needs context before first message
- User can see what agent knows (✅ checkmarks)
- Other files loaded on-demand

## Future Enhancements

1. **Inline Editing:** Edit MD directly in UI
2. **Drag & Drop:** Reorder TODOs/BUGs
3. **Templates:** Custom file templates
4. **Shortcuts:** Keyboard navigation
5. **Search:** Find across all MD files
6. **Sync:** Multi-device sync
7. **Export:** Export to PDF/DOCX
8. **Collaboration:** Multi-user editing

## Testing

```bash
# Test project workspace
python project_workspace.py

# Expected output:
# ✓ Created: ~/.ap/projects/blog-api
# ✓ Loaded 6 files for Blog API
# ✓ Context files: AGENTS.md, README.md, PRD.md
```

## References

- **Project Workspace:** `/project_workspace.py`
- **Backend API:** `/ap_studio_backend.py` (lines 240-270)
- **Frontend UI:** `/ap_studio.html` (lines 1088-1125, 2072-2325)
- **Templates:** `ProjectWorkspace.TEMPLATES` dict

---

**Built for effortless brainstorming - Click, don't type!** 🚀

