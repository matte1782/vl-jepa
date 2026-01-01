---
description: Run the full development pipeline from current state to release
---

# /pipeline:all — Full Pipeline

Orchestrate the complete development lifecycle.

## Usage

```
/pipeline:all
/pipeline:all --from N     # Start from gate N
/pipeline:all --to N       # Stop at gate N
/pipeline:all --dry-run    # Show plan without executing
```

## Protocol

### Step 1: Assess Current State

Invoke **ORCHESTRATOR** agent to check gate status:

```bash
# Check completed gates
ls -la .claude/gates/GATE_*_COMPLETE.md 2>/dev/null

# Determine current gate
for i in $(seq 0 7); do
  if [ ! -f ".claude/gates/GATE_${i}_COMPLETE.md" ]; then
    echo "Current Gate: $i"
    break
  fi
done
```

### Step 2: Execute Pipeline

For each incomplete gate, execute in order:

```
┌─────────────────────────────────────────────────────────────────┐
│ GATE 0: Problem Definition                                       │
│ ├── Status: Check project_brief.md exists                       │
│ └── If incomplete: Ask user to provide project brief            │
├─────────────────────────────────────────────────────────────────┤
│ GATE 1: Architecture                                             │
│ ├── Command: /arch:design                                        │
│ ├── Review: /review:hostile docs/architecture/ARCHITECTURE.md   │
│ └── Output: .claude/gates/GATE_1_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 2: Specification                                            │
│ ├── Command: Create SPECIFICATION.md from architecture          │
│ ├── Review: /review:hostile docs/SPECIFICATION.md               │
│ └── Output: .claude/gates/GATE_2_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 3: Test Design                                              │
│ ├── Command: /qa:testplan                                        │
│ ├── Review: /review:hostile docs/TEST_STRATEGY.md               │
│ └── Output: .claude/gates/GATE_3_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 4: Planning                                                 │
│ ├── Command: /plan:roadmap, /plan:weekly 1                      │
│ ├── Review: /review:hostile docs/planning/ROADMAP.md            │
│ └── Output: .claude/gates/GATE_4_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 5: Implementation                                           │
│ ├── For each task in weekly plan:                               │
│ │   ├── Command: /ml:implement WN.X                             │
│ │   └── Review: /review:hostile (per task)                      │
│ └── Output: .claude/gates/GATE_5_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 6: Validation                                               │
│ ├── Command: Comprehensive hostile review                        │
│ ├── Review: /review:hostile --comprehensive                     │
│ └── Output: .claude/gates/GATE_6_COMPLETE.md                    │
├─────────────────────────────────────────────────────────────────┤
│ GATE 7: Release                                                  │
│ ├── Command: /docs:write README, /release:checklist             │
│ ├── Review: /review:hostile README.md                           │
│ └── Output: Release ready                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Handle Blockers

If a gate fails review:
1. **STOP** — Do not proceed
2. **Document** — Log failure reason
3. **Fix** — Address issues
4. **Retry** — Re-run the gate

### Step 4: Report Progress

After each gate:

```markdown
## ORCHESTRATOR: Pipeline Progress

Gates Complete: X/7
Current Gate: N
Status: [IN_PROGRESS | BLOCKED | COMPLETE]

### Completed
- Gate 0: ✅
- Gate 1: ✅
- Gate 2: ✅

### In Progress
- Gate 3: 🔄 Awaiting hostile review

### Blocked
- Gate 4-7: ⏸️ Waiting for Gate 3

Next Action: /review:hostile docs/TEST_STRATEGY.md
```

### Step 5: Final Report

When pipeline completes:

```markdown
## ORCHESTRATOR: Pipeline Complete

All Gates: ✅ COMPLETE

Artifacts:
- docs/architecture/ARCHITECTURE.md
- docs/SPECIFICATION.md
- docs/TEST_STRATEGY.md
- docs/planning/ROADMAP.md
- src/vl_jepa/ (implementation)
- tests/ (all passing)
- README.md

Status: READY FOR RELEASE

Next: Tag release, publish
```

## Arguments

- `--from N` — Start from specific gate (skip earlier gates)
- `--to N` — Stop at specific gate
- `--dry-run` — Show plan without executing

## Output

- Progress through all gates
- Gate completion markers
- Final release readiness report
