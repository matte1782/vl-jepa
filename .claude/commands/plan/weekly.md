---
description: Create weekly task plan for implementation
---

# /plan:weekly — Weekly Task Plan

Create a detailed task plan for a specific week.

## Usage

```
/plan:weekly $ARGUMENTS
```

Where `$ARGUMENTS` is the week number (e.g., "1", "2")

## Prerequisites

- Roadmap approved (`docs/planning/ROADMAP.md`)
- Gate 4 progress (planning phase)

## Protocol

### Step 1: Load Context

Read:
- `docs/planning/ROADMAP.md`
- `docs/TEST_STRATEGY.md` (if exists)
- Previous week's plan (if applicable)

### Step 2: Create Directory

```bash
mkdir -p docs/planning/weeks
```

### Step 3: Generate Weekly Plan

Create `docs/planning/weeks/WEEK_N.md`:

```markdown
# Week N Task Plan

**Date Range:** YYYY-MM-DD to YYYY-MM-DD
**Goal:** [One sentence describing week's objective]
**Status:** DRAFT

---

## Prerequisites

- [x] Previous week complete (or N/A for Week 1)
- [x] Dependencies resolved
- [ ] HOSTILE_REVIEWER approval

---

## Approved Tasks

| ID | Task | Hours | Owner | Spec | Acceptance |
|----|------|-------|-------|------|------------|
| WN.1 | [Task description] | 4 | ML_ENGINEER | S001 | `pytest test_X` passes |
| WN.2 | [Task description] | 6 | ML_ENGINEER | S002 | Output shape correct |

**Total Hours:** X

---

## Task Details

### WN.1: [Task Name]

**Description:** [What needs to be done]
**Spec Reference:** S001
**Test Reference:** T001.1, T001.2

**Acceptance Criteria:**
- [ ] Test `test_X` passes
- [ ] Type check passes
- [ ] >90% coverage

**Files to Create/Modify:**
- `src/vl_jepa/module.py`
- `tests/unit/test_module.py`

---

## Blocked Tasks

| ID | Task | Blocked By | Unblock Condition |
|----|------|------------|-------------------|
| WN.B1 | [Task] | WN.2 | Encoder working |

---

## Not In Scope

| Task | Why Deferred |
|------|--------------|
| [Task] | [Reason] |

---

## Completion Criteria

This week is COMPLETE when:
- [ ] All tasks in "Approved Tasks" done
- [ ] All tests pass
- [ ] Coverage >90%
- [ ] Type check clean
- [ ] HOSTILE_REVIEWER approves
```

### Step 4: Handoff

```markdown
## PLANNER: Week N Plan Complete

Artifact: docs/planning/weeks/WEEK_N.md
Tasks: X
Hours: Y

Status: PENDING_HOSTILE_REVIEW

Next: /review:hostile docs/planning/weeks/WEEK_N.md
```

## Arguments

- `$ARGUMENTS` — Week number (required, e.g., "1")

## Output

- `docs/planning/weeks/WEEK_N.md`
