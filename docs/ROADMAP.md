# ROADMAP

> Last updated: 2025-12-31
> Framework: FORTRESS 4.1.1

---

## Current Version: v0.1.0 (MVP)

### Goals
Build a working event-aware lecture summarizer with:
- [x] Video input and frame sampling
- [x] Visual encoder (V-JEPA based)
- [x] Event boundary detection
- [x] Embedding storage and retrieval
- [x] Y-decoder integration (text generation)
- [ ] Gradio UI for demo
- [ ] End-to-end pipeline testing

### In Progress
- [ ] Enable remaining test stubs (15/80 tests enabled and passing)
- [ ] Integration testing

### Completed
- [x] Project brief and requirements
- [x] FORTRESS 4.1.1 framework setup
- [x] Architecture design (docs/architecture/)
- [x] Test strategy (docs/TEST_STRATEGY.md)
- [x] Specification (docs/SPECIFICATION.md)
- [x] Package structure (`src/vl_jepa/`)
- [x] Core modules implemented:
  - video.py (VideoInput, VideoDecodeError)
  - frame.py (FrameSampler)
  - encoder.py (VisualEncoder, ModelLoadError)
  - detector.py (EventDetector, EventBoundary)
  - storage.py (Storage with crash recovery)
  - text.py (TextEncoder)
  - decoder.py (YDecoder)
  - index.py (EmbeddingIndex)
  - cli.py (CLI interface)
- [x] pyproject.toml and README.md
- [x] 15 unit tests passing (frame_sampler, event_detector, storage)

### Blocked
- [ ] None currently

---

## Implementation Order (Recommended)

1. **Package Structure** — Create `src/vl_jepa/` with `__init__.py`
2. **Video Input** — `src/vl_jepa/video/` — Load and stream video
3. **Frame Sampler** — Extract frames at target FPS
4. **Visual Encoder** — V-JEPA embedding generation
5. **Event Detector** — Detect semantic boundaries
6. **Storage** — Persist embeddings with FAISS
7. **Text Encoder** — Encode text queries
8. **Query Pipeline** — Search and retrieve
9. **Y-Decoder** — Generate text from embeddings
10. **CLI** — Command-line interface
11. **Gradio UI** — Web interface for demo

---

## Future (v0.2.0+)

- Real-time streaming processing
- ML-based event detection
- Multi-modal summarization
- Cloud deployment

---

*Human decides what to work on. AI helps execute.*
