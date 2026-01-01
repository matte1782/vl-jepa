# VL-JEPA Data Flow Specification v1.0

**Date:** 2024-12-30
**Author:** META_ARCHITECT
**Status:** PROPOSED

---

## 1. Overview

This document specifies the data transformations and flow paths through the VL-JEPA Lecture Summarizer system. Each stage is documented with input/output shapes, timing constraints, and validation requirements.

---

## 2. Primary Data Flows

### 2.1 Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VIDEO SOURCE                                                                │
│  ├── File: .mp4, .webm, .mkv                                                │
│  ├── Stream: RTSP, webcam device                                            │
│  └── Output: Raw frames (BGR, variable resolution)                          │
│       │                                                                      │
│       ▼                                                                      │
│  FRAME SAMPLER                                                               │
│  ├── Input: Raw frames @ source FPS                                         │
│  ├── Transform: Resize + Normalize                                          │
│  │   ├── Resize: source → 224x224                                           │
│  │   ├── Colorspace: BGR → RGB                                              │
│  │   └── Normalize: [0,255] → [-1.0, 1.0]                                   │
│  ├── Rate: Downsample to target FPS (default: 1.0)                          │
│  └── Output: (224, 224, 3) float32 tensors                                  │
│       │                                                                      │
│       ▼                                                                      │
│  VISUAL ENCODER (V-JEPA)                                                     │
│  ├── Input: Batch of frames (B, 3, 224, 224)                                │
│  ├── Transform: ViT-L/16 forward pass                                       │
│  │   ├── Patch embedding: 14x14 patches                                     │
│  │   ├── Transformer: 24 layers, 1024 dim, 16 heads                         │
│  │   └── Pooling: CLS token or mean pool                                    │
│  ├── Normalize: L2 normalization                                            │
│  └── Output: (B, 768) float32 embeddings                                    │
│       │                                                                      │
│       ├─────────────────────────────────┐                                   │
│       ▼                                 ▼                                   │
│  EMBEDDING INDEX                   EVENT DETECTOR                           │
│  ├── Input: (768,) embedding       ├── Input: embeddings[t-w:t]            │
│  ├── Store: FAISS IVF index        ├── Compute: cosine_dist(e_t, e_{t-1})  │
│  └── Output: frame_id → index      ├── Decision: dist > threshold?         │
│                                    └── Output: Event(timestamp, conf)       │
│                                         │                                   │
│                                         ▼ (if event detected)               │
│                                    Y-DECODER (Gemma-2B)                     │
│                                    ├── Input: embedding + context           │
│                                    ├── Generate: text summary               │
│                                    └── Output: summary string               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Query Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            QUERY PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USER QUERY                                                                  │
│  ├── Input: Natural language text                                           │
│  ├── Validation: length <= 256 tokens                                       │
│  └── Output: query string                                                   │
│       │                                                                      │
│       ▼                                                                      │
│  TEXT ENCODER (MiniLM)                                                       │
│  ├── Input: query string                                                    │
│  ├── Tokenize: SentencePiece                                                │
│  ├── Encode: 6-layer transformer                                            │
│  ├── Pool: Mean pooling                                                     │
│  └── Output: (384,) float32 embedding                                       │
│       │                                                                      │
│       ▼                                                                      │
│  PROJECTION LAYER                                                            │
│  ├── Input: (384,) text embedding                                           │
│  ├── Transform: Linear(384, 768) + L2 norm                                  │
│  └── Output: (768,) float32 embedding (aligned)                             │
│       │                                                                      │
│       ▼                                                                      │
│  SIMILARITY SEARCH                                                           │
│  ├── Input: query embedding (768,)                                          │
│  ├── Index: FAISS IVF (nprobe=10)                                           │
│  ├── Metric: Inner product (= cosine on L2-normalized)                      │
│  └── Output: [(frame_id, score), ...] top-k                                 │
│       │                                                                      │
│       ▼                                                                      │
│  RESULT BUILDER                                                              │
│  ├── Input: frame_ids, scores                                               │
│  ├── Fetch: timestamps, summaries from SQLite                               │
│  ├── Format: structured response                                            │
│  └── Output: QueryResult { matches, timestamps, summaries }                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Shapes at Each Stage

### 3.1 Ingestion Pipeline Shapes

| Stage | Input Shape | Output Shape | dtype | Notes |
|:------|:------------|:-------------|:------|:------|
| Video Source | - | (H, W, 3) | uint8 | Variable resolution |
| Frame Sampler | (H, W, 3) | (224, 224, 3) | float32 | Normalized [-1, 1] |
| Batch Buffer | (224, 224, 3) | (B, 3, 224, 224) | float32 | B = batch size |
| Visual Encoder | (B, 3, 224, 224) | (B, 768) | float32 | L2-normalized |
| Event Detector | (W, 768) | Event | - | W = window size |
| Y-Decoder | (768,) + str | str | - | Max 150 tokens |

### 3.2 Query Pipeline Shapes

| Stage | Input Shape | Output Shape | dtype | Notes |
|:------|:------------|:-------------|:------|:------|
| Text Encoder | str | (384,) | float32 | Raw output |
| Projection | (384,) | (768,) | float32 | L2-normalized |
| Search | (768,) | List[(id, score)] | int64, float32 | Top-k results |
| Result | - | QueryResult | - | Structured |

---

## 4. Timing Constraints

### 4.1 Ingestion Timing (1 FPS target)

```
┌────────────────────────────────────────────────────────────────────┐
│                    1 SECOND BUDGET (1 FPS)                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Frame Read:     ███ 10ms                                          │
│  Resize+Norm:    ████ 20ms                                         │
│  V-JEPA Encode:  ████████████████████████████████████████ 200ms   │
│  Event Detect:   █ 5ms                                             │
│  Index Insert:   █ 5ms                                             │
│  (Summary Gen):  [████████████████████████████████] 500ms (async) │
│                  ───────────────────────────────────────────       │
│  TOTAL:          240ms (sync) + 500ms (async)                      │
│  SLACK:          760ms                                             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Query Timing Budget

```
┌────────────────────────────────────────────────────────────────────┐
│                    QUERY BUDGET (100ms target)                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Text Encode:    ████████████████████████████████████████ 50ms    │
│  Projection:     ██ 2ms                                            │
│  FAISS Search:   ████████ 10ms (10k vectors)                       │
│  DB Lookup:      ████████████████ 20ms                             │
│  Format:         ██ 2ms                                            │
│                  ───────────────────────────────────────────       │
│  TOTAL:          84ms                                              │
│  SLACK:          16ms                                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 5. Memory Flow

### 5.1 Memory Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY LIFECYCLE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TRANSIENT (freed after processing)                                          │
│  ├── Raw frame buffer: 6.2 MB per frame (1080p)                             │
│  ├── Resized frame: 150 KB                                                   │
│  ├── Intermediate activations: ~500 MB (during V-JEPA forward)              │
│  └── Token buffer: ~2 KB (during text encode)                               │
│                                                                              │
│  PERSISTENT (kept in memory during session)                                  │
│  ├── V-JEPA model: ~1.5 GB                                                  │
│  ├── MiniLM model: ~120 MB                                                  │
│  ├── Gemma-2B model: ~2.5 GB (INT8)                                         │
│  ├── FAISS index: ~12 MB per hour of video                                  │
│  └── Metadata cache: ~1 MB per hour of video                                │
│                                                                              │
│  ON-DISK (memory-mapped as needed)                                           │
│  ├── Embedding arrays: ~11 MB per hour (.npy)                               │
│  ├── SQLite database: ~5 MB per hour                                        │
│  └── Config/settings: <1 KB                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Peak Memory Analysis

| Scenario | Models | Index | Buffers | Total |
|:---------|:-------|:------|:--------|:------|
| Cold start (no video) | 4.1 GB | 0 | 0 | 4.1 GB |
| 30-min lecture | 4.1 GB | 6 MB | 100 MB | 4.3 GB |
| 1-hour lecture | 4.1 GB | 12 MB | 100 MB | 4.3 GB |
| 2-hour lecture | 4.1 GB | 24 MB | 100 MB | 4.3 GB |

**Conclusion:** Peak memory stays within 8 GB constraint for lectures up to 10+ hours.

---

## 6. Storage Layout

### 6.1 File Organization

```
data/
├── lectures/
│   └── <lecture_id>/
│       ├── metadata.db          # SQLite: frames, events, summaries (WAL mode)
│       ├── embeddings.npy       # NumPy: (N, 768) float32
│       ├── embeddings.npy.bak.1 # Backup (most recent)
│       ├── embeddings.npy.bak.2 # Backup (previous)
│       ├── index.faiss          # FAISS: IVF index
│       └── config.json          # Settings snapshot
├── models/
│   ├── vjepa-vit-l-16.safetensors  # Converted from .pth (see ARCHITECTURE.md 2.3)
│   ├── vjepa-vit-l-16.sha256       # Checksum for integrity verification
│   ├── all-MiniLM-L6-v2/
│   ├── gemma-2b-it-int8/
│   └── projection.pt               # Trained text-visual projection layer
└── cache/
    └── topic_vocabulary.json       # Optional: known topic embeddings for RAG
```

### 6.2 SQLite Schema

```sql
-- Frame metadata
CREATE TABLE frames (
    id INTEGER PRIMARY KEY,
    timestamp_ms INTEGER NOT NULL,
    embedding_idx INTEGER NOT NULL,
    source_path TEXT
);

-- Detected events
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    frame_id INTEGER REFERENCES frames(id),
    confidence REAL NOT NULL,
    event_type TEXT DEFAULT 'boundary'
);

-- Generated summaries
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    text TEXT NOT NULL,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_frames_timestamp ON frames(timestamp_ms);
CREATE INDEX idx_events_frame ON events(frame_id);
```

---

## 7. Validation Points

### 7.1 Input Validation

| Stage | Validation | Action on Failure |
|:------|:-----------|:------------------|
| Video Source | File exists, readable | Raise FileNotFoundError |
| Frame Sampler | Frame not None | Skip frame, log warning |
| Batch Buffer | Buffer not full | Process partial batch |
| Text Query | Length <= 256 chars | Truncate with warning |

### 7.2 Output Validation

| Stage | Invariant | Action on Failure |
|:------|:----------|:------------------|
| Visual Encoder | shape == (B, 768) | Raise ValueError |
| Visual Encoder | L2 norm ≈ 1.0 | Re-normalize |
| Projection | shape == (768,) | Raise ValueError |
| FAISS Search | len(results) <= k | OK (may have fewer) |
| Summary | len(tokens) <= 150 | Truncate |

---

## 8. Error Propagation

### 8.1 Error Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ERROR PROPAGATION                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  RECOVERABLE ERRORS (continue processing)                                    │
│  ├── Frame decode failure → Skip frame, continue                            │
│  ├── Single embedding failure → Skip frame, continue                        │
│  ├── Summary generation timeout → Store event without summary               │
│  └── Query timeout → Return partial results                                 │
│                                                                              │
│  FATAL ERRORS (stop processing)                                              │
│  ├── Model load failure → Cannot continue, require user action              │
│  ├── Out of memory → Cannot continue, require restart                       │
│  ├── Index corruption → Require rebuild from embeddings                     │
│  └── Database corruption → Require recovery from backup                     │
│                                                                              │
│  ERROR REPORTING                                                             │
│  ├── Log level: ERROR for fatal, WARNING for recoverable                    │
│  ├── User notification: Progress bar shows skip count                       │
│  └── Metrics: error_count, skip_rate tracked                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Concurrency Model

### 9.1 Thread/Process Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONCURRENCY MODEL                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MAIN THREAD                                                                 │
│  ├── Video capture loop                                                      │
│  ├── Frame sampling                                                          │
│  ├── UI updates (if applicable)                                             │
│  └── Query handling                                                          │
│                                                                              │
│  INFERENCE THREAD (or GPU stream)                                            │
│  ├── V-JEPA batch processing                                                │
│  ├── Event detection                                                         │
│  └── Index updates                                                           │
│                                                                              │
│  ASYNC TASKS (via asyncio or ThreadPool)                                     │
│  ├── Summary generation (CPU-bound, can be slow)                            │
│  ├── Storage writes (I/O-bound)                                             │
│  └── Cache warming                                                           │
│                                                                              │
│  SYNCHRONIZATION                                                             │
│  ├── Frame queue: Main → Inference (bounded, size=10)                       │
│  ├── Embedding queue: Inference → Storage (bounded, size=100)               │
│  └── Event queue: Inference → Async (unbounded, priority)                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Open Questions

- [Q1] **Projection layer training:** How to collect training pairs for text-visual alignment?
  - Proposed: Use captioned video datasets or synthetic pairs
  - Owner: ML_ENGINEER

- [Q2] **Batch size optimization:** What's the optimal batch size for CPU vs GPU?
  - Proposed: Profile and auto-tune based on available memory
  - Owner: ML_ENGINEER

- [Q3] **Streaming vs batch mode:** Should we support pure streaming (no batch buffer)?
  - Proposed: Start with batched, add streaming later
  - Owner: ARCHITECT

---

## 11. Approval Status

| Reviewer | Verdict | Date | Notes |
|:---------|:--------|:-----|:------|
| HOSTILE_REVIEWER | ✅ GO | 2024-12-31 | Approved with ARCHITECTURE.md |

---

*Data Flow Version: 1.1*
*Author: META_ARCHITECT*
*Project: VL-JEPA Lecture Summarizer*
