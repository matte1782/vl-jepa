---
description: Write documentation for a topic
---

# /docs:write — Write Documentation

Create or update documentation for a specific topic.

## Usage

```
/docs:write $ARGUMENTS
```

Where `$ARGUMENTS` is the doc type or topic (e.g., "README", "installation", "api")

## Protocol

### Step 1: Determine Document Type

| Argument | Output File | Purpose |
|----------|-------------|---------|
| README | README.md | Project overview |
| installation | docs/installation.md | Setup guide |
| api | docs/api/ | API reference |
| contributing | CONTRIBUTING.md | Contribution guide |
| changelog | CHANGELOG.md | Version history |

### Step 2: Load Context

Read relevant source files:
- `src/` for API docs
- `project_brief.md` for README
- Git history for CHANGELOG

### Step 3: Invoke DOCS_WRITER

Create documentation following templates in the DOCS_WRITER agent.

**Key Principles:**
- Audience first
- Examples over theory
- Test all code snippets
- Progressive disclosure

### Step 4: Quality Check

- [ ] All code examples run
- [ ] Links are valid
- [ ] No outdated info
- [ ] Consistent formatting

### Step 5: Handoff

```markdown
## DOCS_WRITER: Documentation Complete

Topic: $ARGUMENTS
File: [output file]

Sections: N
Code Examples: M (all tested)

Next: /review:hostile [file]
```

## Arguments

- `$ARGUMENTS` — Document type or topic (required)

## Output

- Varies by argument (see table above)
