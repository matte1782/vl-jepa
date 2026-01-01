# VL-JEPA Quality Gates

> **FORTRESS 2.0 Gate System**
> Gates cannot be skipped. Each gate must be completed before proceeding.

---

## Gate Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GATE SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────┤
│  GATE 0: Problem Definition     → project_brief.md                  │
│  GATE 1: Architecture           → docs/architecture/ARCHITECTURE.md │
│  GATE 2: Specification          → docs/SPECIFICATION.md             │
│  GATE 3: Test Design            → docs/TEST_STRATEGY.md + stubs     │
│  GATE 4: Planning               → docs/planning/ROADMAP.md          │
│  GATE 5: Implementation         → src/ + passing tests              │
│  GATE 6: Validation             → HOSTILE_REVIEWER comprehensive    │
│  GATE 7: Release                → README.md + CHANGELOG.md          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Gate Details

### Gate 0: Problem Definition

**Status Marker:** `.claude/gates/GATE_0_COMPLETE.md`

**Requirements:**
- [ ] `project_brief.md` exists
- [ ] Problem statement is clear
- [ ] Target users identified
- [ ] Success metrics defined
- [ ] Constraints documented

**Command:** N/A (manual)

---

### Gate 1: Architecture

**Status Marker:** `.claude/gates/GATE_1_COMPLETE.md`

**Requirements:**
- [ ] `docs/architecture/ARCHITECTURE.md` exists
- [ ] All components defined
- [ ] Data flows documented
- [ ] Interfaces specified
- [ ] Performance budgets set
- [ ] Failure modes analyzed
- [ ] HOSTILE_REVIEWER approved

**Command:** `/arch:design`

**Review:** `/review:hostile docs/architecture/ARCHITECTURE.md`

---

### Gate 2: Specification

**Status Marker:** `.claude/gates/GATE_2_COMPLETE.md`

**Requirements:**
- [ ] `docs/SPECIFICATION.md` exists
- [ ] All specs numbered (S001, S002, ...)
- [ ] Invariants defined (INV001, ...)
- [ ] Edge cases documented
- [ ] HOSTILE_REVIEWER approved

**Command:** Create SPECIFICATION.md from architecture

**Review:** `/review:hostile docs/SPECIFICATION.md`

---

### Gate 3: Test Design

**Status Marker:** `.claude/gates/GATE_3_COMPLETE.md`

**Requirements:**
- [ ] `docs/TEST_STRATEGY.md` exists
- [ ] `docs/TEST_MATRIX.md` maps specs to tests
- [ ] Test stubs exist in `tests/`
- [ ] Coverage targets defined (>90%)
- [ ] HOSTILE_REVIEWER approved

**Command:** `/qa:testplan`

**Review:** `/review:hostile docs/TEST_STRATEGY.md`

---

### Gate 4: Planning

**Status Marker:** `.claude/gates/GATE_4_COMPLETE.md`

**Requirements:**
- [ ] `docs/planning/ROADMAP.md` exists
- [ ] Tasks decomposed (<8 hours each)
- [ ] Dependencies explicit
- [ ] Acceptance criteria measurable
- [ ] Risk register complete
- [ ] HOSTILE_REVIEWER approved

**Command:** `/plan:roadmap`

**Review:** `/review:hostile docs/planning/ROADMAP.md`

**Unlocks:** Write access to `src/`

---

### Gate 5: Implementation

**Status Marker:** `.claude/gates/GATE_5_COMPLETE.md`

**Requirements:**
- [ ] All planned tasks complete
- [ ] All tests pass
- [ ] Coverage >90%
- [ ] Type check clean (`mypy --strict`)
- [ ] Lint clean (`ruff check`)
- [ ] Each task reviewed by HOSTILE_REVIEWER

**Command:** `/ml:implement WN.X` (per task)

**Review:** `/review:hostile src/vl_jepa/`

---

### Gate 6: Validation

**Status Marker:** `.claude/gates/GATE_6_COMPLETE.md`

**Requirements:**
- [ ] Comprehensive hostile review passed
- [ ] Security review complete
- [ ] Performance benchmarks met
- [ ] No critical issues
- [ ] No major issues

**Command:** `/review:hostile --comprehensive`

---

### Gate 7: Release

**Status Marker:** `.claude/gates/GATE_7_COMPLETE.md`

**Requirements:**
- [ ] README.md complete
- [ ] CHANGELOG.md updated
- [ ] API docs generated
- [ ] Release checklist passed
- [ ] HOSTILE_REVIEWER final approval

**Command:** `/release:checklist`

**Review:** `/review:hostile README.md`

---

## Gate Enforcement

### Automatic Checks

The `.claude/settings.json` includes hooks that:
1. **PreToolUse:** Warn if writing code before Gate 4
2. **UserPromptSubmit:** Show current gate status

### Manual Verification

Before proceeding to next gate:
1. Verify gate marker exists: `ls .claude/gates/GATE_N_COMPLETE.md`
2. Verify artifacts exist
3. Verify HOSTILE_REVIEWER approval

---

## HOSTILE_REVIEWER Protocol

The HOSTILE_REVIEWER has **KILL AUTHORITY**:

1. **Default to REJECT** — Burden of proof on artifact
2. **No improvements** — Only identify problems
3. **Binary outcome** — APPROVE or REJECT

### Review Criteria

| Issue Level | Action |
|-------------|--------|
| Critical | BLOCK — Must fix before proceeding |
| Major | MUST FIX — Cannot merge without fixing |
| Minor | SHOULD FIX — Can proceed with tracking |

---

## Override Protocol

If absolutely necessary, human can override with:

```markdown
[HUMAN_OVERRIDE]
Reason: [Explicit justification]
Risk Accepted: [What could go wrong]
```

Document in git commit and proceed with explicit acknowledgment.

---

*FORTRESS 2.0 — Gates exist because bugs escape reviews, but they don't escape gates.*
