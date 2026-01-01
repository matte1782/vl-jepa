---
description: Initialize FORTRESS 4.1.1 project structure for a new project
---

# /init — Project Initialization

Initialize or verify FORTRESS 4.1.1 project structure.

## What This Does

Creates the minimal required files if they don't exist:

1. **CLAUDE.md** — Project DNA with build commands, code style, review workflow
2. **docs/ROADMAP.md** — Flat task checklist with goals and progress
3. **docs/ARCHITECTURE.md** — Simple system overview
4. **docs/DECISIONS.md** — Key decision log
5. **docs/reviews/** — Directory for review output files
6. **.claude/settings.json** — Minimal hooks (PreCommit only)
7. **SCRATCHPAD.md** — Optional working memory file

## For Existing Projects

If files already exist, verify structure and report status.

## Usage

```
/init
```

Or just say: "Initialize project structure"

## After Init

1. Update CLAUDE.md with your project specifics
2. Add initial goals to ROADMAP.md
3. Start working — describe what you want in natural language

---

*FORTRESS 4.1.1 — One command to set up, natural language for everything else.*
