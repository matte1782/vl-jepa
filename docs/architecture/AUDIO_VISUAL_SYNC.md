# Audio-Visual Timestamp Synchronization Strategy

> **Version**: 1.0
> **Created**: 2026-01-01
> **Status**: APPROVED (Week 2)
> **Implements**: v0.2.0 G7 - Audio Transcription

---

## Overview

This document defines how audio (transcript) and visual (frame) timestamps are synchronized in the lecture-mind system.

---

## Timestamp Sources

### 1. Visual Pipeline (DINOv2)

| Component | Timestamp Source | Unit | Precision |
|-----------|------------------|------|-----------|
| Video frames | FFmpeg extraction | seconds | millisecond |
| Frame embeddings | Frame position / FPS | seconds | 1/FPS |

**Frame timestamp calculation:**
```python
def frame_timestamp(frame_index: int, fps: float) -> float:
    """Calculate timestamp from frame index and FPS."""
    return frame_index / fps
```

### 2. Audio Pipeline (Whisper)

| Component | Timestamp Source | Unit | Precision |
|-----------|------------------|------|-----------|
| Audio segments | Whisper transcription | seconds | ~10ms |
| Transcript chunks | Derived from segments | seconds | ~10ms |

**Segment structure:**
```python
@dataclass
class TranscriptSegment:
    text: str
    start: float  # seconds from audio start
    end: float    # seconds from audio start
    confidence: float
    language: str
```

---

## Synchronization Strategy

### 1. Common Time Base

Both pipelines use **seconds from video start** as the common time base.

```
Video Start (t=0)
    |
    |-- Frame 0 extracted
    |-- Audio track begins
    |
    |-- Frame 30 (t=1.0s at 30fps)
    |-- Transcript: "Good morning..." (t=0.8s - 2.1s)
    |
    |-- Frame 60 (t=2.0s)
    |
    ...
```

### 2. Alignment Tolerance

| Scenario | Tolerance | Rationale |
|----------|-----------|-----------|
| Frame-to-transcript search | ±1.0s | Speech context spans ~2-3 seconds |
| Transcript-to-frame search | ±0.5s | Visual change should be visible |
| Chunk overlap | 5s | Prevents context loss at boundaries |

### 3. Query Time Resolution

When querying by timestamp:
- **Text queries**: Return transcript segments where `query_time` falls within `[start - 0.5s, end + 0.5s]`
- **Visual queries**: Return frames within `[query_time - 1.0s, query_time + 1.0s]`

---

## Implementation Details

### 1. Video → Audio Alignment

```python
def align_frame_to_transcript(
    frame_time: float,
    segments: list[TranscriptSegment],
    tolerance: float = 1.0,
) -> list[TranscriptSegment]:
    """Find transcript segments near a frame timestamp.

    Args:
        frame_time: Frame timestamp in seconds
        segments: All transcript segments
        tolerance: Maximum time difference (default 1.0s)

    Returns:
        Segments overlapping the tolerance window
    """
    results = []
    window_start = frame_time - tolerance
    window_end = frame_time + tolerance

    for seg in segments:
        # Check if segment overlaps with window
        if seg.end >= window_start and seg.start <= window_end:
            results.append(seg)

    return results
```

### 2. Audio → Video Alignment

```python
def align_transcript_to_frames(
    segment: TranscriptSegment,
    frame_times: list[float],
    tolerance: float = 0.5,
) -> list[int]:
    """Find frame indices near a transcript segment.

    Args:
        segment: Transcript segment
        frame_times: All frame timestamps
        tolerance: Maximum time difference (default 0.5s)

    Returns:
        Frame indices within the tolerance window
    """
    results = []
    window_start = segment.start - tolerance
    window_end = segment.end + tolerance

    for i, t in enumerate(frame_times):
        if window_start <= t <= window_end:
            results.append(i)

    return results
```

### 3. Multimodal Index Entry

Each index entry stores synchronized timestamps:

```python
@dataclass
class IndexEntry:
    """Multimodal index entry with synchronized timestamps."""

    # Identifiers
    video_id: str
    entry_type: Literal["frame", "transcript"]

    # Common timestamp
    timestamp: float  # seconds from video start

    # Embedding
    embedding: np.ndarray

    # Type-specific data
    frame_index: int | None = None  # For frame entries
    segment_id: int | None = None   # For transcript entries
    text: str | None = None         # For transcript entries
```

---

## Chunking Strategy for Alignment

Transcript chunks are designed to align with visual context:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `window_size` | 30s | Matches typical lecture slide duration |
| `overlap` | 5s | Captures context across boundaries |
| `min_text_length` | 10 chars | Filters empty/noise segments |

```python
chunker = TranscriptChunker(
    window_size=30.0,
    overlap=5.0,
    min_text_length=10,
)

for chunk in chunker.chunk(segments):
    # chunk.start aligns with video time
    # chunk.end aligns with video time
    # Search for frames in this time window
    frame_indices = align_transcript_to_frames(chunk, frame_times)
```

---

## Edge Cases

### 1. Audio Delay in Video

**Problem**: Some lecture videos have audio offset (sync issues in recording).

**Detection**:
```python
def detect_audio_offset(video_path: str) -> float:
    """Detect audio track offset if metadata available."""
    # FFprobe can detect stream start times
    # Returns offset in seconds (typically 0)
    ...
```

**Mitigation**: Apply offset to all audio timestamps before alignment.

### 2. Variable Frame Rate (VFR)

**Problem**: Some video sources have variable frame rate.

**Detection**:
```python
def is_variable_framerate(video_path: str) -> bool:
    """Check if video has variable frame rate."""
    # Compare duration * FPS vs frame count
    ...
```

**Mitigation**: Use FFmpeg's `-vsync cfr` to convert to constant frame rate during extraction.

### 3. Silence Gaps

**Problem**: Whisper may skip silent sections, creating gaps in transcript timeline.

**Mitigation**:
- Gaps are natural and expected
- Search uses tolerance windows to bridge small gaps
- Large gaps (>5s) may indicate slide changes or pauses

---

## Testing Strategy

### Unit Tests

```python
def test_frame_to_transcript_alignment():
    """Test basic alignment within tolerance."""
    segments = [
        TranscriptSegment("Hello", 0.0, 2.0, 0.9, "en"),
        TranscriptSegment("World", 2.5, 4.0, 0.9, "en"),
    ]

    # Frame at t=1.5s should match "Hello" segment
    result = align_frame_to_transcript(1.5, segments, tolerance=1.0)
    assert len(result) == 1
    assert result[0].text == "Hello"

def test_transcript_to_frame_alignment():
    """Test reverse alignment."""
    frame_times = [0.0, 1.0, 2.0, 3.0, 4.0]
    segment = TranscriptSegment("Test", 1.5, 2.5, 0.9, "en")

    # Should find frames at t=1.0, 2.0, 3.0
    result = align_transcript_to_frames(segment, frame_times, tolerance=0.5)
    assert result == [1, 2, 3]
```

### Integration Tests (Week 3)

```python
def test_audio_visual_sync_real_video():
    """Test with real lecture video."""
    # Extract frames at 1 FPS
    # Transcribe audio
    # Verify alignment within ±1 second
    ...
```

---

## Performance Considerations

| Operation | Complexity | Optimization |
|-----------|------------|--------------|
| Frame-to-transcript search | O(n) | Pre-sort segments by time |
| Transcript-to-frame search | O(m) | Binary search on sorted frame times |
| Chunk-to-frame mapping | O(n*m) | Build time index once |

For a 1-hour lecture:
- ~3,600 frames at 1 FPS
- ~200-400 transcript segments
- ~120 chunks at 30s window

---

## Integration with Multimodal Index (Week 3)

```python
class MultimodalIndex:
    """Index supporting both visual and transcript search."""

    def add_video(self, video_path: str):
        """Index a video with synchronized timestamps."""
        # 1. Extract frames and compute timestamps
        frames, frame_times = extract_frames(video_path, fps=1.0)

        # 2. Extract audio and transcribe
        audio_path = extract_audio(video_path)
        segments = transcriber.transcribe(audio_path)

        # 3. Chunk transcript with alignment
        chunks = chunker.chunk(segments)

        # 4. Add to index with synchronized timestamps
        for i, (frame, t) in enumerate(zip(frames, frame_times)):
            emb = visual_encoder.encode(frame)
            self._add_entry("frame", t, emb, frame_index=i)

        for chunk in chunks:
            emb = text_encoder.encode(chunk.text)
            t = (chunk.start + chunk.end) / 2  # Center timestamp
            self._add_entry("transcript", t, emb, text=chunk.text)
```

---

## Summary

| Aspect | Decision |
|--------|----------|
| Time base | Seconds from video start |
| Frame→Audio tolerance | ±1.0s |
| Audio→Frame tolerance | ±0.5s |
| Chunk window | 30s |
| Chunk overlap | 5s |
| Edge case handling | Offset detection, VFR conversion |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-01 | Initial strategy document |

---

*"Synchronization is the bridge between seeing and hearing."*
