# VL-JEPA Lecture Summarizer

> **Framework**: FORTRESS 4.1.1 — Minimal Viable Framework
> **Principle**: AI prepares, Human decides

---

## Mission

Build an event-aware lecture summarizer using VL-JEPA that provides students with real-time, context-aware summaries and retrieval of lecture segments.

**Users**: Students and teaching staff
**Deployment**: Local-first (laptop CPU/GPU)

---

## Build Commands

```bash
# Install
pip install -e ".[dev]"

# Test
pytest tests/ -v

# Lint & Format
ruff check src/ && ruff format src/

# Type Check
mypy src/ --strict

# Run Demo
python -m vl_jepa.demo --video lecture.mp4
```

---

## Code Style

- Python 3.10+, type hints required on all functions
- **TDD**: Write tests before implementation
- Formatting: `ruff format`
- Linting: `ruff check` (no warnings)
- Coverage target: >90%

---

## Anti-Patterns (Learned)

- Don't skip TDD — write failing tests first
- Don't use `unwrap()` equivalents — handle errors explicitly
- Don't over-engineer — simplest solution that works
- Don't commit without tests passing

---

## Review Workflow

When I request a review with subagent:
1. Write findings directly to `docs/reviews/REVIEW_[type].md`
2. Include confidence scores (0-100) for each issue
3. I will read the file and decide GO/NO_GO

**Format:**
```markdown
## Summary
- Issues: X critical, Y major, Z minor
- Recommendation: READY / CAUTION / BLOCK

## Critical Issues (80%+ confidence)
### 1. [Title]
**Location:** `file.py:42`
**Issue:** [Description]
**Suggested Fix:** [How to fix]
```

---

## Current Focus

See `docs/ROADMAP.md` for current goals and tasks.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| ML Framework | PyTorch |
| Video | OpenCV, decord |
| Embeddings | V-JEPA ViT-L/16 |
| Text Encoder | all-MiniLM-L6 |
| Decoder | Gemma-2B / Llama-3 8B |
| Search | FAISS |
| Testing | pytest, hypothesis |
| Linting | ruff, mypy |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Frame embedding | <50ms (GPU), <200ms (CPU) |
| Event detection | <10ms |
| Query latency | <100ms (100k embeddings) |
| Memory | <4GB for 2hr lecture |

---

## Natural Language Patterns

Just describe what you want. No commands needed.

**Planning:**
- "Plan version X.Y.Z" → Updates ROADMAP.md
- "What should I work on next?" → Reads ROADMAP.md

**Implementation:**
- "Implement [feature]" → Explore → Plan → TDD → Implement
- "Fix [bug]" → Diagnose → Fix → Test

**Review:**
- "Review this change" → Single-pass review
- "Deep security review, use subagent, write to REVIEW_security.md"

**Status:**
- "Where are we?" → Shows progress from ROADMAP.md

---

## Links

- **V-JEPA Paper**: https://arxiv.org/abs/2312.15213
- **V-JEPA Code**: https://github.com/facebookresearch/jepa
- **Project Brief**: `./project_brief.md`

---

*FORTRESS 4.1.1 — Simplest solution that works. AI prepares, Human decides.*
