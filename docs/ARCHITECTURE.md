# ARCHITECTURE

> VL-JEPA Lecture Summarizer System Design
> Framework: FORTRESS 4.1.1

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VL-JEPA LECTURE SUMMARIZER                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  VIDEO INPUT                                                         │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────┐                                                    │
│  │ Frame       │ → Extracts frames at configurable FPS              │
│  │ Sampler     │                                                    │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐                                                    │
│  │ Visual      │ → V-JEPA ViT-L/16 encoder                         │
│  │ Encoder     │ → Produces 768-dim embeddings                     │
│  └──────┬──────┘                                                    │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐     ┌─────────────┐                                │
│  │ Event       │ ──▶ │ Storage     │ → FAISS index                 │
│  │ Detector    │     │ + Index     │ → Timestamps + embeddings     │
│  └──────┬──────┘     └──────┬──────┘                                │
│         │                   │                                        │
│         │ (on event)        │ (on query)                            │
│         ▼                   ▼                                        │
│  ┌─────────────┐     ┌─────────────┐                                │
│  │ Y-Decoder   │     │ Query       │ ← Text encoder                 │
│  │ (LLM)       │     │ Pipeline    │ ← Similarity search           │
│  └──────┬──────┘     └──────┬──────┘                                │
│         │                   │                                        │
│         ▼                   ▼                                        │
│    SUMMARY TEXT       RELEVANT SEGMENTS                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Video Input | `src/vl_jepa/video/` | Load and stream video files |
| Frame Sampler | `src/vl_jepa/video/frame_sampler.py` | Extract frames at target FPS |
| Visual Encoder | `src/vl_jepa/encoder/` | V-JEPA embedding generation |
| Event Detector | `src/vl_jepa/event/` | Detect semantic boundaries |
| Storage | `src/vl_jepa/retrieval/storage.py` | Persist embeddings + metadata |
| Text Encoder | `src/vl_jepa/retrieval/text_encoder.py` | Encode text queries |
| Query Pipeline | `src/vl_jepa/retrieval/query.py` | Search and retrieve |
| Y-Decoder | `src/vl_jepa/decoder/` | Generate text from embeddings |
| CLI | `src/vl_jepa/cli.py` | Command-line interface |
| UI | `src/vl_jepa/ui/` | Gradio web interface |

---

## Data Flow

1. **Ingestion**: Video → Frames → Embeddings → Storage
2. **Detection**: Embeddings → Change detection → Event triggers → Summaries
3. **Retrieval**: Query text → Query embedding → Similarity search → Results

---

## Detailed Documentation

For comprehensive architecture details, see:
- `docs/architecture/ARCHITECTURE.md` — Full system design
- `docs/architecture/DATA_FLOW.md` — Detailed data pipelines
- `docs/architecture/API_DESIGN.md` — API specifications

---

*Keep it simple. Add complexity only when needed.*
