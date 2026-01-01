---
description: Create an Architecture Decision Record
---

# /arch:adr — Architecture Decision Record

Document a significant architectural decision.

## Usage

```
/arch:adr $ARGUMENTS
```

Where `$ARGUMENTS` is the decision title (e.g., "Use V-JEPA over CLIP")

## Protocol

### Step 1: Get Next ADR Number

```bash
ls docs/ADR/ | grep "ADR-" | tail -1
```

### Step 2: Create ADR

Create `docs/ADR/ADR-NNNN-[slug].md`:

```markdown
# ADR-NNNN: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded
**Deciders:** [Who made this decision]
**Supersedes:** [ADR-XXXX if applicable]

---

## Context

[What is the issue we're addressing? Why does this decision need to be made?]

## Decision

[What is the change we're making? Be specific and actionable.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Tradeoff 1]
- [Tradeoff 2]

### Risks
- [Risk 1] — Mitigation: [How we address it]

## Alternatives Considered

### Option A: [Name]
- **Description:** [What is this option?]
- **Pros:** [Benefits]
- **Cons:** [Drawbacks]
- **Why rejected:** [Reason]

### Option B: [Name]
[...]

## References

- [Link 1]
- [Link 2]
```

### Step 3: Link to Architecture

Update `docs/architecture/ARCHITECTURE.md` to reference the new ADR.

### Step 4: Handoff

```markdown
## ARCHITECT: ADR Created

Artifact: docs/ADR/ADR-NNNN-[slug].md
Decision: [Brief summary]

Status: PROPOSED

Next: Review with stakeholders
```

## Arguments

- `$ARGUMENTS` — Decision title (required)

## Output

- `docs/ADR/ADR-NNNN-[slug].md`
