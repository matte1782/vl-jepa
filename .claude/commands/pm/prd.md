---
description: Create a Product Requirements Document from the project brief
---

# /pm:prd — Product Requirements Document

Create a comprehensive PRD based on the project brief.

## Usage

```
/pm:prd
/pm:prd $ARGUMENTS  # Additional context or focus areas
```

## Protocol

### Step 1: Load Context

Read the following files:
- `project_brief.md` — Original requirements
- `docs/research/LITERATURE.md` — If exists, research findings

### Step 2: Generate PRD

Create `docs/PRD.md` with this structure:

```markdown
# Product Requirements Document: VL-JEPA Lecture Summarizer

**Version:** 1.0.0
**Date:** YYYY-MM-DD
**Author:** Product Manager
**Status:** DRAFT

---

## 1. Executive Summary

[One paragraph overview]

## 2. Problem Statement

### 2.1 Current Pain Points
- [Pain point 1]
- [Pain point 2]

### 2.2 Target Users
- Primary: [User type 1]
- Secondary: [User type 2]

## 3. Solution Overview

[How VL-JEPA addresses the problems]

## 4. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Event detection accuracy | Precision/Recall | >80% |
| Search relevance | Recall@10 | >85% |
| Latency | P95 frame processing | <200ms |
| User satisfaction | Survey score | >4/5 |

## 5. Features (MVP)

### 5.1 P0 — Must Have
- [ ] Video ingestion and frame sampling
- [ ] Embedding computation (V-JEPA)
- [ ] Event boundary detection
- [ ] Basic Q&A interface

### 5.2 P1 — Should Have
- [ ] Summary export
- [ ] Timestamp navigation

### 5.3 P2 — Nice to Have
- [ ] Real-time streaming
- [ ] Multi-language support

## 6. Non-Functional Requirements

### 6.1 Performance
- Frame encoding: <50ms (GPU), <200ms (CPU)
- Query latency: <100ms

### 6.2 Privacy
- All processing local by default
- No data transmission without consent

### 6.3 Compatibility
- Python 3.10+
- Works on CPU (degraded) and GPU

## 7. Constraints

- 4-8 week MVP timeline
- Must work without VL-JEPA weights (fallback to V-JEPA + text encoder)
- Local-first architecture

## 8. Out of Scope (MVP)

- Cloud deployment
- Real-time collaboration
- Mobile app

## 9. Open Questions

- [Q1] [Question with owner]
- [Q2] [Question with owner]

## 10. Appendix

### A. User Stories
### B. Wireframes (if any)
### C. Technical Constraints
```

### Step 3: Handoff

```markdown
## PM: PRD Complete

Artifact: docs/PRD.md
Status: DRAFT

Next: /review:hostile docs/PRD.md
```

## Arguments

- `$ARGUMENTS` — Optional focus areas or additional context to incorporate

## Output

- `docs/PRD.md` — Product Requirements Document
