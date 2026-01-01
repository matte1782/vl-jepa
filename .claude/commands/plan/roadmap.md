---
description: Create development roadmap from architecture
---

# /plan:roadmap — Development Roadmap

Create a phased development roadmap based on approved architecture.

## Usage

```
/plan:roadmap
/plan:roadmap $ARGUMENTS  # Duration or focus
```

## Prerequisites

- Gate 1 complete (`.claude/gates/GATE_1_COMPLETE.md` exists)
- Architecture approved (`docs/architecture/ARCHITECTURE.md`)

## Protocol

### Step 1: Verify Gate

```bash
if [ ! -f ".claude/gates/GATE_1_COMPLETE.md" ]; then
  echo "ERROR: Gate 1 not complete. Run /arch:design first."
  exit 1
fi
```

### Step 2: Load Context

Read:
- `docs/architecture/ARCHITECTURE.md`
- `docs/PRD.md` (if exists)
- `project_brief.md`

### Step 3: Generate Roadmap

Invoke **PLANNER** agent to create `docs/planning/ROADMAP.md`:

**Required Sections:**
1. **Executive Summary** — Goal, duration, critical path
2. **Phases** — Logical groupings of work
3. **Milestones** — Checkpoints with Definition of Done
4. **Tasks** — Decomposed work (<8 hours each)
5. **Dependencies** — What blocks what
6. **Risk Register** — What could go wrong

**Estimation Rules:**
- Apply 2x multiplier to all estimates
- No task > 8 hours (decompose if larger)
- Include buffer between phases

### Step 4: Create Risk Register

Create `docs/planning/RISKS.md` with identified risks and mitigations.

### Step 5: Handoff

```markdown
## PLANNER: Roadmap Complete

Artifacts:
- docs/planning/ROADMAP.md
- docs/planning/RISKS.md

Total Duration: N weeks
Milestones: M
Critical Risks: R

Status: PENDING_HOSTILE_REVIEW

Next: /review:hostile docs/planning/ROADMAP.md
```

## Arguments

- `$ARGUMENTS` — Optional duration constraint or focus area

## Output

- `docs/planning/ROADMAP.md`
- `docs/planning/RISKS.md`
