# DECISIONS

> Key architectural and technical decisions for VL-JEPA Lecture Summarizer
> Framework: FORTRESS 4.1.1

---

## Decision Log

### DEC-001: Use V-JEPA encoder instead of full VL-JEPA
**Date**: 2024-12-30
**Status**: Accepted
**Context**: Official VL-JEPA weights not yet available
**Decision**: Use V-JEPA visual encoder + separate text encoder to approximate VL-JEPA behavior
**Rationale**: Allows development to proceed while waiting for official weights
**Trade-offs**: May have slightly different embedding space than full VL-JEPA

### DEC-002: Local-first deployment
**Date**: 2024-12-30
**Status**: Accepted
**Context**: Privacy concerns with lecture recordings
**Decision**: Process all video locally, no cloud upload required
**Rationale**: Students and institutions need control over sensitive lecture content
**Trade-offs**: Requires sufficient local compute (GPU recommended)

### DEC-003: Event detection via embedding change rate
**Date**: 2024-12-30
**Status**: Accepted
**Context**: Need to detect topic changes without full transcription
**Decision**: Monitor cosine distance between consecutive embeddings, trigger on threshold
**Rationale**: Computationally cheap, works in latent space
**Trade-offs**: May miss subtle topic changes, requires threshold tuning

### DEC-004: FAISS for embedding storage
**Date**: 2024-12-30
**Status**: Accepted
**Context**: Need fast similarity search for query retrieval
**Decision**: Use FAISS with IVF index for scalable search
**Rationale**: Battle-tested, supports GPU acceleration, good for 100k+ vectors
**Trade-offs**: Additional dependency, index rebuild on updates

### DEC-005: Gradio for demo UI
**Date**: 2024-12-30
**Status**: Accepted
**Context**: Need simple web interface for demonstration
**Decision**: Use Gradio for rapid UI development
**Rationale**: Python-native, easy to deploy, good for ML demos
**Trade-offs**: Limited customization compared to full web framework

---

## How to Add Decisions

```markdown
### DEC-XXX: [Title]
**Date**: YYYY-MM-DD
**Status**: Proposed / Accepted / Deprecated / Superseded
**Context**: [Why this decision was needed]
**Decision**: [What was decided]
**Rationale**: [Why this option was chosen]
**Trade-offs**: [What we gave up]
```

---

*Document decisions as they're made. Future you will thank you.*
