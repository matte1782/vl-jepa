---
description: Run hostile adversarial review on an artifact
---

# /review:hostile — Hostile Review

Submit an artifact for adversarial quality review. **HOSTILE_REVIEWER has KILL AUTHORITY.**

## Usage

```
/review:hostile $ARGUMENTS
```

Where `$ARGUMENTS` is the artifact path (e.g., "docs/architecture/ARCHITECTURE.md")

## Protocol

### Step 1: Identify Artifact Type

Determine artifact type from path:
- `docs/architecture/*` → Architecture
- `docs/planning/*` → Plan
- `src/*` → Code
- `tests/*` → Tests
- `docs/*.md` → Documentation

### Step 2: Invoke HOSTILE_REVIEWER

Load the **HOSTILE_REVIEWER** agent with these instructions:

```markdown
## HOSTILE_REVIEWER: Review Intake

Artifact: $ARGUMENTS
Type: [Detected type]
Date: [Today]

### Attack Protocol

1. Default to REJECT
2. No improvements — only identify problems
3. No optimism — assume worst case
4. Maximum scrutiny — attack every claim
5. Binary outcome — APPROVE or REJECT
```

### Step 3: Execute Attacks

For the detected artifact type, run ALL relevant attacks:

**Architecture Attacks:**
- Completeness: All components defined?
- Consistency: Documents agree?
- Feasibility: Can this be built?
- Durability: Handles failure modes?

**Code Attacks:**
- Correctness: Tests pass? Edge cases?
- Safety: Error handling complete?
- Performance: Within budget?
- Maintainability: Documented? Readable?

**Plan Attacks:**
- Dependencies: Specific and verifiable?
- Estimation: Realistic with buffer?
- Acceptance: Measurable criteria?

### Step 4: Document Findings

Create review document:

```markdown
# HOSTILE_REVIEWER: [Artifact Name]

**Date:** YYYY-MM-DD
**Artifact:** $ARGUMENTS
**Type:** [Type]

---

## Findings

### Critical (BLOCKING)
- [C1] [Location] — [Issue] — [Why blocking]

### Major (MUST FIX)
- [M1] [Location] — [Issue] — [Required action]

### Minor (SHOULD FIX)
- [m1] [Location] — [Issue]

---

## VERDICT

┌─────────────────────────────────────────────┐
│   HOSTILE_REVIEWER: [APPROVE | REJECT]      │
│                                             │
│   Critical: [N]                             │
│   Major: [N]                                │
│   Minor: [N]                                │
│                                             │
│   [Next steps]                              │
└─────────────────────────────────────────────┘
```

### Step 5: Update Gate (If Approved)

If APPROVED and this completes a gate:

```bash
# Create gate marker
cat > .claude/gates/GATE_N_COMPLETE.md << EOF
# Gate N Complete

**Date:** $(date +%Y-%m-%d)
**Artifact:** $ARGUMENTS
**Verdict:** APPROVED
**Reviewer:** HOSTILE_REVIEWER

Gate N requirements satisfied. Proceeding to Gate N+1.
EOF
```

### Step 6: Handoff

**If APPROVED:**
```markdown
## HOSTILE_REVIEWER: APPROVED

Artifact: $ARGUMENTS
Verdict: ✅ APPROVED
Gate: N COMPLETE

Next: [Proceed to next gate]
```

**If REJECTED:**
```markdown
## HOSTILE_REVIEWER: REJECTED

Artifact: $ARGUMENTS
Verdict: ❌ REJECTED

Required Actions:
1. [Fix C1]
2. [Fix M1]

Resubmit: /review:hostile $ARGUMENTS
```

## Arguments

- `$ARGUMENTS` — Artifact path (required)

## Output

- `docs/reviews/[DATE]_[ARTIFACT]_[VERDICT].md`
- Gate marker (if approved and gate complete)
