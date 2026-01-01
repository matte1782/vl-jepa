# Lecture Mind — Product Roadmap v2.0

> **Last Updated**: 2026-01-01
> **Current Version**: v0.1.0
> **Status**: Pre-v0.2.0 validation required
> **Hostile Review**: Passed with conditions

---

## Executive Summary

| Version | Theme | Hours | Calendar | Status |
|---------|-------|-------|----------|--------|
| v0.1.0 | Foundation | - | DONE | ✅ Released |
| **Gate 0** | **Technical Validation** | **12h** | **Week 1** | ⏳ Required |
| v0.2.0 | Real Models | 80h | Weeks 2-5 | Blocked by Gate 0 |
| v0.3.0 | User Experience | 80h | Weeks 6-9 | Blocked by v0.2.0 |
| v1.0.0 | Production | 80h | Weeks 10-13 | Blocked by v0.3.0 |

**Assumptions:**
- Work velocity: 20 hours/week
- Single developer
- Part-time project

---

## Gate 0: Technical Validation (BLOCKING)

> **This gate MUST pass before v0.2.0 begins.**
> **Estimated effort: 12 hours**

### Purpose

Validate that the core technical approach works before investing in full implementation.

### Checklist

```
✅ G0.1: Technical Spike (4h) — COMPLETE
  ✅ Created technical_spike.py script
  ✅ Placeholder encoder validates interface (similarity tests pass)
  ⏳ DINOv2 test pending (requires: pip install torch transformers)
  ✅ Synthetic frame tests show semantic clustering
  ✅ Report: docs/reviews/TECHNICAL_SPIKE_REPORT.md

□ G0.2: Test Data Creation (3h) — PENDING
  □ Record or source 3 sample videos (Creative Commons)
    - lecture_10s.mp4 (minimal test)
    - lecture_60s.mp4 (short test with transitions)
    - lecture_slides.mp4 (clear slide changes)
  □ Store in tests/fixtures/videos/ (use git-lfs if >50MB)
  □ Document expected behavior for each video

✅ G0.3: Encoder Interface Design (2h) — COMPLETE
  ✅ Define VisualEncoderProtocol (src/vl_jepa/encoders/base.py)
  ✅ Define TextEncoderProtocol (src/vl_jepa/encoders/base.py)
  ✅ PlaceholderVisualEncoder implements Protocol
  ✅ PlaceholderTextEncoder implements Protocol
  ✅ DINOv2Encoder implements Protocol
  ✅ 23 interface tests passing (tests/unit/test_encoders.py)

✅ G0.4: Acceptance Criteria (1h) — COMPLETE
  ✅ PASS/FAIL criteria defined for all v0.2.0 goals (see below)
  ✅ Added to roadmap

□ G0.5: Dependency Validation (2h) — PARTIAL
  □ Test torch + DINOv2 installation on clean environment
  ✅ Version matrix documented (Dependency Matrix section)
  ✅ CI uses placeholder encoder (no real model required)
```

### Exit Criteria

| Criteria | Requirement | Status |
|----------|-------------|--------|
| Spike result | Embeddings show semantic clustering | ✅ Placeholder validated |
| Test videos | At least 2 videos in fixtures | ⏳ Pending |
| Interface | Protocol classes defined and tested | ✅ 23 tests passing |
| Acceptance | All v0.2.0 goals have PASS/FAIL criteria | ✅ Defined |

### GO/NO-GO Decision

```
IF all exit criteria met:
  → Proceed to v0.2.0 (GO)

IF spike shows embeddings don't cluster:
  → Investigate alternative approaches
  → Consider: CLIP + audio transcription
  → Re-evaluate entire approach before continuing

IF dependencies have conflicts:
  → Resolve before proceeding
  → Document workarounds
```

---

## v0.2.0 — Real Models & Core Pipeline

**Theme**: Replace placeholders with working models
**Effort**: 80 hours (4 weeks @ 20h/week)
**Prerequisites**: Gate 0 complete

### Goals with Acceptance Criteria

| ID | Goal | PASS Criteria | FAIL Criteria |
|----|------|---------------|---------------|
| G1 | Real visual encoder | Load DINOv2 in <30s, produce 768-dim embeddings, similar frames have cosine >0.85 | Load fails, wrong dimensions, random similarity |
| G2 | Real text encoder | Load sentence-transformers, produce 768-dim embeddings after projection | Import error, dimension mismatch |
| G3 | Working video pipeline | Process 10-min video in <120s, extract frames at 1 FPS ±0.1, memory <4GB | Crash, wrong FPS, OOM |
| G4 | PyPI publication | `pip install lecture-mind` succeeds, imports work, CLI runs | Install fails, import error |
| G5 | Performance baselines | Documented latency for encode/search/generate operations | No measurements |
| G6 | Test coverage 70%+ | pytest --cov reports ≥70% | Below 70% |

### Task Breakdown (with realistic estimates)

| Week | Task | Hours | Deliverable |
|------|------|-------|-------------|
| **Week 2** | | 20h | |
| | Implement encoder interface | 4h | `src/vl_jepa/encoders/base.py` |
| | DINOv2 encoder implementation | 8h | `src/vl_jepa/encoders/dinov2.py` |
| | Encoder tests (unit + integration) | 4h | `tests/unit/test_encoders.py` |
| | Debug buffer | 4h | - |
| **Week 3** | | 20h | |
| | Video processing with OpenCV | 8h | `src/vl_jepa/video.py` tested |
| | Frame extraction tests | 4h | `tests/integration/test_video.py` |
| | End-to-end pipeline test | 4h | `tests/integration/test_pipeline.py` |
| | Debug buffer | 4h | - |
| **Week 4** | | 20h | |
| | Text encoder with real model | 6h | `src/vl_jepa/text.py` updated |
| | Benchmark suite creation | 6h | `benchmarks/` |
| | Performance documentation | 4h | `docs/BENCHMARKS.md` |
| | Debug buffer | 4h | - |
| **Week 5** | | 20h | |
| | PyPI packaging preparation | 4h | `pyproject.toml` finalized |
| | README and docs update | 4h | User-facing documentation |
| | CI updates for real models | 4h | `.github/workflows/` |
| | Final testing and fixes | 4h | - |
| | Release v0.2.0 | 4h | Tag, release notes, PyPI publish |

### Deliverables

```
v0.2.0/
├── src/vl_jepa/
│   ├── encoders/
│   │   ├── __init__.py
│   │   ├── base.py          # Protocol definitions
│   │   ├── dinov2.py        # DINOv2 implementation
│   │   ├── placeholder.py   # Current placeholder (for testing)
│   │   └── clip.py          # Optional CLIP fallback
│   ├── video.py             # Tested with real videos
│   └── text.py              # Real sentence-transformers
├── tests/
│   ├── fixtures/
│   │   └── videos/          # Sample test videos
│   ├── unit/
│   │   └── test_encoders.py
│   └── integration/
│       ├── test_video.py
│       └── test_pipeline.py
├── benchmarks/
│   ├── bench_encoder.py
│   ├── bench_search.py
│   └── results/
├── docs/
│   ├── BENCHMARKS.md
│   └── INSTALLATION.md      # Including model download
└── pyproject.toml           # PyPI ready
```

### Risk Mitigations

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| DINOv2 doesn't produce good embeddings | Technical spike in Gate 0 | Switch to CLIP |
| Model too slow on CPU | Document GPU requirements | Offer cloud API option |
| PyPI name taken | Check availability early | Use `lecture-mind-ai` |
| CI can't run real models | Use lightweight model for CI | Mock in CI, test locally |

---

## v0.3.0 — User Experience & Distribution

**Theme**: Make it usable by non-developers
**Effort**: 80 hours (4 weeks @ 20h/week)
**Prerequisites**: v0.2.0 complete, working pipeline

### Goals with Acceptance Criteria

| ID | Goal | PASS Criteria | FAIL Criteria |
|----|------|---------------|---------------|
| G1 | Gradio web UI | Upload video, see events, execute query in browser | Crashes, no output |
| G2 | Progress indication | Progress bar updates during processing | Freezes without feedback |
| G3 | Export functionality | Download results as Markdown/JSON | No export option |
| G4 | Docker image | `docker run` starts working app, <3GB image | Build fails, >5GB |
| G5 | API documentation | Hosted docs with examples | No docs |
| G6 | Test coverage 80%+ | pytest --cov reports ≥80% | Below 80% |

### Task Breakdown

| Week | Task | Hours | Deliverable |
|------|------|-------|-------------|
| **Week 6** | | 20h | |
| | Gradio app skeleton | 8h | `src/vl_jepa/ui/app.py` |
| | Video upload + progress | 8h | Working upload with progress bar |
| | Debug buffer | 4h | - |
| **Week 7** | | 20h | |
| | Event timeline display | 6h | Visual timeline component |
| | Query interface | 6h | Text input + results display |
| | Export to Markdown | 4h | Download button |
| | Debug buffer | 4h | - |
| **Week 8** | | 20h | |
| | Dockerfile creation | 8h | Multi-stage, optimized |
| | Docker testing | 4h | Test on different platforms |
| | docker-compose setup | 4h | Easy local deployment |
| | Debug buffer | 4h | - |
| **Week 9** | | 20h | |
| | mkdocs setup | 4h | Documentation framework |
| | API documentation | 6h | All public APIs documented |
| | User tutorials | 4h | Getting started guide |
| | Demo recording | 2h | GIF/video for README |
| | Release v0.3.0 | 4h | Tag, release, Docker Hub |

### Deliverables

```
v0.3.0/
├── src/vl_jepa/
│   └── ui/
│       ├── __init__.py
│       ├── app.py           # Main Gradio app
│       ├── components.py    # Reusable components
│       └── export.py        # Export functionality
├── Dockerfile               # Optimized, multi-stage
├── docker-compose.yml       # Local deployment
├── docs/
│   ├── index.md             # mkdocs home
│   ├── getting-started.md   # Tutorial
│   ├── api/                 # Generated API docs
│   └── assets/
│       └── demo.gif         # README demo
├── mkdocs.yml               # Documentation config
└── tests/
    └── integration/
        └── test_ui.py       # UI tests
```

### Scope Limitations

> **NOT included in v0.3.0:**
> - OCR integration (deferred to v0.4.0)
> - Real Y-decoder summaries (use placeholder text)
> - GPU support in Docker (CPU only)

---

## v1.0.0 — Production Stable

**Theme**: Reliable, optimized, deployable
**Effort**: 80 hours (4 weeks @ 20h/week)
**Prerequisites**: v0.3.0 complete, user feedback collected

### Goals with Acceptance Criteria

| ID | Goal | PASS Criteria | FAIL Criteria |
|----|------|---------------|---------------|
| G1 | Performance optimization | Query latency p99 <200ms on CPU | Slower than v0.3.0 |
| G2 | Real Y-decoder | Generate actual summaries (Phi-3 mini or similar) | Still placeholder |
| G3 | Security audit | bandit + safety pass with 0 high issues | Critical vulnerabilities |
| G4 | AWS deployment guide | Step-by-step instructions that work | Broken instructions |
| G5 | Health monitoring | /health endpoint, basic metrics | No observability |
| G6 | Test coverage 85%+ | pytest --cov reports ≥85% | Below 85% |

### Task Breakdown

| Week | Task | Hours | Deliverable |
|------|------|-------|-------------|
| **Week 10** | | 20h | |
| | Real decoder integration (Phi-3) | 12h | Working summaries |
| | Decoder tests | 4h | Quality validation |
| | Debug buffer | 4h | - |
| **Week 11** | | 20h | |
| | Performance profiling | 6h | Identify bottlenecks |
| | Optimization implementation | 8h | Caching, batching |
| | Benchmark comparison | 2h | vs v0.3.0 |
| | Debug buffer | 4h | - |
| **Week 12** | | 20h | |
| | Security audit (bandit, safety) | 4h | Vulnerability report |
| | Security fixes | 6h | Address findings |
| | Health endpoints | 4h | /health, /metrics |
| | Logging improvements | 2h | Structured logging |
| | Debug buffer | 4h | - |
| **Week 13** | | 20h | |
| | AWS deployment guide | 6h | ECS or Lambda docs |
| | Final documentation | 4h | All docs complete |
| | Release preparation | 4h | Changelog, migration guide |
| | Release v1.0.0 | 2h | Tag, release |
| | Buffer | 4h | - |

### Deferred to v1.1.0+

| Feature | Reason |
|---------|--------|
| Real-time streaming | Fundamentally different architecture |
| Multi-language (i18n) | Nice-to-have, not core |
| Multi-cloud (GCP, Azure) | AWS first, document others later |
| Kubernetes deployment | Docker sufficient for v1.0 |
| OCR integration | Adds complexity without core value |

---

## Dependency Matrix

| Package | Min | Max | Notes |
|---------|-----|-----|-------|
| python | 3.10 | 3.12 | 3.13 experimental |
| torch | 2.0.0 | 2.3.x | DINOv2 compatibility |
| torchvision | 0.15.0 | 0.18.x | Must match torch |
| transformers | 4.35.0 | 4.x | DINOv2 models |
| sentence-transformers | 2.2.0 | 2.x | Text encoding |
| gradio | 4.0.0 | 4.x | Pin major version |
| faiss-cpu | 1.7.4 | 1.x | Embedding search |
| opencv-python | 4.8.0 | 4.x | Video processing |

### Version Lock Strategy

```toml
# pyproject.toml
dependencies = [
    "torch>=2.0.0,<2.4",
    "transformers>=4.35.0,<5",
    # ... etc
]
```

---

## Risk Register (Updated)

| ID | Risk | Impact | Prob | Mitigation | Status |
|----|------|--------|------|------------|--------|
| R1 | DINOv2 embeddings don't work for lectures | HIGH | MED | Gate 0 technical spike | ⏳ Validate |
| R2 | GPU required for usable speed | MED | HIGH | Document, offer cloud | ⏳ Measure |
| R3 | Video codec issues | MED | MED | Test matrix in Gate 0 | ⏳ Validate |
| R4 | PyPI name taken | LOW | LOW | Check now | ✅ Available |
| R5 | Scope creep | HIGH | HIGH | Strict version scopes | ✅ Defined |
| R6 | Single maintainer | MED | HIGH | Document everything | ⏳ Ongoing |
| R7 | Model licensing issues | MED | LOW | Use Apache/MIT models | ✅ DINOv2 OK |

---

## Success Metrics (Realistic)

| Version | Metric | Target | Stretch |
|---------|--------|--------|---------|
| v0.2.0 | PyPI downloads (month 1) | 50 | 200 |
| v0.2.0 | 10-min video processing time | <120s | <60s |
| v0.3.0 | GitHub stars | 25 | 100 |
| v0.3.0 | Docker pulls (month 1) | 100 | 500 |
| v1.0.0 | Query latency (p99) | <200ms | <100ms |
| v1.0.0 | Active users (monthly) | 10 | 50 |

---

## Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-01-01 | DINOv2 as primary encoder | Apache license, good availability, proven quality | V-JEPA (complex), CLIP (less semantic) |
| 2026-01-01 | Gradio over Streamlit | Better ML integration, simpler deployment | Streamlit, FastAPI+React |
| 2026-01-01 | Gate 0 before v0.2.0 | Validate approach before major investment | YOLO (risky) |
| 2026-01-01 | Defer OCR to v0.4.0 | Focus on core pipeline first | Include in v0.3.0 (scope creep) |
| 2026-01-01 | Phi-3 mini for decoder | Small, fast, permissive license | Gemma (restrictive), GPT (API cost) |

---

## Calendar View

```
January 2026
├── Week 1 (Jan 1-7): Gate 0 - Technical Validation
│   └── Spike, test data, interface design
│
├── Week 2-5 (Jan 8 - Feb 4): v0.2.0 - Real Models
│   ├── Week 2: Encoder implementation
│   ├── Week 3: Video pipeline
│   ├── Week 4: Benchmarks
│   └── Week 5: PyPI release
│
February 2026
├── Week 6-9 (Feb 5 - Mar 4): v0.3.0 - User Experience
│   ├── Week 6: Gradio skeleton
│   ├── Week 7: UI features
│   ├── Week 8: Docker
│   └── Week 9: Docs + release
│
March 2026
├── Week 10-13 (Mar 5 - Apr 1): v1.0.0 - Production
│   ├── Week 10: Real decoder
│   ├── Week 11: Optimization
│   ├── Week 12: Security
│   └── Week 13: AWS + release
```

---

## Next Actions

1. **Now**: Start Gate 0 - Download DINOv2, run technical spike
2. **After spike**: GO/NO-GO decision for v0.2.0
3. **If GO**: Begin Week 2 tasks

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v2.0 | 2026-01-01 | Added Gate 0, realistic estimates, acceptance criteria |
| v1.0 | 2026-01-01 | Initial roadmap |

---

*"Measure twice, cut once. Validate before you build."*
