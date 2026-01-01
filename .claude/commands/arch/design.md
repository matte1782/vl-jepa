---
description: Create system architecture design document
---

# /arch:design — System Architecture

Design system architecture based on approved requirements.

## Usage

```
/arch:design
/arch:design $ARGUMENTS  # Focus on specific component
```

## Prerequisites

- Gate 0 complete (project_brief.md exists)
- Research done (docs/research/ populated) — recommended

## Protocol

### Step 1: Load Context

Read:
- `project_brief.md`
- `docs/PRD.md` (if exists)
- `docs/research/LITERATURE.md` (if exists)

### Step 2: Design Architecture

Invoke the **ARCHITECT** agent to create `docs/architecture/ARCHITECTURE.md`:

**Key Sections:**
1. **System Overview** — High-level description
2. **Components** — Each major module with:
   - Responsibility
   - Inputs/Outputs
   - Interfaces
   - Constraints
3. **Data Flow** — How data moves through the system
4. **Interfaces** — Protocol definitions
5. **Performance Budget** — Latency/memory targets
6. **Failure Modes** — What can go wrong and recovery
7. **Open Questions** — Unresolved design decisions

### Step 3: Create Supporting Documents

If needed:
- `docs/architecture/DATA_FLOW.md` — Detailed data pipeline
- `docs/architecture/API_DESIGN.md` — Interface contracts
- `docs/ADR/ADR-0001-*.md` — Key decisions

### Step 4: Handoff

```markdown
## ARCHITECT: Design Complete

Artifacts:
- docs/architecture/ARCHITECTURE.md
- docs/ADR/ADR-0001-encoder-selection.md (if applicable)

Status: PENDING_HOSTILE_REVIEW

Next: /review:hostile docs/architecture/ARCHITECTURE.md
```

## Arguments

- `$ARGUMENTS` — Component to focus on (e.g., "encoder", "event-detection")

## Output

- `docs/architecture/ARCHITECTURE.md`
- Optional: ADRs, data flow diagrams
