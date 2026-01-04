# Week 3 Revised Plan

> **Created:** 2026-01-04
> **Revision:** Based on Week 2 completion + completed tasks
> **Status:** ACTIVE

---

## Context: What's Already Done

Tasks completed ahead of schedule (from Week 2 Day 5):

| Original Week 3 Task | Status | Evidence |
|---------------------|--------|----------|
| Multimodal index impl | ✅ DONE | 39 tests passing |
| Multimodal search impl | ✅ DONE | `search_multimodal()` works |
| Ranking algorithm | ✅ DONE | Weighted fusion in `RankingConfig` |
| End-to-end pipeline test | ✅ DONE | 8 integration tests |
| FAISS verification | ✅ DONE | Used by multimodal index |

---

## Week 3 Revised Focus

**Theme:** Real Model Integration + Environment Fix
**Hours:** 20h (adjusted for completed work)
**Priority:** Fix environment → Real model validation → Coverage

---

## Critical Issue to Fix First

**Text Encoder Environment Problem:**
- pytest Python has broken torchvision/pytorch
- Tests skip instead of run with real models
- Blocks CI validation

**Fix Strategy:**
```bash
# Create clean virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Day-by-Day Plan (Revised)

### Day 1 (Today): Environment Fix + Real Model Tests

| # | Task | Hours | Deliverable | PASS Criteria |
|---|------|-------|-------------|---------------|
| 1 | Create virtual environment | 0.5h | `.venv` working | All imports work |
| 2 | Verify all dependencies | 0.5h | Import tests | torch, sentence-transformers, whisper |
| 3 | Run full test suite in venv | 0.5h | All tests pass | No skipped real-model tests |
| 4 | Text encoder real model test | 1h | Real embeddings | 768-dim, semantic similarity |
| 5 | DINOv2 + text encoder combined | 1.5h | Both encoders | Multimodal search with real models |

**Total Day 1:** 4h

### Day 2: Video Pipeline with Real DINOv2

| # | Task | Hours | Deliverable | PASS Criteria |
|---|------|-------|-------------|---------------|
| 1 | Video processor with real DINOv2 | 2h | Real frame embeddings | Works on test video |
| 2 | Real model integration test | 1.5h | Integration test | Video → real embeddings |
| 3 | Performance baseline | 0.5h | Latency measurements | Document actual speeds |

**Total Day 2:** 4h

### Day 3: Full Pipeline Integration

| # | Task | Hours | Deliverable | PASS Criteria |
|---|------|-------|-------------|---------------|
| 1 | Real Whisper + real encoders | 2h | Full pipeline | Video → transcript → index |
| 2 | Audio-visual sync validation | 1h | Sync test | Timestamps align ±1s |
| 3 | Query with real embeddings | 1h | Search works | Semantic results returned |

**Total Day 3:** 4h

### Day 4: Coverage + Polish

| # | Task | Hours | Deliverable | PASS Criteria |
|---|------|-------|-------------|---------------|
| 1 | Coverage analysis | 0.5h | Report | Identify gaps |
| 2 | Add tests for low-coverage modules | 2h | New tests | +5% coverage |
| 3 | CI configuration update | 1h | Updated workflow | Uses venv approach |
| 4 | Buffer | 0.5h | - | Catch up |

**Total Day 4:** 4h

### Day 5: Week 3 Review

| # | Task | Hours | Deliverable | PASS Criteria |
|---|------|-------|-------------|---------------|
| 1 | Full test suite verification | 0.5h | All pass | No failures |
| 2 | Coverage check | 0.5h | Report | >= 62% |
| 3 | Performance documentation | 1h | BENCHMARKS.md started | Key metrics documented |
| 4 | Hostile review | 1h | Review doc | GO/NO-GO |
| 5 | Week 3 summary | 1h | Daily log update | Complete |

**Total Day 5:** 4h

---

## Week 3 Exit Criteria (Revised)

```
[ ] Virtual environment created and working
[ ] All real-model tests pass (no skips for env issues)
[ ] sentence-transformers produces 768-dim embeddings
[ ] DINOv2 + text encoder work together
[ ] Full pipeline: Video → Whisper → Encoders → Index → Query
[ ] Audio-visual timestamps align ±1 second
[ ] Performance baselines documented
[ ] Coverage >= 62%
[ ] Hostile review APPROVED
```

---

## Risk Adjustments

| Original Risk | Status | Adjustment |
|--------------|--------|------------|
| FAISS issues | ✅ Resolved | Already working |
| Multimodal index | ✅ Resolved | Already complete |
| Text encoder env | ⚠️ ACTIVE | Priority fix Day 1 |
| DINOv2 speed | ⚠️ To measure | Day 2 baseline |

---

## Carryover from Week 2

None - all Week 2 tasks complete.

---

## Deferred to Week 4

- Full benchmark suite (just baselines in Week 3)
- Coverage push to 67% (target 62% for Week 3)

---

*Revised plan accounts for ahead-of-schedule work. Focus on environment fix and real model validation.*
