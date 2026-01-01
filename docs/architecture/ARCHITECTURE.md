# VL-JEPA Lecture Summarizer Architecture v1.0

**Date:** 2024-12-30
**Author:** META_ARCHITECT
**Status:** PROPOSED

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VL-JEPA LECTURE SUMMARIZER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   VIDEO     │    │   FRAME     │    │   VISUAL    │    │   EVENT     │  │
│  │   INPUT     │───▶│   SAMPLER   │───▶│   ENCODER   │───▶│  DETECTOR   │  │
│  │             │    │  (1-2 FPS)  │    │  (V-JEPA)   │    │ (threshold) │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘  │
│                                              │                    │         │
│                                              ▼                    ▼         │
│                                        ┌─────────────┐    ┌─────────────┐  │
│                                        │  EMBEDDING  │    │  Y-DECODER  │  │
│                                        │    INDEX    │    │ (Gemma-2B)  │  │
│                                        │   (FAISS)   │    │             │  │
│                                        └──────┬──────┘    └──────┬──────┘  │
│                                               │                   │         │
│                                               ▼                   ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   USER      │    │    TEXT     │    │  SIMILARITY │    │   SUMMARY   │  │
│  │   QUERY     │───▶│   ENCODER   │───▶│   SEARCH    │    │   OUTPUT    │  │
│  │             │    │ (MiniLM)    │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         STORAGE LAYER                                │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │  │   SQLite    │    │   Numpy     │    │   Config    │              │   │
│  │  │  (metadata) │    │ (embeddings)│    │   (JSON)    │              │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Video Input Module

- **Purpose:** Ingest video from file or stream (webcam/screen capture)
- **Inputs:** Video file path OR stream URL OR device ID
- **Outputs:** Raw video frames (BGR, variable resolution)
- **Invariants:**
  - INV001: Frame timestamps are monotonically increasing
  - INV002: Frame buffer never exceeds 10 frames (memory bound)

### 2.2 Frame Sampler

- **Purpose:** Sample frames at configurable FPS for embedding
- **Inputs:** Raw video frames with timestamps
- **Outputs:** Sampled frames (224x224, RGB, normalized)
- **Invariants:**
  - INV003: Output frames are exactly 224x224x3
  - INV004: Frames are normalized to [-1, 1] range (V-JEPA requirement)

**Configuration:**
- `fps`: Target frames per second (default: 1.0, range: 0.1-30.0)
- `resize_mode`: "center_crop" | "resize" | "pad"

### 2.3 Visual Encoder (V-JEPA)

- **Purpose:** Encode video frames to semantic embeddings
- **Inputs:** Batch of frames (B, 3, 224, 224)
- **Outputs:** Embeddings (B, 768)
- **Invariants:**
  - INV005: Output embedding dimension is exactly 768
  - INV006: Embeddings are L2-normalized

**Model Specification:**
- Architecture: ViT-L/16
- Input: 224x224 RGB images
- Output: 768-dimensional embeddings
- Checkpoint: `vjepa-vit-l-16.pth` (from Meta, PyTorch format)

**Checkpoint Loading Protocol:**
1. Download `.pth` checkpoint from Meta's official V-JEPA repository
2. Convert to safetensors format using `torch.save()` → `safetensors.torch.save_file()`
3. Store as `models/vjepa-vit-l-16.safetensors` for secure loading
4. Verify SHA256 checksum matches published hash

**[HYPOTHESIS]** V-JEPA embeddings are semantically meaningful for lecture content. Requires validation.

### 2.4 Event Detector

- **Purpose:** Detect semantic boundaries (topic changes, slide transitions)
- **Inputs:** Sequence of embeddings with timestamps
- **Outputs:** Event boundaries with confidence scores
- **Invariants:**
  - INV007: Events are non-overlapping
  - INV008: Event confidence in [0.0, 1.0]

**Algorithm (with smoothing):**
```python
# Maintain sliding window buffer
window_buffer: deque[ndarray] = deque(maxlen=smoothing_window)
last_event_time: float = -inf

for each new embedding e_t at timestamp t:
    window_buffer.append(e_t)

    if len(window_buffer) < smoothing_window:
        continue  # Wait for buffer to fill

    # Compute smoothed embedding (mean of window)
    e_smoothed = mean(window_buffer, axis=0)
    e_smoothed = e_smoothed / norm(e_smoothed)  # Re-normalize

    # Compare against previous smoothed embedding
    if e_prev_smoothed is not None:
        distance = 1 - cosine_similarity(e_smoothed, e_prev_smoothed)

        # Check threshold AND minimum gap
        if distance > threshold and (t - last_event_time) >= min_event_gap:
            confidence = min(1.0, distance)  # Clamp to [0, 1]
            emit Event(timestamp=t, confidence=confidence)
            last_event_time = t

    e_prev_smoothed = e_smoothed
```

**Configuration:**
- `threshold`: Detection threshold (default: 0.3, range: 0.1-0.9)
- `min_event_gap`: Minimum seconds between events (default: 10)
- `smoothing_window`: Frames to average for stability (default: 3)

### 2.5 Text Encoder (MiniLM)

- **Purpose:** Encode user queries to embedding space
- **Inputs:** Text query string
- **Outputs:** Query embedding (384-dim, projected to 768)
- **Invariants:**
  - INV009: Output embedding dimension matches visual encoder (768)
  - INV010: Query embedding is L2-normalized

**Model Specification:**
- Model: `all-MiniLM-L6-v2`
- Input: Text string (max 256 tokens)
- Native output: 384-dimensional
- Projection: Linear layer 384 to 768

**Projection Layer Training Strategy:**

The projection layer aligns MiniLM text embeddings with V-JEPA visual embeddings. Training approach:

1. **Dataset:** Use captioned video datasets (e.g., HowTo100M subset, lecture recordings with transcripts)
2. **Training objective:** Contrastive loss (InfoNCE)
   ```python
   # For batch of (text, frame) pairs:
   text_emb = projection(minilm_encode(text))  # (B, 768)
   visual_emb = vjepa_encode(frame)             # (B, 768)

   # Cosine similarity matrix
   sim = text_emb @ visual_emb.T  # (B, B)

   # InfoNCE loss (symmetric)
   labels = torch.arange(B)
   loss = (cross_entropy(sim, labels) + cross_entropy(sim.T, labels)) / 2
   ```
3. **Training size:** ~10K aligned pairs sufficient for domain adaptation
4. **Fallback:** If no training data available, use frozen random projection (degraded but functional)

**[VALIDATED]** Projection approach follows established vision-language alignment methods (CLIP, ALIGN).

### 2.6 Embedding Index (FAISS)

- **Purpose:** Store and search embeddings efficiently
- **Inputs:** Embeddings with metadata (timestamp, frame_id)
- **Outputs:** Top-k similar embeddings for query
- **Invariants:**
  - INV011: Index contains all processed embeddings
  - INV012: Search returns exactly k results (or all if less than k exist)

**Index Configuration:**
- Type: `IndexIVFFlat` for large collections, `IndexFlatIP` for small
- Metric: Inner product (on L2-normalized vectors = cosine similarity)
- nlist: 100 (number of clusters for IVF)
- nprobe: 10 (clusters to search)

**IVF Training Procedure:**

IVF index requires training on representative vectors before use:

1. **Trigger condition:** When embedding count exceeds 1,000 vectors
2. **Training process:**
   ```python
   # Start with flat index for small collections
   if num_embeddings < 1000:
       index = faiss.IndexFlatIP(768)
   else:
       # Train IVF when threshold exceeded
       quantizer = faiss.IndexFlatIP(768)
       index = faiss.IndexIVFFlat(quantizer, 768, nlist=100)

       # Train on first N embeddings (or all if < 10k)
       training_vectors = embeddings[:min(10000, len(embeddings))]
       index.train(training_vectors)

       # Add all embeddings to trained index
       index.add(embeddings)
   ```
3. **Retraining:** Rebuild index when embedding count doubles from last training
4. **Cold start:** Use IndexFlatIP (exact search) until enough vectors for IVF

### 2.7 Y-Decoder (Gemma-2B)

- **Purpose:** Generate natural language summaries from visual context
- **Inputs:** Event context (timestamps, surrounding frame descriptions, previous summaries)
- **Outputs:** Summary text (1-3 sentences)
- **Invariants:**
  - INV013: Output length is at most 150 tokens
  - INV014: Generation completes within timeout (30s CPU, 5s GPU)

**Model Specification:**
- Model: `google/gemma-2b-it`
- Max output tokens: 150
- Temperature: 0.7
- Quantization: INT8 for CPU deployment

**Prompt Engineering Strategy:**

Since Gemma-2B is a text-to-text model, we cannot feed raw embeddings directly. Instead:

1. **Context Construction:** Build text prompt from metadata and retrieved context
   ```python
   def build_summary_prompt(event: Event, context: EventContext) -> str:
       prompt = f"""You are summarizing a lecture video segment.

   Segment Information:
   - Timestamp: {format_timestamp(event.timestamp_s)}
   - Duration since last topic: {event.timestamp_s - context.prev_event_time:.0f} seconds
   - Event type: {event.event_type} (confidence: {event.confidence:.2f})

   Previous segment summary: {context.prev_summary or "Start of lecture"}

   Nearby content indicators:
   {context.ocr_text or "No text detected on screen"}

   Generate a 1-2 sentence summary of what likely happened in this segment.
   Focus on topic transitions, key concepts, or visual changes.

   Summary:"""
       return prompt
   ```

2. **Context Sources:**
   - Previous event summaries (temporal coherence)
   - OCR text from frames (optional, if slide text extraction enabled)
   - Embedding similarity to known lecture topics (from topic vocabulary)
   - Time elapsed since last event

3. **Alternative: Retrieval-Augmented Generation**
   - Use event embedding to retrieve similar segments from training corpus
   - Include retrieved summaries as few-shot examples in prompt

**[DECISION]** Prompt-based approach selected over soft-prompting due to:
- No additional training required
- Interpretable and debuggable
- Works with quantized models

### 2.8 Storage Layer

- **Purpose:** Persist embeddings, metadata, and configuration
- **Invariants:**
  - INV015: All writes are atomic (no partial states)
  - INV016: Data survives process crash

**Components:**
- **SQLite database:** Metadata, timestamps, event markers
- **NumPy files:** Embedding vectors (memory-mapped for large lectures)
- **JSON config:** User settings, model paths

**Atomicity & Crash Recovery Implementation:**

1. **SQLite Configuration:**
   ```python
   # Enable WAL mode for crash safety
   connection.execute("PRAGMA journal_mode=WAL")
   connection.execute("PRAGMA synchronous=NORMAL")  # Balance speed/safety
   connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # On clean shutdown
   ```

2. **Embedding File Writes (atomic via rename):**
   ```python
   def save_embeddings_atomic(embeddings: np.ndarray, path: Path) -> None:
       temp_path = path.with_suffix('.tmp')
       np.save(temp_path, embeddings)
       os.fsync(open(temp_path, 'rb').fileno())  # Force to disk
       temp_path.rename(path)  # Atomic on POSIX, nearly atomic on Windows
   ```

3. **Backup Strategy:**
   - Auto-backup on every 100 new embeddings
   - Keep last 3 backups: `embeddings.npy.bak.1`, `.bak.2`, `.bak.3`
   - Backup SQLite via `.backup()` API

4. **Recovery Procedure:**
   ```python
   def recover_from_crash(lecture_path: Path) -> bool:
       db_path = lecture_path / "metadata.db"
       emb_path = lecture_path / "embeddings.npy"

       # Check for WAL recovery
       if (db_path.with_suffix('.db-wal')).exists():
           # SQLite auto-recovers on next open
           conn = sqlite3.connect(db_path)
           conn.execute("PRAGMA wal_checkpoint(RESTART)")

       # Check embedding consistency
       if not emb_path.exists() and (emb_path.with_suffix('.tmp')).exists():
           # Incomplete write - restore from backup
           backup = find_latest_backup(emb_path)
           if backup:
               shutil.copy(backup, emb_path)
               return True
           return False  # Unrecoverable

       return True  # No recovery needed
   ```

**[ENFORCED]** INV015 and INV016 are enforced via WAL mode and atomic rename pattern.

---

## 3. Data Flow

### 3.1 Ingestion Flow (Real-time)

```
Video Source
    │
    ▼
[Frame Sampler] ──────▶ frames: (224, 224, 3) @ 1 FPS
    │
    ▼
[Visual Encoder] ─────▶ embeddings: (768,) per frame
    │
    ├──────────────────▶ [Embedding Index] (append)
    │
    ▼
[Event Detector] ─────▶ event_detected: bool
    │
    ▼ (if event)
[Y-Decoder] ──────────▶ summary: str
    │
    ▼
[Storage] ────────────▶ SQLite + NumPy files
```

### 3.2 Query Flow (Interactive)

```
User Query
    │
    ▼
[Text Encoder] ───────▶ query_embedding: (768,)
    │
    ▼
[Embedding Index] ────▶ top_k_results: [(frame_id, score), ...]
    │
    ▼
[Storage] ────────────▶ metadata: timestamps, summaries
    │
    ▼
[Response Builder] ───▶ formatted response + video timestamps
```

---

## 4. Memory Layout

### 4.1 Per-Frame Memory

| Component | Size | Notes |
|:----------|:-----|:------|
| Raw frame (1080p) | 6.2 MB | 1920x1080x3 bytes |
| Resized frame (224x224) | 150 KB | 224x224x3 bytes |
| Embedding (float32) | 3 KB | 768 x 4 bytes |
| Metadata | ~100 bytes | timestamp, frame_id |

### 4.2 Lecture Storage Estimates

| Duration | Frames (1 FPS) | Embeddings | Index Size | Total |
|:---------|:---------------|:-----------|:-----------|:------|
| 30 min | 1,800 | 5.4 MB | ~6 MB | ~12 MB |
| 1 hour | 3,600 | 10.8 MB | ~12 MB | ~25 MB |
| 2 hours | 7,200 | 21.6 MB | ~24 MB | ~50 MB |

### 4.3 Model Memory

| Model | Size (disk) | Size (RAM) | Notes |
|:------|:------------|:-----------|:------|
| V-JEPA ViT-L/16 | ~1.2 GB | ~1.5 GB | Float16 |
| MiniLM-L6-v2 | ~90 MB | ~120 MB | Float32 |
| Gemma-2B (INT8) | ~2 GB | ~2.5 GB | Quantized |
| **Total** | ~3.3 GB | ~4.1 GB | |

**[FACT]** Total memory budget: ~4GB for models + ~50MB for 2-hour lecture = within 8GB RAM constraint.

### 4.4 Batch Size Constraints

| Device | Available RAM | Max Batch Size | Activation Memory | Notes |
|:-------|:--------------|:---------------|:------------------|:------|
| CPU (8GB) | ~3.5 GB free | 1 | ~500 MB | Sequential processing |
| CPU (16GB) | ~11 GB free | 4 | ~2 GB | Modest parallelism |
| GPU (4GB VRAM) | ~2.5 GB free | 2 | ~1 GB | Entry-level GPU |
| GPU (8GB VRAM) | ~6.5 GB free | 8 | ~2.5 GB | Mid-range GPU |
| GPU (16GB VRAM) | ~14 GB free | 16 | ~5 GB | High-end GPU |

**Batch Size Selection Logic:**
```python
def select_batch_size(device: str, available_memory_gb: float) -> int:
    # Reserve 1.5GB for V-JEPA model, 0.5GB for safety margin
    usable_memory = available_memory_gb - 2.0

    # Each frame in batch requires ~300MB for activations
    activation_per_frame_gb = 0.3

    max_batch = max(1, int(usable_memory / activation_per_frame_gb))

    # Clamp to power of 2 for efficiency
    return min(16, 2 ** int(log2(max_batch)))
```

**Incomplete Batch Handling:**
- Process partial batches immediately (no waiting)
- Pad batch to power-of-2 for GPU efficiency (optional)
- INV017: Batch size never exceeds available memory

---

## 5. Performance Budget

| Operation | Target (CPU) | Target (GPU) | Constraint |
|:----------|:-------------|:-------------|:-----------|
| Frame encode (V-JEPA) | <200ms | <50ms | Per frame |
| Event detection | <10ms | <5ms | Per frame |
| Query encode (MiniLM) | <50ms | <10ms | Per query |
| Similarity search (10k) | <10ms | <5ms | P99 |
| Similarity search (100k) | <100ms | <20ms | P99 |
| Summary generation | <30s | <5s | Per event |
| Index load (2hr lecture) | <1s | <500ms | Cold start |

---

## 6. Failure Modes

| Failure | Detection | Recovery |
|:--------|:----------|:---------|
| GPU not available | CUDA check fails | Fall back to CPU |
| Model file missing | FileNotFoundError | Prompt download, provide URL |
| Out of memory | MemoryError | Reduce batch size, enable streaming |
| Video decode fails | OpenCV/decord error | Log error, skip frame, continue |
| Index corrupted | Checksum mismatch | Rebuild from embeddings |
| Storage full | IOError | Alert user, stop ingestion |

---

## 7. Security Considerations

### 7.1 Data Privacy

- All processing is local by default
- No network calls without explicit user consent
- Video files are not retained unless explicitly saved
- Embeddings are stored, but cannot reconstruct original video

### 7.2 Model Security

- Models loaded from local files only (no auto-download by default)
- Safetensors format preferred for model weights (secure serialization)
- Model integrity verified by checksum

### 7.3 Input Validation

- Video file paths validated (no path traversal)
- Query strings sanitized (max length enforced)
- Configuration values bounded (no arbitrary code execution)

---

## 8. Open Questions

- [Q1] **Embedding alignment:** ~~How well do V-JEPA visual embeddings align with MiniLM text embeddings?~~
  - **Status:** ✅ RESOLVED — Contrastive projection training strategy defined in Section 2.5
  - **Owner:** ML_ENGINEER

- [Q2] **Event detection threshold:** What is the optimal threshold for lecture content?
  - **Status:** OPEN — Requires empirical tuning during implementation
  - **Owner:** QA_LEAD
  - **Deadline:** Gate 5 (Implementation)

- [Q3] **Decoder prompt:** ~~What prompt format produces best summaries from Gemma-2B?~~
  - **Status:** ✅ RESOLVED — Prompt engineering strategy defined in Section 2.7
  - **Owner:** ML_ENGINEER

- [Q4] **Real-time streaming:** Can we maintain 1 FPS processing on M1 MacBook Air (CPU only)?
  - **Status:** OPEN — Requires benchmarking during implementation
  - **Owner:** ML_ENGINEER
  - **Deadline:** Gate 5 (Implementation)

---

## 9. Dependencies

### 9.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4  # or faiss-gpu
decord>=0.6.0
opencv-python>=4.8.0
gradio>=4.0.0
sqlalchemy>=2.0.0
numpy>=1.24.0
```

### 9.2 External Models

| Model | Source | License |
|:------|:-------|:--------|
| V-JEPA ViT-L/16 | Meta (GitHub) | CC-BY-NC |
| all-MiniLM-L6-v2 | HuggingFace | Apache 2.0 |
| Gemma-2B | Google | Gemma License |

**[UNKNOWN]** V-JEPA license may restrict commercial use. Verify before release.

---

## 10. Approval Status

| Reviewer | Verdict | Date | Notes |
|:---------|:--------|:-----|:------|
| HOSTILE_REVIEWER | ⚠️ CONDITIONAL_GO | 2024-12-31 | Initial review |
| HOSTILE_REVIEWER | ✅ GO | 2024-12-31 | All issues addressed |

---

## 11. Revision History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | 2024-12-30 | Initial architecture |
| 1.1 | 2024-12-31 | Addressed hostile review findings: C1-C8 |

**Changes in v1.1:**
- Added checkpoint loading protocol (C2)
- Updated event detection algorithm with smoothing (C4)
- Added projection layer training strategy (C1)
- Added IVF training procedure (C7)
- Added Y-Decoder prompt engineering strategy (C3)
- Added storage atomicity and crash recovery (C8)
- Added batch size constraints table (C5)
- Added INV017 (batch size memory constraint)

---

*Architecture Version: 1.1*
*Author: META_ARCHITECT*
*Project: VL-JEPA Lecture Summarizer*
