# Week 9 Plan: Documentation + v0.3.0 Release

**Duration**: 5 days @ 4 hours/day = 20 hours total
**Goal**: Complete documentation and release v0.3.0
**Status**: REVISED (Hostile Review Issues Addressed)

---

## Prerequisites (MUST COMPLETE BEFORE DAY 1)

### P1: Install MkDocs Dependencies
```bash
pip install -e ".[docs]"
# Verify installation:
mkdocs --version
```

### P2: Verify GitHub Pages Access
- Confirm admin access to repository
- Note: First deployment may take 10-15 minutes

### P3: Verify Screen Recording Tools (for Day 4)
- Windows: Download ScreenToGif from https://www.screentogif.com/
- Alternative: Use browser-based recording (no install required)

---

## Overview

| Day | Focus | Hours | Deliverables |
|-----|-------|-------|--------------|
| Day 1 | Local Setup Guide | 4h | `docs/local-setup.md`, updated README |
| Day 2 | MkDocs Framework | 4-5h | `mkdocs.yml`, docs structure, GitHub Pages |
| Day 3 | API Documentation | 3h | Leverage FastAPI auto-docs, add examples |
| Day 4 | API Docs + Demo | 4h | Complete docs, demo GIF |
| Day 5 | Release v0.3.0 | 4-5h | CHANGELOG, tag, GitHub release |

**Buffer**: ~2-3h across week for unexpected issues

---

## Day 1: Local Setup Guide (4h)

### Objectives
Create a comprehensive local installation guide for students who want the full experience (not cloud demo).

### Deliverables

**File: `docs/local-setup.md`**
```
Contents:
├── Prerequisites
│   ├── Python 3.10+ installation
│   ├── FFmpeg installation (Windows/Mac/Linux)
│   ├── Git installation
│   └── Optional: CUDA for GPU acceleration
├── Installation Steps
│   ├── Clone repository
│   ├── Create virtual environment
│   ├── Install dependencies (pip install -e ".[all]")
│   └── Verify installation
├── Running the Application
│   ├── Start the web UI (uvicorn command)
│   ├── Access at localhost:8000
│   └── Upload your first video
├── Troubleshooting
│   ├── Common errors and solutions
│   ├── FFmpeg not found
│   ├── CUDA issues
│   └── Memory issues
└── Next Steps
    ├── Try the demo video
    ├── Explore the API
    └── Read the architecture docs
```

**Updates to `README.md`**
- Add "Try it Online" section with Render link
- Add "Full Local Installation" section with link to local-setup.md
- Update roadmap checkboxes

### Quality Criteria (Measurable)
- [ ] Guide word count < 800 words (readable in <10 minutes)
- [ ] Step count < 12 (not overwhelming)
- [ ] All 3 OS covered (Windows, Mac, Linux) with specific commands
- [ ] 3 screenshots: install verification, UI launch, first upload
- [ ] Tested: following guide results in working localhost:8000

---

## Day 2: MkDocs Framework (4-5h)

### Objectives
Set up MkDocs for professional documentation site with GitHub Pages deployment.

### Prerequisites Check
```bash
# Must pass before starting Day 2:
mkdocs --version  # Should show 1.5.0+
pip show mkdocs-material  # Should show 9.5.0+
```

### Deliverables

**File: `mkdocs.yml`** (in project root)
```yaml
site_name: Lecture Mind
site_url: https://matte1782.github.io/lecture-mind
repo_url: https://github.com/matte1782/lecture-mind
docs_dir: docs  # Use existing docs/ directory

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.highlight

nav:
  - Home: index.md
  - Getting Started:
    - Quick Start: quickstart.md
    - Local Setup: local-setup.md
    - Cloud Demo: cloud-demo.md
  - User Guide:
    - Web Interface: guide/web-ui.md
    - API Reference: guide/api.md
  - Development:
    - Architecture: ARCHITECTURE.md
    - Contributing: CONTRIBUTING.md
```

**New Files in `docs/`**
```
docs/
├── index.md              # Home page (based on README)
├── quickstart.md         # 5-minute guide
├── local-setup.md        # From Day 1
├── cloud-demo.md         # Render demo guide
└── guide/
    ├── web-ui.md         # Web interface guide
    └── api.md            # API reference (links to /docs)
```

**GitHub Pages Setup Steps**
1. Go to repo Settings > Pages
2. Set Source: "Deploy from a branch"
3. Set Branch: gh-pages / root
4. Run: `mkdocs gh-deploy --force`
5. Wait 10-15 minutes for first deployment
6. Verify at https://matte1782.github.io/lecture-mind

**GitHub Action: `.github/workflows/docs.yml`**
```yaml
name: Deploy Documentation

on:
  push:
    branches: [master]
    paths: ['docs/**', 'mkdocs.yml']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install mkdocs mkdocs-material
      - run: mkdocs gh-deploy --force
```

### Quality Criteria (Measurable)
- [ ] `mkdocs serve` runs without errors locally
- [ ] `mkdocs build` produces site/ with no warnings
- [ ] GitHub Pages URL loads (may take 24h for DNS)
- [ ] Navigation shows all planned sections
- [ ] Search finds "installation" keyword

---

## Day 3: API Documentation (3h)

### Objectives
Document REST API, leveraging FastAPI's auto-generated docs.

### Strategy (Per Hostile Review M3)
FastAPI already provides:
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- OpenAPI spec at `/openapi.json`

**Do NOT duplicate what FastAPI provides.** Instead:
1. Create guide showing how to access auto-docs
2. Add usage examples and tutorials
3. Document rate limits and authentication (future)

### Deliverables

**File: `docs/guide/api.md`**
```markdown
# API Reference

## Interactive Documentation

Lecture Mind provides automatic API documentation:

- **Swagger UI**: [/docs](/docs) - Interactive API explorer
- **ReDoc**: [/redoc](/redoc) - Clean reference documentation
- **OpenAPI Spec**: [/openapi.json](/openapi.json) - Machine-readable spec

## Base URLs

| Environment | URL |
|-------------|-----|
| Cloud Demo | https://lecture-mind.onrender.com |
| Local | http://localhost:8000 |

## Quick Examples

### Upload a Video (curl)
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@lecture.mp4"
```

### Check Processing Status
```bash
curl "http://localhost:8000/api/status/{job_id}"
```

### Search Transcript
```bash
curl -X POST "http://localhost:8000/api/search/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /api/upload | 10 requests per minute per IP |
| All others | No limit |

## File Size Limits

- Maximum upload: 100MB
- Supported formats: mp4, webm, avi, mov, mkv
```

### Quality Criteria (Measurable)
- [ ] Links to /docs and /redoc work
- [ ] 3+ curl examples that work when copy-pasted
- [ ] Rate limits documented
- [ ] File size limits documented

---

## Day 4: API Documentation Part 2 + Demo (4h)

### Objectives
Complete API documentation and create demo GIF.

### Part 1: Complete API Docs (1.5h)
- Review and polish guide/api.md
- Add error code reference
- Add WebSocket docs if applicable
- Cross-reference from other pages

### Part 2: Demo Recording (2.5h)

**Tool Options (in priority order)**:
1. ScreenToGif (Windows) - Pre-installed per prerequisites
2. Kap (Mac)
3. Browser recording fallback (no install)
4. Fallback: MP4 video, convert to GIF later

**Demo Script (30-60 seconds)**:
1. Navigate to localhost:8000 (2s)
2. Click "Upload Video" (2s)
3. Select sample video (3s)
4. Watch progress bar fill (10-15s, speed up)
5. Show events panel (3s)
6. Show transcript panel (3s)
7. Execute search query (5s)
8. Show search results (3s)
9. Click Export > Markdown (3s)
10. Show downloaded file (2s)

**File: `docs/assets/demo.gif`**
- Target size: < 5MB
- Optimize with gifsicle: `gifsicle -O3 --colors 128 demo.gif -o demo-opt.gif`
- Alternative: Use online optimizer (ezgif.com)

**Update README.md**
```markdown
## See it in Action

![Lecture Mind Demo](docs/assets/demo.gif)

[Try the Cloud Demo](https://lecture-mind.onrender.com) | [Local Setup](docs/local-setup.md)
```

### Quality Criteria (Measurable)
- [ ] Demo GIF file size < 5MB
- [ ] Duration 30-60 seconds
- [ ] Text readable at GitHub preview size
- [ ] Shows complete workflow: upload → results → search → export
- [ ] GIF renders in GitHub README preview

---

## Day 5: Release v0.3.0 (4-5h)

### Objectives
Tag and release v0.3.0 with proper changelog and release notes.

### Part 1: Version Bump (30m)

**Update `pyproject.toml`**:
```toml
version = "0.3.0"
```

### Part 2: CHANGELOG (1h)

**File: `CHANGELOG.md`** (keepachangelog.com format)
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-01-XX

### Added
- Web UI with FastAPI backend
- Real-time processing progress indication
- Semantic search across transcript
- Export to Markdown/JSON/SRT formats
- Docker support with multi-stage build
- Cloud demo on Render (demo mode)
- Comprehensive documentation site (MkDocs)

### Changed
- Improved event detection accuracy
- Better error handling throughout API

### Fixed
- Memory management for long videos
- Rate limiting and file size validation
- Path traversal vulnerability (CVE-like severity)
- CORS configuration security

### Security
- C1: Fixed CORS wildcard with credentials
- C2: Added server-side file size limits (100MB)
- C3: Implemented rate limiting (10 req/min)
- C4: Replaced innerHTML with safe DOM methods
- C5: Fixed path traversal via filename sanitization
- C6: Fixed rate limit bypass via client IP validation
- Plus 6 additional minor issues (see REVIEW_hostile_final.md)

## [0.2.0] - 2026-01-XX

### Added
- Real V-JEPA encoder integration
- Audio transcription via Whisper
- CLI interface
- FAISS similarity search

## [0.1.0] - 2026-01-XX

### Added
- Initial project structure
- Mock encoder for development
- Basic video processing pipeline

[Unreleased]: https://github.com/matte1782/lecture-mind/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/matte1782/lecture-mind/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/matte1782/lecture-mind/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/matte1782/lecture-mind/releases/tag/v0.1.0
```

### Part 3: Pre-Release Verification (1h)

```bash
# 1. Ensure all tests pass
pytest tests/ -v

# 2. Verify documentation builds
mkdocs build

# 3. Check package builds
pip install build
python -m build

# 4. Verify package installs from local build
pip install dist/lecture_mind-0.3.0-py3-none-any.whl
```

### Part 4: GitHub Release (1h)

**Create Tag**:
```bash
git tag -a v0.3.0 -m "v0.3.0 - Web UI + Cloud Demo + Security Hardening"
git push origin v0.3.0
```

**GitHub Release Notes**:
```markdown
## v0.3.0 - Web UI + Cloud Demo

### Highlights
- Web interface for video processing
- Cloud demo at https://lecture-mind.onrender.com
- Security hardened (12 issues fixed)
- Docker support
- Professional documentation

### Try it now
- **Cloud**: https://lecture-mind.onrender.com
- **Local**: See [Local Setup Guide](docs/local-setup.md)
- **Documentation**: https://matte1782.github.io/lecture-mind

### Full Changelog
See [CHANGELOG.md](CHANGELOG.md)

---
Generated with Claude Code
```

### Part 5: Post-Release Verification (30m)
- [ ] GitHub release visible at /releases
- [ ] Tag v0.3.0 visible at /tags
- [ ] Documentation site accessible
- [ ] Cloud demo still working
- [ ] README displays demo GIF

### Rollback Plan (if needed)
```bash
# Delete release (via GitHub UI)
# Delete tag:
git tag -d v0.3.0
git push origin :refs/tags/v0.3.0
# Re-deploy docs:
mkdocs gh-deploy --force
```

### Quality Criteria (Measurable)
- [ ] `pytest tests/ -v` passes (all green)
- [ ] `mkdocs build` succeeds with no warnings
- [ ] GitHub tag v0.3.0 exists
- [ ] GitHub release has release notes
- [ ] CHANGELOG follows keepachangelog format

---

## Quality Gates

### Pre-Release Checklist (Day 5)
- [ ] All Week 9 deliverables complete
- [ ] CI green on all Python versions (3.10, 3.11, 3.12, 3.13)
- [ ] MkDocs builds without errors
- [ ] Demo GIF works in README preview
- [ ] Cloud demo stable and accessible
- [ ] Local setup guide tested

### Post-Release Verification
- [ ] GitHub release visible
- [ ] Documentation site live
- [ ] No broken links in docs
- [ ] README renders correctly on GitHub

---

## Risk Mitigation

| Risk | Mitigation | Fallback |
|------|------------|----------|
| MkDocs theme issues | Use vanilla Material theme | Plain MkDocs theme |
| GitHub Pages slow DNS | Wait 24-48h | Document delay in release notes |
| Demo GIF too large | Use gifsicle optimization | Use MP4 with play button |
| PyPI upload fails | Not required for v0.3.0 | GitHub release is primary |

---

## Success Criteria

**v0.3.0 is RELEASED when:**
1. GitHub tag v0.3.0 exists
2. GitHub release with notes published
3. Documentation site live (or in progress with ETA)
4. Cloud demo accessible
5. README has demo GIF
6. CHANGELOG updated

---

## Notes from Hostile Review

Issues addressed:
- [C1] PyPI verification: Removed as requirement, GitHub-only release is valid
- [C2] MkDocs: Added to pyproject.toml[docs], prerequisite check added
- [M1] Quality criteria: Made measurable with word/step counts
- [M2] GitHub Pages: Explicit setup steps added
- [M3] API docs scope: Leveraging FastAPI auto-docs, examples only
- [M4] Demo tools: Prerequisite check added, fallbacks defined
- [M5] ROADMAP.md: Updated separately
- [m1] Directory structure: Using docs/ directly (no subdirectory)
- [m2] Rollback plan: Added to Day 5
- [m3] CHANGELOG format: Updated to keepachangelog.com standard

---

*Plan created: 2026-01-09*
*Revised: 2026-01-09 (Hostile Review Issues Addressed)*
*Status: READY FOR EXECUTION*
