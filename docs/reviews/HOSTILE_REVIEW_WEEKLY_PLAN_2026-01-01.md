# HOSTILE_VALIDATOR Report

> **Date**: 2026-01-01
> **Scope**: Planning (v0.2.0 Weekly Plan)
> **Artifact**: `docs/planning/WEEKLY_PLAN_V0.2.0.md`
> **Reviewer**: HOSTILE_VALIDATOR

---

## VERDICT: ❌ NO_GO

**BLOCKED. Cannot proceed with current plan.**

---

## Executive Summary

The plan has **6 critical issues** and **8 major issues** that will cause schedule failure if not addressed. The plan underestimates model download times, lacks fallback strategies, and has inconsistent targets.

---

## 1. Critical Issues (Must Fix Before Approval)

### C1: Model Download Times Not Accounted

| Model | Size | Download Time (50Mbps) | Allocated |
|:------|:-----|:----------------------|:----------|
| DINOv2 ViT-L/16 | ~1.2 GB | 3-5 min | 0 min |
| sentence-transformers | ~90 MB | 15 sec | 0 min |
| faster-whisper base | ~150 MB | 25 sec | 0 min |
| **Total first-run overhead** | | **~10-15 min** | **0 min** |

**Impact**: Week 2 Wednesday could slip by 1+ hour on first run.

**Fix**: Add explicit "Model download + cache verification" task (1h).

---

### C2: FFmpeg Dependency Not Verified

Audio extraction (Week 2 Friday) requires FFmpeg installed system-wide.

```
Current plan: No FFmpeg verification task
Risk: "FFmpeg not found" error blocks audio extraction
```

**Fix**: Add "Verify FFmpeg installation" task (15 min) before audio extraction.

---

### C3: No Fallback If DINOv2 Similarity < 0.85

Plan states PASS criteria: "Similar frames cosine > 0.85"

**What if it fails?**
- Current plan: Silent
- Risk: Entire approach invalidated, no contingency

**Fix**: Add decision tree:
```
IF similarity < 0.85:
  → Try CLIP encoder (fallback)
  → IF still fails: STOP, re-evaluate architecture
```

---

### C4: Package Name Inconsistency

| Location | Package Name |
|:---------|:-------------|
| pyproject.toml | `vl-jepa` |
| Plan (Week 5) | `lecture-mind` |
| Roadmap | `lecture-mind` |

**Impact**: PyPI publish will fail or publish wrong name.

**Fix**: Decide NOW: Is it `vl-jepa` or `lecture-mind`? Update all references.

---

### C5: Coverage Jump Unrealistic

| Week | Target | Delta |
|:-----|:-------|:------|
| Week 2 | >58% | baseline |
| Week 4 | >70% | **+12%** |

**12% coverage increase in 2 weeks is aggressive.**

Current test count: 91 passing
To reach 70% from 58%: Need ~20-30 additional tests

**Fix**:
- Week 3 exit criteria: >62%
- Week 4 exit criteria: >67%
- Week 5 exit criteria: >70%

---

### C6: Whisper Not Tested on Real Audio

Plan has:
- ✅ PlaceholderTranscriber tests
- ❌ WhisperTranscriber integration test

**No task verifies Whisper actually transcribes the lecture video.**

**Fix**: Add "Whisper integration test on lecture video" (Week 2, 2h).

---

## 2. Major Issues (Should Fix)

### M1: No GPU Availability Verification

Plan mentions "GPU benchmarks" but no task to:
- Check CUDA availability
- Verify torch.cuda.is_available()
- Document GPU model/memory

**Fix**: Add "GPU environment check" task (30 min).

---

### M2: FAISS Installation Not Verified

Multimodal index (Week 3) requires FAISS:
```python
import faiss  # Not verified anywhere
```

**Fix**: Add FAISS verification in Week 3 Day 1.

---

### M3: TestPyPI Account Setup Missing

Week 5 Thursday assumes TestPyPI publish works.

Requirements not mentioned:
- PyPI account creation
- API token generation
- `.pypirc` configuration

**Fix**: Add "PyPI account setup" task (30 min) or document as prerequisite.

---

### M4: Memory Profiling Missing

Roadmap acceptance criteria: "memory <4GB for 2hr lecture"

Plan has NO memory profiling task.

**Fix**: Add "Memory profiling on 1hr video" (Week 4, 1h).

---

### M5: No Rollback Plan for Failed Release

What if PyPI publish fails on Friday?
- Name collision
- Package rejected
- Network error

**Fix**: Add contingency: "If PyPI fails, debug Monday, release Tuesday."

---

### M6: Debug Buffer Insufficient

| Week | Debug Buffer | Complex Tasks |
|:-----|:-------------|:--------------|
| Week 2 | 2h | DINOv2, Whisper, FFmpeg |
| Week 3 | 2h | FAISS, multimodal ranking |
| Week 4 | 2h | Benchmarks, coverage |

**2h buffer for weeks with 3+ complex integrations is risky.**

**Fix**: Increase Week 2-3 buffer to 4h each (reduce other task estimates).

---

### M7: Week Numbering Confusing

Document says "4 weeks" but labels them Week 2-5.

- Is Week 1 = Gate 0 (already done)?
- Or is this Weeks 1-4 mislabeled?

**Fix**: Clarify: "Weeks 2-5 (v0.2.0 development, Week 1 was Gate 0)"

---

### M8: No Integration Test for Audio+Visual Sync

Week 2 Thursday has "Audio + Visual alignment" as design only.

No task TESTS that audio timestamps align with video frames.

**Fix**: Add integration test: "Verify transcript timestamp matches frame timestamp ±1s"

---

## 3. Planning Quality Verification

### Estimates Review

| Task | Estimated | Realistic | Delta |
|:-----|:----------|:----------|:------|
| Install torch + transformers | 1h | 2h (with downloads) | +1h |
| DINOv2 integration test | 3h | 4h (debugging) | +1h |
| Multimodal index impl | 2h | 3h (FAISS issues) | +1h |
| TestPyPI publish | 2h | 3h (account setup) | +1h |
| **Total underestimate** | | | **+4h** |

Plan is ~4 hours underestimated. Buffer of 8h across 4 weeks (2h/week) is insufficient.

---

### Exit Criteria Quality

| Week | Exit Criteria | Measurable? | Testable? |
|:-----|:--------------|:------------|:----------|
| Week 2 | "DINOv2 produces valid embeddings" | ⚠️ Vague | ✅ |
| Week 3 | "Processing 10-min video < 120s" | ✅ | ✅ |
| Week 4 | "Encoder latency <50ms (GPU)" | ✅ | ⚠️ No GPU guaranteed |
| Week 5 | "pip install lecture-mind" | ⚠️ Wrong name | ✅ |

---

## 4. Risk Assessment

### Unmitigated Risks

| Risk | In Plan? | Mitigation? |
|:-----|:---------|:------------|
| Model download fails | ❌ | ❌ |
| CUDA version mismatch | ❌ | ❌ |
| FFmpeg not installed | ❌ | ❌ |
| Whisper crashes on long audio | ❌ | ❌ |
| FAISS index corruption | ❌ | ❌ |

---

## Required Actions

| Priority | Action | Deadline |
|:---------|:-------|:---------|
| **P0** | Fix package name inconsistency | Before approval |
| **P0** | Add model download task | Before approval |
| **P0** | Add FFmpeg verification | Before approval |
| **P0** | Add DINOv2 fallback decision tree | Before approval |
| **P0** | Add Whisper integration test | Before approval |
| **P0** | Fix coverage targets (gradual) | Before approval |
| **P1** | Add GPU verification task | Before Week 2 |
| **P1** | Add FAISS verification | Before Week 3 |
| **P1** | Add memory profiling task | Before Week 4 |
| **P1** | Clarify week numbering | Before approval |
| **P2** | Increase debug buffers | Recommended |
| **P2** | Add PyPI account prerequisite | Before Week 5 |

---

## Verdict Justification

```
┌─────────────────────────────────────────────────────────────────┐
│  HOSTILE_VALIDATOR VERDICT: ❌ NO_GO                            │
│                                                                 │
│  Critical issues found: 6                                       │
│  Major issues found: 8                                          │
│                                                                 │
│  The plan WILL FAIL if executed as-is.                          │
│  Missing: model downloads, FFmpeg check, fallbacks, tests       │
│                                                                 │
│  FIX ALL P0 ISSUES, then resubmit for review.                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sign-off

**HOSTILE_VALIDATOR**: HOSTILE_VALIDATOR
**Date**: 2026-01-01
**Verdict**: ❌ NO_GO

---

*"A plan that doesn't account for failure is a plan to fail."*
