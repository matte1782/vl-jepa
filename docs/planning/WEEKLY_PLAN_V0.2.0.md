# v0.2.0 Detailed Implementation Plan

> **Version**: 2.0 (Post Hostile Review)
> **Created**: 2026-01-01
> **Status**: REVISED
> **Total Effort**: 80 hours (4 weeks @ 20h/week)
> **Schedule**: 4 hours/day, 5 days/week
> **Weeks**: 2-5 (Week 1 = Gate 0, completed)

---

## Package Name Decision

**DECIDED**: Package name is `lecture-mind`

- PyPI: `pip install lecture-mind`
- Import: `from vl_jepa import ...` (source directory name)
- CLI: `lecture-mind --help`

---

## Prerequisites (Before Week 2)

```
[x] Python 3.10+ installed
[x] pip install -e ".[dev]" works
[ ] FFmpeg installed and in PATH
    - Windows: winget install ffmpeg
    - macOS: brew install ffmpeg
    - Linux: apt install ffmpeg
    - Verify: ffmpeg -version
[ ] GPU check (optional but recommended):
    - python -c "import torch; print(torch.cuda.is_available())"
[ ] ~2GB disk space for model downloads
```

---

## Assumptions

| Assumption | Value | Risk if Wrong | Mitigation |
|------------|-------|---------------|------------|
| Daily availability | 4 hours | Tasks slip | Weekend catchup allowed |
| Weekend work | Emergency only | - | 4h emergency buffer |
| Dependencies install | May fail | +1h debug | Fallback to placeholder |
| Tests pass first time | 70% | +30% time | 4h buffer per week |
| Models download | 10-15 min | Block progress | Cache after first download |

---

## Week 2: Audio Module + DINOv2 Setup

**Goal**: Complete audio pipeline and validate DINOv2 encoder
**Hours**: 20h
**Theme**: Foundation validation

### Day-by-Day

| Day | Task | Hours | Deliverable | PASS Criteria |
|-----|------|-------|-------------|---------------|
| **Mon** | FFmpeg verification | 0.5h | Script output | `ffmpeg -version` works |
| | Transcript chunker design | 1.5h | `audio/chunker.py` skeleton | Classes defined |
| | Chunker implementation | 2h | Working chunker | Splits by time windows |
| **Tue** | Chunker tests | 2h | `tests/unit/test_chunker.py` | 10+ tests pass |
| | Chunker edge cases | 2h | Edge case handling | Empty, single, overlap |
| **Wed** | Model download + cache | 1h | Models cached | DINOv2 + sentence-transformers |
| | DINOv2 integration test | 3h | `scripts/test_dinov2.py` | Real embeddings generated |
| **Thu** | DINOv2 similarity validation | 2h | Similarity tests | Similar frames cosine > 0.85 |
| | **DECISION GATE** | - | GO/NO-GO | See fallback below |
| | Whisper integration test | 2h | Transcribe lecture video | Text output matches audio |
| **Fri** | Audio extraction integration | 1.5h | WAV from lecture video | File extracted, playable |
| | Audio+Visual timestamp sync | 1.5h | Alignment document | Sync strategy documented |
| | Week 2 buffer | 1h | - | Catch up / documentation |

### DINOv2 Decision Gate (Thursday)

```
IF similar_frames_cosine >= 0.85:
    → PASS: Continue with DINOv2

ELIF similar_frames_cosine >= 0.70:
    → INVESTIGATE: Try different frame pairs
    → IF still < 0.85: Document limitation, continue

ELIF similar_frames_cosine < 0.70:
    → FALLBACK: Switch to CLIP encoder
    → Add 4h to Week 3 for CLIP integration
    → IF CLIP also fails: STOP, architecture review needed
```

### Week 2 Exit Criteria

```
[ ] FFmpeg verified working
[ ] audio/chunker.py implemented and tested (10+ tests)
[ ] Models downloaded and cached
[ ] DINOv2 produces embeddings from real frames
[ ] DINOv2 Decision Gate: PASS or FALLBACK decided
[ ] Whisper transcribes lecture video successfully
[ ] Audio extraction from video works
[ ] All unit tests pass (target: 105+ tests)
[ ] Coverage >= 58%
```

---

## Week 3: Video + Text Pipeline

**Goal**: Complete video processing and multimodal index
**Hours**: 20h
**Theme**: Integration

### Prerequisites Check

```
[ ] FAISS installed: python -c "import faiss; print(faiss.__version__)"
[ ] sentence-transformers installed
[ ] DINOv2 or CLIP encoder working (from Week 2)
```

### Day-by-Day

| Day | Task | Hours | Deliverable | PASS Criteria |
|-----|------|-------|-------------|---------------|
| **Mon** | FAISS verification | 0.5h | Import test | `import faiss` works |
| | Video processor refactor | 1.5h | `video.py` with OpenCV | Load video, get metadata |
| | Frame extraction impl | 2h | Extract at 1 FPS | Correct frame count |
| **Tue** | Text encoder real model | 2h | `text.py` updated | Load model, encode |
| | Text encoder tests | 2h | Unit tests | 768-dim output verified |
| **Wed** | Multimodal index design | 1h | Architecture doc | Visual + text strategy |
| | Multimodal index impl | 3h | `index.py` updated | Both modalities stored |
| **Thu** | Multimodal search impl | 2h | Query both types | Results from both |
| | Ranking algorithm | 2h | Combined scoring | Weighted fusion works |
| **Fri** | End-to-end pipeline test | 2h | `test_pipeline.py` | Video → index works |
| | Audio+Visual sync test | 1h | Integration test | Timestamps align ±1s |
| | Week 3 buffer | 1h | - | Catch up |

### Week 3 Exit Criteria

```
[ ] FAISS verified working
[ ] Video processor extracts frames at 1 FPS ±0.1
[ ] Text encoder produces 768-dim embeddings
[ ] Multimodal index stores visual + transcript
[ ] Search returns results from both modalities
[ ] Ranking combines scores correctly
[ ] Audio-visual timestamps align ±1 second
[ ] End-to-end pipeline test passes
[ ] Processing 10-min video < 120 seconds
[ ] Coverage >= 62%
```

---

## Week 4: Benchmarks + Quality

**Goal**: Performance validation and coverage boost
**Hours**: 20h
**Theme**: Validation

### Day-by-Day

| Day | Task | Hours | Deliverable | PASS Criteria |
|-----|------|-------|-------------|---------------|
| **Mon** | Benchmark framework | 2h | `benchmarks/` ready | pytest-benchmark works |
| | Encoder benchmarks | 2h | `bench_encoder.py` | Latency logged |
| **Tue** | Search benchmarks | 2h | `bench_search.py` | <100ms @ 10k vectors |
| | Transcription benchmarks | 2h | `bench_transcribe.py` | <60s for 10-min |
| **Wed** | Memory profiling | 1.5h | Memory report | Document peak usage |
| | Benchmark documentation | 1.5h | `docs/BENCHMARKS.md` | All metrics documented |
| | Performance bottlenecks | 1h | Profile results | Top 3 bottlenecks identified |
| **Thu** | Coverage boost: core | 2h | Additional tests | +5% coverage |
| | Coverage boost: audio | 2h | Additional tests | +3% coverage |
| **Fri** | Coverage boost: pipeline | 2h | Integration tests | Target met |
| | Week 4 buffer | 2h | - | Quality polish |

### Week 4 Exit Criteria

```
[ ] Benchmark suite runs without errors
[ ] All performance metrics documented in BENCHMARKS.md
[ ] Encoder latency: <50ms/frame (GPU) or <200ms (CPU)
[ ] Search latency: <100ms (10k vectors)
[ ] Whisper latency: <60s for 10-min audio
[ ] Memory usage documented
[ ] Test coverage >= 67%
```

---

## Week 5: Release

**Goal**: PyPI publication and documentation
**Hours**: 20h
**Theme**: Ship it

### Prerequisites Check

```
[ ] PyPI account created (https://pypi.org/account/register/)
[ ] API token generated (https://pypi.org/manage/account/token/)
[ ] ~/.pypirc configured OR use --token flag
[ ] TestPyPI account (optional but recommended)
```

### Day-by-Day

| Day | Task | Hours | Deliverable | PASS Criteria |
|-----|------|-------|-------------|---------------|
| **Mon** | pyproject.toml final | 1.5h | Release config | All metadata complete |
| | Version bump to 0.2.0 | 0.5h | Version updated | Consistent everywhere |
| | Build test | 1h | `pip install -e .` | Clean install works |
| | Wheel build test | 1h | `python -m build` | .whl created |
| **Tue** | README update | 2h | User docs | Install, usage, examples |
| | CHANGELOG update | 1h | `CHANGELOG.md` | All changes listed |
| | API docstrings | 1h | All public APIs | Docstrings complete |
| **Wed** | CI workflow updates | 2h | `.github/workflows/` | Tests on PR |
| | CI model handling | 2h | Placeholder in CI | Real models optional |
| **Thu** | TestPyPI publish | 1.5h | Test package | Install from test.pypi.org |
| | TestPyPI validation | 1.5h | Test imports | All imports work |
| | Fix issues | 1h | Issues resolved | Ready for prod |
| **Fri** | PyPI publish | 1h | `pip install lecture-mind` | Package live |
| | GitHub release | 1h | Tag v0.2.0 | Release created |
| | Fresh install test | 1h | Clean env test | Works on new venv |
| | Coverage final push | 1h | Final tests | >= 70% |

### Release Contingency

```
IF PyPI publish fails:
    → Debug over weekend (2h max)
    → Publish Monday of next week
    → Document issue in post-mortem

IF TestPyPI fails:
    → Fix Thursday, retry Friday AM
    → If still fails: skip TestPyPI, go direct (risky)
```

### Week 5 Exit Criteria

```
[ ] pip install lecture-mind succeeds (fresh venv)
[ ] All imports work correctly
[ ] CLI runs: lecture-mind --help
[ ] README has clear installation instructions
[ ] CHANGELOG documents all v0.2.0 changes
[ ] GitHub release with tag v0.2.0
[ ] CI passes on main branch
[ ] Test coverage >= 70%
```

---

## Coverage Trajectory

| Week | Target | From | Tests to Add |
|:-----|:-------|:-----|:-------------|
| Week 2 | >= 58% | 58% | Maintain |
| Week 3 | >= 62% | 58% | ~10 tests |
| Week 4 | >= 67% | 62% | ~15 tests |
| Week 5 | >= 70% | 67% | ~10 tests |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| DINOv2 slow on CPU | HIGH | Schedule slip | Document GPU rec | Reduce frame rate |
| DINOv2 similarity low | MEDIUM | Approach invalid | CLIP fallback | Architecture review |
| Whisper install fails | MEDIUM | Block audio | Placeholder mode | Manual install docs |
| FFmpeg missing | LOW | Block extraction | Install docs | User installs |
| PyPI name taken | LOW | Block release | Check now | Use `vl-jepa-ai` |
| CI times out | MEDIUM | Merge blocked | Split tests | Use markers |
| Coverage target missed | MEDIUM | Quality gate | Incremental | Reduce target |
| Model download fails | LOW | Block Week 2 | Retry, cache | Manual download |
| FAISS issues | MEDIUM | Block Week 3 | faiss-cpu | numpy fallback |

---

## Daily Standup Template

```markdown
## Standup [DATE]

### Yesterday
- [Completed tasks]
- [Hours logged]

### Today
- [Planned tasks]
- [Expected hours]

### Blockers
- [Any blockers]

### Confidence
- [ ] On track
- [ ] Minor delay (<2h)
- [ ] Major delay (>4h) - need plan adjustment
```

---

## Weekly Review Template

```markdown
## Week [N] Review

### Completed
- [List of completed tasks]
- Hours: [X]/20

### Incomplete
- [Tasks not finished]
- Reason: [Why]
- Carryover: [To which day/week]

### Metrics
- Tests: [X] passing (+Y from last week)
- Coverage: [X]% (+Y% from last week)
- Blockers hit: [N]

### Decision Gates
- [Any decisions made]

### Next Week Adjustments
- [Plan changes if any]
```

---

## Checkpoints

| Checkpoint | End of | Validation | Fallback |
|------------|--------|------------|----------|
| Audio Complete | Week 2 | Whisper + chunker work | Use placeholder |
| DINOv2 Decision | Week 2 Thu | Cosine > 0.85 | CLIP encoder |
| Pipeline Complete | Week 3 | E2E test passes | Reduce scope |
| Benchmarks Done | Week 4 | All metrics logged | Document gaps |
| Release Ready | Week 5 | PyPI live | Delay 1 week |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | - | - | - |
| Hostile Reviewer | - | - | PENDING RE-REVIEW |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-01 | Fixed all P0 issues from hostile review |
| 1.0 | 2026-01-01 | Initial plan (rejected) |

---

*"A plan that accounts for failure is a plan that succeeds."*
