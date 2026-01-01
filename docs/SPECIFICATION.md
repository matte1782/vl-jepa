# VL-JEPA Lecture Summarizer — Specification v1.0

**Date:** 2024-12-31
**Author:** QA_LEAD
**Status:** APPROVED
**Prerequisite:** ARCHITECTURE.md v1.1 (APPROVED)

---

## 1. Overview

This specification defines testable requirements derived from the approved architecture. Each specification is numbered, maps to invariants, and includes edge cases and test requirements.

---

## 2. Specification Index

| Spec ID | Component | Description | Invariants |
|:--------|:----------|:------------|:-----------|
| S001 | Video Input | Video file ingestion | INV001, INV002 |
| S002 | Video Input | Stream ingestion | INV001, INV002 |
| S003 | Frame Sampler | Frame extraction and normalization | INV003, INV004 |
| S004 | Visual Encoder | V-JEPA embedding generation | INV005, INV006 |
| S005 | Event Detector | Semantic boundary detection | INV007, INV008 |
| S006 | Text Encoder | Query embedding with projection | INV009, INV010 |
| S007 | Embedding Index | FAISS index operations | INV011, INV012 |
| S008 | Y-Decoder | Summary generation | INV013, INV014 |
| S009 | Storage | Persistence and crash recovery | INV015, INV016 |
| S010 | Batch Processing | Memory-aware batching | INV017 |
| S011 | Query Pipeline | End-to-end query flow | Multiple |
| S012 | CLI Interface | Command-line operations | N/A |
| S013 | Gradio Interface | Web UI operations | N/A |

---

## 3. Detailed Specifications

### S001: Video File Ingestion

**Component:** Video Input Module
**Invariants:** INV001, INV002

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S001.R1 | Accept .mp4, .webm, .mkv, .avi video formats | P0 |
| S001.R2 | Return frames as BGR numpy arrays | P0 |
| S001.R3 | Provide frame timestamps in seconds | P0 |
| S001.R4 | Handle videos up to 4 hours duration | P1 |
| S001.R5 | Support seeking to arbitrary timestamp | P1 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV001 | Frame timestamps are monotonically increasing | Runtime assertion |
| INV002 | Frame buffer never exceeds 10 frames | Bounded queue |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC001 | Empty video file (0 frames) | Raise `VideoDecodeError` |
| EC002 | Corrupted video (decode fails) | Skip corrupted frames, log warning |
| EC003 | Very short video (<1 second) | Process all frames, may have 0-1 events |
| EC004 | Variable frame rate video | Use PTS timestamps, not frame count |
| EC005 | File path with spaces/unicode | Handle correctly via Path objects |
| EC006 | Non-existent file path | Raise `FileNotFoundError` |
| EC007 | File without video stream | Raise `VideoDecodeError` |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T001.1 | Unit | Load valid MP4 file |
| T001.2 | Unit | Load valid WebM file |
| T001.3 | Unit | Reject non-video file |
| T001.4 | Unit | Handle corrupted video |
| T001.5 | Unit | Verify timestamp monotonicity |
| T001.6 | Unit | Verify buffer size limit |
| T001.7 | Property | Timestamps always increasing |
| T001.8 | Integration | Process 1-hour lecture video |

---

### S002: Stream Ingestion

**Component:** Video Input Module
**Invariants:** INV001, INV002

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S002.R1 | Accept webcam device ID (integer) | P0 |
| S002.R2 | Accept RTSP stream URL | P1 |
| S002.R3 | Accept screen capture source | P2 |
| S002.R4 | Graceful handling of stream disconnection | P0 |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC008 | Invalid device ID | Raise `VideoDecodeError` with device info |
| EC009 | Network stream timeout | Retry 3 times, then raise `ConnectionError` |
| EC010 | Stream resolution change mid-capture | Adapt to new resolution |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T002.1 | Unit | Mock webcam device |
| T002.2 | Integration | RTSP stream (local test server) |
| T002.3 | Unit | Handle stream disconnection |

---

### S003: Frame Sampling and Normalization

**Component:** Frame Sampler
**Invariants:** INV003, INV004

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S003.R1 | Resize frames to exactly 224x224 pixels | P0 |
| S003.R2 | Convert BGR to RGB color space | P0 |
| S003.R3 | Normalize pixel values to [-1.0, 1.0] | P0 |
| S003.R4 | Sample at configurable FPS (0.1-30.0) | P0 |
| S003.R5 | Support center_crop, resize, pad modes | P1 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV003 | Output frames are exactly 224x224x3 | Shape assertion |
| INV004 | Pixel values in [-1.0, 1.0] | Clamp + assertion |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC011 | Non-square input (1920x1080) | Apply resize_mode correctly |
| EC012 | Very small input (64x64) | Upscale to 224x224 |
| EC013 | Grayscale input | Convert to 3-channel RGB |
| EC014 | Input with alpha channel | Drop alpha, keep RGB |
| EC015 | FPS higher than source FPS | Clamp to source FPS |
| EC016 | FPS = 0 | Raise `ValueError` |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T003.1 | Unit | Verify output shape 224x224x3 |
| T003.2 | Unit | Verify normalization range |
| T003.3 | Unit | Test center_crop mode |
| T003.4 | Unit | Test resize mode |
| T003.5 | Unit | Test pad mode |
| T003.6 | Property | Output always 224x224x3 |
| T003.7 | Property | Values always in [-1, 1] |
| T003.8 | Benchmark | Resize latency <20ms |

---

### S004: Visual Encoding (V-JEPA)

**Component:** Visual Encoder
**Invariants:** INV005, INV006

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S004.R1 | Accept batch of frames (B, 3, 224, 224) | P0 |
| S004.R2 | Output embeddings of shape (B, 768) | P0 |
| S004.R3 | L2-normalize output embeddings | P0 |
| S004.R4 | Support CPU and CUDA devices | P0 |
| S004.R5 | Load model from safetensors checkpoint | P0 |
| S004.R6 | Verify checkpoint integrity via SHA256 | P1 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV005 | Output embedding dimension is exactly 768 | Shape assertion |
| INV006 | Embeddings are L2-normalized (norm ≈ 1.0) | Normalization + assertion |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC017 | Batch size = 0 | Return empty tensor (0, 768) |
| EC018 | Batch size = 1 | Works correctly |
| EC019 | Missing checkpoint file | Raise `ModelLoadError` |
| EC020 | Corrupted checkpoint | Raise `ModelLoadError` |
| EC021 | Checkpoint checksum mismatch | Raise `ModelLoadError` |
| EC022 | GPU out of memory | Fall back to CPU with warning |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T004.1 | Unit | Verify output shape (B, 768) |
| T004.2 | Unit | Verify L2 normalization |
| T004.3 | Unit | Test batch size = 1 |
| T004.4 | Unit | Test batch size = 8 |
| T004.5 | Unit | Load from safetensors |
| T004.6 | Unit | Handle missing checkpoint |
| T004.7 | Property | Embedding dim always 768 |
| T004.8 | Property | L2 norm always ≈ 1.0 |
| T004.9 | Benchmark | Encode latency <200ms CPU |
| T004.10 | Benchmark | Encode latency <50ms GPU |

---

### S005: Event Detection

**Component:** Event Detector
**Invariants:** INV007, INV008

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S005.R1 | Detect semantic boundaries via embedding distance | P0 |
| S005.R2 | Apply smoothing window to reduce noise | P0 |
| S005.R3 | Enforce minimum gap between events | P0 |
| S005.R4 | Return confidence score for each event | P0 |
| S005.R5 | Configurable threshold (0.1-0.9) | P1 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV007 | Events are non-overlapping | min_event_gap enforcement |
| INV008 | Event confidence in [0.0, 1.0] | Clamp + assertion |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC023 | First frame (no previous) | No event emitted |
| EC024 | Identical consecutive frames | No event (distance = 0) |
| EC025 | Threshold = 0.0 | Event on every frame (after gap) |
| EC026 | Threshold = 1.0 | No events detected |
| EC027 | Smoothing window larger than history | Wait until buffer fills |
| EC028 | Very rapid topic changes | Respect min_event_gap |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T005.1 | Unit | Detect boundary on embedding change |
| T005.2 | Unit | No event on identical embeddings |
| T005.3 | Unit | Verify smoothing reduces noise |
| T005.4 | Unit | Verify min_event_gap enforcement |
| T005.5 | Unit | Confidence in [0, 1] |
| T005.6 | Property | Events never overlap |
| T005.7 | Property | Confidence always bounded |
| T005.8 | Benchmark | Detection latency <10ms |

---

### S006: Text Encoding with Projection

**Component:** Text Encoder (MiniLM)
**Invariants:** INV009, INV010

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S006.R1 | Encode text queries to 384-dim embeddings | P0 |
| S006.R2 | Project to 768-dim aligned space | P0 |
| S006.R3 | L2-normalize projected embeddings | P0 |
| S006.R4 | Support batch encoding | P1 |
| S006.R5 | Truncate queries >256 tokens | P0 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV009 | Output embedding dimension is 768 | Shape assertion |
| INV010 | Query embedding is L2-normalized | Normalization + assertion |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC029 | Empty query string | Raise `ValueError` |
| EC030 | Query >256 tokens | Truncate with warning |
| EC031 | Non-ASCII characters | Handle UTF-8 correctly |
| EC032 | Only whitespace | Raise `ValueError` |
| EC033 | Very short query (1 word) | Works correctly |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T006.1 | Unit | Verify output shape (768,) |
| T006.2 | Unit | Verify L2 normalization |
| T006.3 | Unit | Handle long query truncation |
| T006.4 | Unit | Reject empty query |
| T006.5 | Unit | Batch encoding works |
| T006.6 | Property | Dimension always 768 |
| T006.7 | Property | L2 norm always ≈ 1.0 |
| T006.8 | Benchmark | Encode latency <50ms |

---

### S007: Embedding Index (FAISS)

**Component:** Embedding Index
**Invariants:** INV011, INV012

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S007.R1 | Add embeddings with unique IDs | P0 |
| S007.R2 | Search returns top-k similar embeddings | P0 |
| S007.R3 | Use flat index for <1000 vectors | P0 |
| S007.R4 | Use IVF index for >=1000 vectors | P0 |
| S007.R5 | Save and load index from disk | P0 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV011 | Index contains all processed embeddings | Count assertion |
| INV012 | Search returns ≤k results | Return value check |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC034 | Empty index search | Return empty list |
| EC035 | k > total vectors | Return all vectors |
| EC036 | Duplicate embedding ID | Update existing entry |
| EC037 | Index with 0 vectors | Valid, returns empty on search |
| EC038 | IVF transition (999→1000 vectors) | Rebuild with IVF |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T007.1 | Unit | Add single embedding |
| T007.2 | Unit | Add batch embeddings |
| T007.3 | Unit | Search returns correct top-k |
| T007.4 | Unit | Search empty index |
| T007.5 | Unit | Save and load index |
| T007.6 | Unit | IVF transition |
| T007.7 | Property | All added vectors searchable |
| T007.8 | Property | Results ≤ k |
| T007.9 | Benchmark | Search 10k vectors <10ms |
| T007.10 | Benchmark | Search 100k vectors <100ms |

---

### S008: Summary Generation (Y-Decoder)

**Component:** Y-Decoder (Gemma-2B)
**Invariants:** INV013, INV014

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S008.R1 | Generate summary from event context | P0 |
| S008.R2 | Use prompt template for context injection | P0 |
| S008.R3 | Limit output to 150 tokens | P0 |
| S008.R4 | Support INT8 quantization | P0 |
| S008.R5 | Timeout after 30s (CPU) / 5s (GPU) | P0 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV013 | Output length ≤ 150 tokens | max_new_tokens param |
| INV014 | Generation completes within timeout | asyncio.timeout |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC039 | No previous summary (first event) | Use "Start of lecture" |
| EC040 | No OCR text available | Use "No text detected" |
| EC041 | Generation timeout | Return partial or empty summary |
| EC042 | Model produces empty output | Return "[Summary unavailable]" |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T008.1 | Unit | Generate summary with full context |
| T008.2 | Unit | Generate summary without OCR |
| T008.3 | Unit | Verify output length ≤ 150 tokens |
| T008.4 | Unit | Handle timeout gracefully |
| T008.5 | Benchmark | Generation <30s CPU |
| T008.6 | Benchmark | Generation <5s GPU |

---

### S009: Storage and Crash Recovery

**Component:** Storage Layer
**Invariants:** INV015, INV016

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S009.R1 | Store metadata in SQLite with WAL mode | P0 |
| S009.R2 | Store embeddings in NumPy files | P0 |
| S009.R3 | Atomic writes via temp file + rename | P0 |
| S009.R4 | Auto-backup every 100 embeddings | P1 |
| S009.R5 | Recover from crash on startup | P0 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV015 | All writes are atomic | Temp file pattern |
| INV016 | Data survives process crash | WAL + fsync |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC043 | Crash during embedding write | Recover from backup |
| EC044 | Crash during SQLite write | WAL auto-recovery |
| EC045 | Disk full | Raise `IOError`, stop ingestion |
| EC046 | Corrupted backup file | Skip to older backup |
| EC047 | Missing WAL file | SQLite handles automatically |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T009.1 | Unit | Atomic write succeeds |
| T009.2 | Unit | Atomic write rollback on failure |
| T009.3 | Unit | Backup creation |
| T009.4 | Unit | Recovery from crash state |
| T009.5 | Unit | WAL mode enabled |
| T009.6 | Integration | Simulate crash + recovery |

---

### S010: Memory-Aware Batching

**Component:** Batch Processing
**Invariants:** INV017

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S010.R1 | Auto-detect available memory | P0 |
| S010.R2 | Select batch size based on device | P0 |
| S010.R3 | Process partial batches immediately | P0 |
| S010.R4 | Never exceed available memory | P0 |

#### Invariants

| INV ID | Statement | Enforcement |
|:-------|:----------|:------------|
| INV017 | Batch size never exceeds available memory | Runtime calculation |

#### Edge Cases

| EC ID | Scenario | Expected Behavior |
|:------|:---------|:------------------|
| EC048 | Very low memory (2GB) | Batch size = 1 |
| EC049 | Memory changes during processing | Recalculate on next batch |
| EC050 | Partial batch at end of video | Process immediately |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T010.1 | Unit | Batch size calculation |
| T010.2 | Unit | Partial batch processing |
| T010.3 | Property | Never OOM |
| T010.4 | Integration | Long video without OOM |

---

### S011: Query Pipeline (End-to-End)

**Component:** Query Flow
**Invariants:** Multiple (INV009, INV010, INV011, INV012)

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S011.R1 | Accept natural language query | P0 |
| S011.R2 | Return top-k results with timestamps | P0 |
| S011.R3 | Include summaries in results | P0 |
| S011.R4 | Complete within 100ms budget | P0 |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T011.1 | Integration | End-to-end query |
| T011.2 | Integration | Query with no matches |
| T011.3 | Benchmark | Query latency <100ms |

---

### S012: CLI Interface

**Component:** Command Line
**Invariants:** N/A

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S012.R1 | `vl-jepa process <video>` command | P0 |
| S012.R2 | `vl-jepa query <data_dir>` command | P0 |
| S012.R3 | `vl-jepa serve <data_dir>` command | P1 |
| S012.R4 | Progress bar during processing | P1 |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T012.1 | Unit | Parse process command |
| T012.2 | Unit | Parse query command |
| T012.3 | Integration | CLI end-to-end |

---

### S013: Gradio Web Interface

**Component:** Web UI
**Invariants:** N/A

#### Requirements

| Req ID | Description | Priority |
|:-------|:------------|:---------|
| S013.R1 | Video upload component | P0 |
| S013.R2 | Processing progress display | P0 |
| S013.R3 | Query input and results display | P0 |
| S013.R4 | Event timeline visualization | P1 |

#### Test Requirements

| TEST ID | Type | Description |
|:--------|:-----|:------------|
| T013.1 | Integration | Launch Gradio app |
| T013.2 | Integration | Upload and process video |
| T013.3 | Integration | Execute query |

---

## 4. Coverage Summary

### Specification Coverage

| Category | Count |
|:---------|:------|
| Specifications | 13 |
| Requirements | 54 |
| Invariants | 17 |
| Edge Cases | 50 |
| Test Requirements | 74 |

### Test Type Distribution

| Test Type | Count |
|:----------|:------|
| Unit Tests | 42 |
| Property Tests | 14 |
| Integration Tests | 7 |
| Benchmark Tests | 11 |
| **Total** | **74** |

### Coverage Targets

| Metric | Target |
|:-------|:-------|
| Line Coverage | >90% |
| Branch Coverage | >85% |
| Spec Coverage | 100% |

---

## 5. Approval Status

| Reviewer | Verdict | Date |
|:---------|:--------|:-----|
| HOSTILE_REVIEWER | ✅ GO | 2024-12-31 |

---

*Specification Version: 1.0*
*Author: QA_LEAD*
*Project: VL-JEPA Lecture Summarizer*
