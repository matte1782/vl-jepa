---
description: Create test strategy and test matrix
---

# /qa:testplan — Test Strategy

Create comprehensive test strategy and spec-to-test mapping.

## Usage

```
/qa:testplan
/qa:testplan $ARGUMENTS  # Focus area
```

## Prerequisites

- Specification exists (`docs/SPECIFICATION.md` or architecture)
- Gate 2 progress (specification phase)

## Protocol

### Step 1: Load Context

Read:
- `docs/architecture/ARCHITECTURE.md`
- `docs/SPECIFICATION.md` (if exists)
- `project_brief.md`

### Step 2: Generate Test Strategy

Invoke **QA_LEAD** agent to create `docs/TEST_STRATEGY.md`:

```markdown
# VL-JEPA Test Strategy

**Version:** 1.0.0
**Author:** QA_LEAD
**Coverage Target:** >90%

---

## Test Pyramid

```
         E2E (few)
        ─────────
       Integration
      ─────────────
         Unit (many)
```

## Test Categories

### Unit Tests (tests/unit/)
- Scope: Single function/class
- Speed: <100ms each
- Mocking: External deps mocked

### Integration Tests (tests/integration/)
- Scope: Component interactions
- Speed: <5s each
- Mocking: Minimal

### Property Tests (tests/property/)
- Framework: hypothesis
- Scope: Invariant validation

### Performance Tests (tests/perf/)
- Framework: pytest-benchmark
- Scope: Latency/throughput

## Coverage Requirements

| Module | Target | Priority |
|--------|--------|----------|
| encoder | >90% | HIGH |
| event | >90% | HIGH |
| retrieval | >90% | HIGH |
| ui | >80% | MEDIUM |

## Edge Case Checklist

- [ ] Empty input
- [ ] Single item
- [ ] Maximum size
- [ ] Invalid type
- [ ] Boundary values
```

### Step 3: Generate Test Matrix

Create `docs/TEST_MATRIX.md`:

```markdown
# Spec-to-Test Matrix

| Spec | Description | Tests | Status |
|------|-------------|-------|--------|
| S001 | Encoder output | T001.1, T001.2 | STUB |
| S002 | Event detection | T002.1-T002.3 | STUB |
```

### Step 4: Create Test Stubs

Generate test stub files in `tests/` with `@pytest.mark.skip`.

### Step 5: Handoff

```markdown
## QA_LEAD: Test Strategy Complete

Artifacts:
- docs/TEST_STRATEGY.md
- docs/TEST_MATRIX.md
- tests/unit/test_*.py (stubs)

Total Stubs: N
Coverage Target: >90%

Status: PENDING_HOSTILE_REVIEW

Next: /review:hostile docs/TEST_STRATEGY.md
```

## Arguments

- `$ARGUMENTS` — Optional focus area (e.g., "encoder", "event")

## Output

- `docs/TEST_STRATEGY.md`
- `docs/TEST_MATRIX.md`
- Test stub files in `tests/`
