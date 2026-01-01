---
description: Implement ML feature using TDD strict mode
---

# /ml:implement — ML Implementation (TDD)

Implement a task from the weekly plan using strict TDD.

## Usage

```
/ml:implement $ARGUMENTS
```

Where `$ARGUMENTS` is the task ID (e.g., "W1.1", "W2.3")

## Prerequisites

- Weekly plan approved for this task
- Test stubs exist for the task
- Gate 4 complete (planning approved)

## Protocol

### Step 1: Load Task

Read:
- `docs/planning/weeks/WEEK_N.md` — Find task details
- Test stubs for this task
- Relevant architecture docs

### Step 2: Verify Test Stubs Exist

```bash
# Ensure test file exists with stubs
grep -r "TEST_ID: T00X" tests/
```

If no stubs exist, create them first via `/qa:generate`.

### Step 3: TDD Cycle

Invoke **ML_ENGINEER** agent in TDD strict mode:

```
┌─────────────────────────────────────────────┐
│              TDD STRICT MODE                 │
├─────────────────────────────────────────────┤
│ 1. REMOVE @pytest.mark.skip from test       │
│ 2. RUN TEST → Must FAIL (Red)               │
│ 3. WRITE minimal code to pass               │
│ 4. RUN TEST → Must PASS (Green)             │
│ 5. REFACTOR if needed                       │
│ 6. COMMIT with trace                        │
│ 7. REPEAT for next test                     │
└─────────────────────────────────────────────┘
```

### Step 4: Quality Checks

After all tests pass:

```bash
# Format
ruff format src/

# Lint
ruff check src/

# Type check
mypy src/ --strict

# Tests with coverage
pytest tests/ -v --cov=src/vl_jepa --cov-report=term
```

### Step 5: Commit

```bash
git add src/ tests/
git commit -m "feat(SXXX): Implement [feature]

IMPLEMENTS: SXXX
TESTS: TXXX.1, TXXX.2
INVARIANTS: INVXXX

- [Change 1]
- [Change 2]"
```

### Step 6: Handoff

```markdown
## ML_ENGINEER: Task Complete

Task: WN.X
Spec: SXXX

Artifacts:
- src/vl_jepa/[module].py
- tests/unit/test_[module].py

Tests: All pass
Coverage: XX%
Type Check: Clean

Status: PENDING_HOSTILE_REVIEW

Next: /review:hostile src/vl_jepa/[module].py
```

## Arguments

- `$ARGUMENTS` — Task ID from weekly plan (required, e.g., "W1.1")

## Output

- Implementation code in `src/`
- Passing tests in `tests/`
- Git commit with trace
