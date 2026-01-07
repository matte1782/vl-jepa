# Lecture Mind — Product Roadmap v2.1

> **Last Updated**: 2026-01-07
> **Current Version**: v0.2.0
> **Status**: v0.2.0 RELEASE READY
> **Hostile Review**: GO - Ready for PyPI publication

---

## Executive Summary

| Version | Theme | Hours | Calendar | Status |
|---------|-------|-------|----------|--------|
| v0.1.0 | Foundation | - | DONE | ✅ Released |
| Gate 0 | Technical Validation | 12h | Week 1 | ✅ Complete |
| **v0.2.0** | **Real Models + Audio** | **80h** | **Weeks 2-6** | ⏳ In Progress |
| v0.3.0 | User Experience | 80h | Weeks 7-10 | Blocked by v0.2.0 |
| v1.0.0 | Production | 80h | Weeks 11-14 | Blocked by v0.3.0 |

**Assumptions:**
- Work velocity: 20 hours/week
- Single developer
- Part-time project

---

## Gate 0: Technical Validation ✅ COMPLETE

> **Gate passed on 2026-01-01**
> **Effort: 12 hours**

### Completed Tasks

```
✅ G0.1: Technical Spike (4h)
  ✅ Created technical_spike.py script
  ✅ Placeholder encoder validates interface
  ✅ Synthetic frame tests show semantic clustering

✅ G0.2: Test Data Creation (3h)
  ✅ Private lecture video tested (31 min)
  ✅ 50 frames extracted, 3 transitions detected
  ✅ Stored in tests/lecture_ex/ (gitignored)

✅ G0.3: Encoder Interface Design (2h)
  ✅ VisualEncoderProtocol defined
  ✅ TextEncoderProtocol defined
  ✅ 23 interface tests passing

✅ G0.4: Acceptance Criteria (1h)
  ✅ PASS/FAIL criteria defined for v0.2.0

✅ G0.5: Dependency Validation (2h)
  ✅ Version matrix documented
  ✅ CI uses placeholder encoder
```

### Decision: GO

Proceed to v0.2.0 implementation.

---

## v0.2.0 — Real Models & Core Pipeline

**Theme**: Replace placeholders with working models + audio transcription
**Effort**: 80 hours (4 weeks @ 20h/week)
**Prerequisites**: Gate 0 complete ✅
**Status**: ⏳ In Progress

### Goals with Acceptance Criteria

| ID | Goal | PASS Criteria | FAIL Criteria | Status |
|----|------|---------------|---------------|--------|
| G1 | Real visual encoder | DINOv2 768-dim embeddings, similar frames cosine >0.85 | Load fails, random similarity | ✅ Validated Week 3 |
| G2 | Real text encoder | sentence-transformers, 768-dim embeddings | Import error | ✅ Validated Week 3 |
| G3 | Video pipeline | 10-min video in <120s, 1 FPS, memory <4GB | Crash, OOM | ✅ Tested Week 3 |
| G7 | Audio transcription | Whisper <60s for 10-min, WER <10%, aligned timestamps | Garbled text | ✅ Module complete |
| G8 | Multimodal index | Combined visual + transcript ranking | Single modality | ✅ Tested Week 3 |
| G4 | PyPI publication | `pip install lecture-mind` works | Install fails | ⏳ Week 5 |
| G5 | Performance baselines | Documented latency for all operations | No measurements | ✅ Documented Week 3 |
| G6 | Test coverage 70%+ | pytest --cov ≥70% | Below 70% | ✅ 71% achieved |

### Task Breakdown

| Week | Task | Hours | Status |
|------|------|-------|--------|
| **Week 2** | **Audio Module** | 16h | **In Progress** |
| | ~~Whisper transcriber~~ | ~~6h~~ | ✅ `audio/transcriber.py` |
| | ~~FFmpeg audio extractor~~ | ~~4h~~ | ✅ `audio/extractor.py` |
| | ~~Placeholder transcriber~~ | ~~2h~~ | ✅ `audio/placeholder.py` |
| | ~~Audio tests~~ | ~~4h~~ | ✅ 17 tests passing |
| | Transcript chunking | 4h | ⏳ `audio/chunker.py` |
| | DINOv2 integration test | 6h | ⏳ Requires torch |
| | Debug buffer | 6h | - |
| **Week 3** | **Video + Text Pipeline** | 20h | ✅ Complete |
| | Video processing with OpenCV | 6h | ✅ `video.py` tested |
| | Multimodal index | 6h | ✅ 98% coverage |
| | Text encoder real model | 4h | ✅ `text.py` validated |
| | Debug buffer | 4h | ✅ Used for fixes |
| **Week 4** | **Benchmarks + Polish** | 20h | ✅ Complete |
| | ~~Benchmark suite~~ | ~~6h~~ | ✅ `tests/benchmarks/` |
| | ~~Performance docs~~ | ~~4h~~ | ✅ `BENCHMARKS.md` |
| | ~~Coverage to 70%+~~ | ~~6h~~ | ✅ 74% achieved |
| | ~~Debug buffer~~ | ~~4h~~ | ✅ Used for polish |
| **Week 5** | **Release** | 20h | |
| | PyPI packaging | 4h | `pyproject.toml` final |
| | README + docs update | 4h | Documentation |
| | CI updates | 4h | `.github/workflows/` |
| | Final testing | 4h | - |
| | Release v0.2.0 | 4h | Tag, PyPI publish |

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
│   ├── audio/               # NEW: Audio transcription
│   │   ├── __init__.py
│   │   ├── transcriber.py   # Whisper integration
│   │   ├── chunker.py       # Transcript segmentation
│   │   └── extractor.py     # Audio extraction from video
│   ├── video.py             # Tested with real videos
│   ├── text.py              # Real sentence-transformers
│   └── index.py             # Multimodal index (visual + transcript)
├── tests/
│   ├── fixtures/
│   │   └── videos/          # Sample test videos
│   ├── unit/
│   │   ├── test_encoders.py
│   │   └── test_audio.py    # NEW: Audio tests
│   └── integration/
│       ├── test_video.py
│       ├── test_audio.py    # NEW: Transcription integration
│       └── test_pipeline.py # Full multimodal pipeline
├── benchmarks/
│   ├── bench_encoder.py
│   ├── bench_search.py
│   ├── bench_transcribe.py  # NEW: Whisper benchmarks
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
| PyPI name taken | ✅ `lecture-mind` verified available | Use `lecture-mind-ai` |
| **Whisper too slow on CPU** | **Use faster-whisper (CTranslate2)** | **Whisper.cpp or cloud API** |
| **Audio extraction fails** | **FFmpeg dependency** | **moviepy fallback** |
| **Non-English lectures** | **Whisper supports 99 languages** | **Language detection first** |
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
| **faster-whisper** | **1.0.0** | **1.x** | **Audio transcription (CTranslate2)** |
| gradio | 4.0.0 | 4.x | Pin major version |
| faiss-cpu | 1.7.4 | 1.x | Embedding search |
| opencv-python | 4.8.0 | 4.x | Video processing |
| **ffmpeg-python** | **0.2.0** | **0.x** | **Audio extraction** |

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
├── Week 1 (Jan 1-7): Gate 0 - Technical Validation ✅ COMPLETE
│   └── Spike, test data, interface design, audio module started
│
├── Week 2-5 (Jan 8 - Feb 4): v0.2.0 - Real Models + Audio
│   ├── Week 2: Audio module + DINOv2 integration ✅ COMPLETE
│   ├── Week 3: Video + Text pipeline ✅ COMPLETE
│   ├── Week 4: Benchmarks + Polish ✅ COMPLETE
│   └── Week 5: Release prep + PyPI publish (NEXT)
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

1. **Now**: Week 5 - Release v0.2.0 to PyPI
2. **Week 5**: README update, CI finalization, PyPI publish
3. **Week 6**: Begin v0.3.0 - Gradio UI

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v2.4 | 2026-01-07 | v0.2.0 release ready, README comprehensive, PyPI metadata complete |
| v2.3 | 2026-01-06 | Week 4 complete, 74% coverage, v0.2.0-rc1 ready |
| v2.2 | 2026-01-04 | Week 3 complete, 7/8 v0.2.0 goals achieved, 71% coverage |
| v2.1 | 2026-01-01 | Updated Gate 0 complete, audio module progress tracked |
| v2.0 | 2026-01-01 | Added Gate 0, realistic estimates, acceptance criteria |
| v1.0 | 2026-01-01 | Initial roadmap |

---

*"Measure twice, cut once. Validate before you build."*
