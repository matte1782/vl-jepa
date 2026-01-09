# Lecture Mind

Event-aware lecture summarizer using V-JEPA visual encoder for real-time, context-aware summaries and retrieval.

## Try It Now

| Option | Description | Link |
|--------|-------------|------|
| **Cloud Demo** | Try instantly in your browser | [lecture-mind.onrender.com](https://lecture-mind.onrender.com) |
| **Local Setup** | Full features on your machine | [Local Setup Guide](local-setup.md) |

!!! note "Demo Mode"
    The cloud demo runs with placeholder processing. For full AI functionality, use the local installation.

## Features

- **Visual Encoding**: DINOv2 ViT-L/16 for 768-dim frame embeddings
- **Text Encoding**: sentence-transformers (all-MiniLM-L6-v2) for query embeddings
- **Audio Transcription**: Whisper integration for lecture transcription
- **Multimodal Search**: Combined visual + transcript ranking
- **Event Detection**: Automatic slide transition and scene change detection
- **FAISS Index**: Fast similarity search with IVF optimization

## Architecture Overview

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
            │VisualEncoder│            │EventDetector│            │ Transcriber │
            │  (DINOv2)   │            │             │            │  (Whisper)  │
            └─────────────┘            └─────────────┘            └─────────────┘
                    │                          │                          │
                    └──────────────────────────┼──────────────────────────┘
                                               ▼
                                    ┌─────────────────┐
                                    │ MultimodalIndex │
                                    │     (FAISS)     │
                                    └─────────────────┘
```

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Query latency (1k vectors) | <100ms | 30.6µs |
| Search latency (100k vectors) | <100ms | 106.4µs |
| Frame embedding (placeholder) | <50ms | 0.36ms |
| Event detection | <10ms | 0.24ms |

## Quick Links

- [Quick Start Guide](quickstart.md) - Get started in 5 minutes
- [Local Setup](local-setup.md) - Full installation guide
- [API Reference](guide/api.md) - REST API documentation
- [Architecture](ARCHITECTURE.md) - System design details

## License

MIT License - see [LICENSE](https://github.com/matte1782/lecture-mind/blob/master/LICENSE) for details.
