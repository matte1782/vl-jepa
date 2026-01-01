---
description: Scan literature and related work for a topic
---

# /research:scan — Literature Scan

Research related work, prior art, and technical approaches.

## Usage

```
/research:scan $ARGUMENTS
```

Where `$ARGUMENTS` is the research topic (e.g., "video embeddings", "event detection")

## Protocol

### Step 1: Define Scope

Invoke **RESEARCH_LEAD** agent with:
- Topic: $ARGUMENTS
- Sources: Academic papers, GitHub, official docs

### Step 2: Gather Sources

Search for:
1. **Academic Papers** — arXiv, ACL, NeurIPS, CVPR
2. **Repositories** — GitHub, HuggingFace
3. **Documentation** — Official library docs
4. **Blog Posts** — Engineering blogs (mark as lower quality)

### Step 3: Document Findings

Create `docs/research/LITERATURE.md`:

```markdown
# Literature Review: $ARGUMENTS

**Date:** YYYY-MM-DD
**Author:** RESEARCH_LEAD
**Scope:** [What was researched]

---

## Key Papers

### 1. [Paper Title] (Author, Year)
**URL:** [Link]
**Relevance:** HIGH | MEDIUM | LOW

**Summary:**
[Key findings]

**Implications for Us:**
[How this affects our design]

### 2. [Paper Title]
[...]

---

## Related Projects

### [Project Name]
**URL:** [Link]
**Status:** Active | Archived

**Comparison:**
| Aspect | Them | Us |
|--------|------|-----|
| Approach | X | Y |

---

## Gaps Identified

1. [Gap] — Evidence: [Source]
2. [Gap] — Evidence: [Source]

---

## Recommendations

Based on this research:
1. [Recommendation 1]
2. [Recommendation 2]
```

### Step 4: Handoff

```markdown
## RESEARCH_LEAD: Scan Complete

Topic: $ARGUMENTS
Sources Reviewed: N
Key Papers: M

Artifact: docs/research/LITERATURE.md

Next: /arch:design (incorporate findings)
```

## Arguments

- `$ARGUMENTS` — Research topic (required)

## Output

- `docs/research/LITERATURE.md`
