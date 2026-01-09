# ADR-0001: IndexedDB for Client-Side Storage

**Date:** 2026-01-09
**Status:** Proposed
**Deciders:** ARCHITECT

---

## Context

v0.4.0 Student Playground requires persistent browser storage for:

1. **Multi-lecture library** - Store metadata for 100+ lectures per course
2. **Progress tracking** - Per-segment watch status, quiz scores
3. **Flashcard system** - SM-2 spaced repetition with scheduling data
4. **Offline functionality** - Full app functionality without network
5. **Confusion analytics** - Anonymous voting data for professor dashboard

### Current State

The v0.3.0 implementation uses `localStorage` for:
- Bookmarks (`lectureMind_bookmarks`)
- Confusion votes (`lectureMind_confusionVotes`)

Limitations of localStorage:
- 5-10MB quota (varies by browser)
- Synchronous API blocks main thread
- No indexing or querying
- String-only storage (JSON serialization overhead)
- No binary data support (video caching impossible)

### Requirements

| Requirement | localStorage | IndexedDB | Server-Only |
|-------------|--------------|-----------|-------------|
| Store 100+ lectures metadata | Limited | Yes | Yes |
| Store video blobs (offline) | No | Yes | No |
| Complex queries (by date, course) | No | Yes | Yes |
| Offline-first | Partial | Yes | No |
| No network latency | Yes | Yes | No |
| Async (non-blocking) | No | Yes | Yes |

---

## Options Considered

### Option A: localStorage (Current)

**Pros:**
- Already implemented for bookmarks/confusion
- Simple key-value API
- Universal browser support

**Cons:**
- 5-10MB quota insufficient for video metadata + flashcards
- Blocks main thread on read/write
- No indexing for queries like "flashcards due today"
- Cannot store video blobs for offline mode

**Why rejected:** Insufficient quota and no query support.

### Option B: IndexedDB (Vanilla)

**Pros:**
- Large quota (50MB+ guaranteed, often GB-scale)
- Async API (non-blocking)
- Indexes for efficient queries
- Supports binary data (Blobs)
- No external dependencies
- Full control over schema

**Cons:**
- Complex callback/event-based API
- More implementation effort
- Safari has historical IndexedDB bugs (mostly fixed)

### Option C: IndexedDB with Dexie.js

**Pros:**
- Promise-based wrapper over IndexedDB
- Simplified query syntax
- Well-tested library

**Cons:**
- 50KB+ bundle size increase
- Another dependency to maintain
- Less control over low-level behavior
- May not support all IndexedDB features

**Why rejected:** Bundle size and dependency management concerns.

### Option D: localForage

**Pros:**
- Simple localStorage-like API
- Falls back gracefully across browsers

**Cons:**
- Designed for key-value, not relational data
- No index support
- 15KB+ bundle size

**Why rejected:** Does not support indexed queries.

### Option E: Server-Only Storage

**Pros:**
- Simpler client code
- Centralized data management
- Easy backup/restore

**Cons:**
- Requires network for all operations
- Latency for every interaction
- No offline functionality
- Privacy concerns (all data on server)

**Why rejected:** Violates offline-first requirement and adds latency.

---

## Decision

**Use vanilla IndexedDB with a custom typed wrapper.**

Implementation approach:
1. Build a promise-based wrapper (`LectureMindDB` class)
2. Define object stores with indexes for common queries
3. Create repository classes for high-level operations
4. Implement migration system for schema versioning
5. Build offline sync queue for eventual consistency

---

## Consequences

### Positive

1. **Large storage capacity** - Can store hundreds of lectures with metadata
2. **Binary data support** - Video blobs for true offline mode
3. **Indexed queries** - Fast lookups for "due flashcards", "lectures by course"
4. **Non-blocking** - Async API keeps UI responsive
5. **No dependencies** - Zero bundle size increase from libraries
6. **Full control** - Custom migration system, optimized for our schema
7. **Privacy-first** - All data stays in browser by default

### Negative

1. **Implementation effort** - ~20h for complete storage layer (Week 10)
2. **API complexity** - IndexedDB's event-based API requires careful wrapping
3. **Testing overhead** - Need browser environment for tests (jsdom limitations)
4. **Safari quirks** - Must test thoroughly on Safari (WebKit IndexedDB bugs)

### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Safari IndexedDB bugs | Medium | High | Test on real Safari, have fallback error handling |
| Storage quota exceeded | Low | Medium | Show storage usage UI, implement LRU cleanup |
| Data corruption | Low | High | Implement backup/restore, validate on read |
| Migration failures | Low | High | Test migrations with real data, keep rollback path |
| Performance degradation | Low | Medium | Monitor with 100+ lectures, add pagination |

---

## Alternatives for Future Consideration

### OPFS (Origin Private File System)

Emerging standard for large file storage. Consider for v1.0 if video caching becomes a priority.

### SQLite via WebAssembly

sql.js provides full SQLite in browser. Consider if relational queries become complex.

### CRDTs for Sync

If multi-device sync becomes required, consider CRDT libraries (Yjs, Automerge).

---

## Implementation Plan

See `docs/planning/WEEK10_STORAGE_PLAN.md` for detailed 5-day implementation schedule.

### Schema Overview

```
Object Stores:
- courses (indexed: name, createdAt)
- lectures (indexed: courseId, createdAt, title)
- segments (indexed: lectureId, startTime)
- events (indexed: lectureId, timestamp)
- progress (composite key: lectureId + segmentId)
- flashcards (indexed: lectureId, dueDate, status)
- bookmarks (indexed: lectureId, type, timestamp)
- confusionVotes (indexed: lectureId, segmentId, synced)
- syncQueue (indexed: type, createdAt)
- settings (key-value)
```

---

## References

- [MDN IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [IndexedDB Promised](https://github.com/nicolo-ribaudo/idb) - Inspiration for wrapper API
- [Safari IndexedDB Issues](https://bugs.webkit.org/buglist.cgi?product=WebKit&component=IndexedDB)
- [SM-2 Algorithm](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | ARCHITECT | Initial decision |

---

*ADR-0001 - IndexedDB provides the foundation for offline-first Student Playground.*
