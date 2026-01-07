# Lecture Mind

[![CI](https://github.com/matte1782/lecture-mind/actions/workflows/ci.yml/badge.svg)](https://github.com/matte1782/lecture-mind/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-74%25-green.svg)](https://github.com/matte1782/lecture-mind)

Event-aware lecture summarizer using V-JEPA visual encoder for real-time, context-aware summaries and retrieval.

## Features

- **Visual Encoding**: DINOv2 ViT-L/16 for 768-dim frame embeddings
- **Text Encoding**: sentence-transformers (all-MiniLM-L6-v2) for query embeddings
- **Audio Transcription**: Whisper integration for lecture transcription
- **Multimodal Search**: Combined visual + transcript ranking with configurable weights
- **Event Detection**: Automatic slide transition and scene change detection
- **FAISS Index**: Fast similarity search with IVF optimization for large collections

## Installation

### Basic Installation (CPU)

```bash
pip install lecture-mind
```

### With ML Dependencies (GPU recommended)

```bash
pip install lecture-mind[ml]
```

### With Audio Transcription

```bash
pip install lecture-mind[audio]
```

### Full Installation

```bash
pip install lecture-mind[all]
```

### Development Installation

```bash
git clone https://github.com/matte1782/lecture-mind.git
cd lecture-mind
pip install -e ".[dev,ml,audio]"
```

## Quick Start

### CLI Usage

```bash
# Process a lecture video
lecture-mind process lecture.mp4 --output data/

# Query the processed lecture
lecture-mind query data/ "What is gradient descent?"

# List detected events
lecture-mind events data/

# Get help
lecture-mind --help
```

### Python API

```python
from vl_jepa import (
    VideoInput,
    FrameSampler,
    VisualEncoder,
    TextEncoder,
    MultimodalIndex,
    EventDetector,
)

# Load and sample video frames
with VideoInput.from_file("lecture.mp4") as video:
    sampler = FrameSampler(fps=1.0)
    frames = sampler.sample(video)

# Encode frames (uses placeholder encoder by default)
encoder = VisualEncoder.load()
embeddings = encoder.encode_batch(frames)

# Build searchable index
index = MultimodalIndex()
index.add_visual(embeddings, timestamps=[f.timestamp for f in frames])

# Query the lecture
text_encoder = TextEncoder.load()
query_emb = text_encoder.encode("machine learning basics")
results = index.search(query_emb, k=5)

for result in results:
    print(f"Timestamp: {result.timestamp:.1f}s, Score: {result.score:.3f}")
```

## Architecture

```
lecture.mp4
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ VideoInput  │────▶│FrameSampler│────▶│   Frames    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    ▼                          ▼                          ▼
            ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
            │VisualEncoder│            │EventDetector│            │AudioExtract │
            │  (DINOv2)   │            │             │            │  (FFmpeg)   │
            └─────────────┘            └─────────────┘            └─────────────┘
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
            │  Embeddings │            │   Events    │            │ Transcriber │
            │  (768-dim)  │            │             │            │  (Whisper)  │
            └─────────────┘            └─────────────┘            └─────────────┘
                    │                          │                          │
                    └──────────────────────────┼──────────────────────────┘
                                               ▼
                                    ┌─────────────────┐
                                    │ MultimodalIndex │
                                    │     (FAISS)     │
                                    └─────────────────┘
                                               │
                                               ▼
                                    ┌─────────────────┐
                                    │  Search/Query   │
                                    └─────────────────┘
```

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Query latency (1k vectors) | <100ms | 30.6µs |
| Search latency (100k vectors) | <100ms | 106.4µs |
| Frame embedding (placeholder) | <50ms | 0.36ms |
| Event detection | <10ms | 0.24ms |

See [BENCHMARKS.md](docs/BENCHMARKS.md) for detailed performance analysis.

## Requirements

- Python 3.10+
- NumPy >= 1.24.0
- OpenCV >= 4.8.0

### Optional Dependencies

- **ML**: PyTorch >= 2.0, transformers, sentence-transformers, FAISS
- **Audio**: faster-whisper >= 1.0.0
- **UI** (v0.3.0): Gradio >= 4.0.0

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/vl_jepa --cov-report=term

# Lint and format
ruff check src/ && ruff format src/

# Type check
mypy src/ --strict

# Run benchmarks
pytest tests/benchmarks/ -v --benchmark-only
```

## Roadmap

- [x] **v0.1.0**: Foundation (placeholder encoders, basic pipeline)
- [x] **v0.2.0**: Real Models + Audio (DINOv2, Whisper, multimodal search)
- [ ] **v0.3.0**: User Experience (Gradio web UI, Docker)
- [ ] **v1.0.0**: Production (optimization, real decoder, deployment)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use Lecture Mind in your research, please cite:

```bibtex
@software{lecture_mind,
  title = {Lecture Mind: Event-aware Lecture Summarizer},
  author = {Matteo Panzeri},
  year = {2026},
  url = {https://github.com/matte1782/lecture-mind}
}
```
