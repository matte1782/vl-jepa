# HOSTILE_REVIEWER: Week 9 Plan Review

**Date:** 2026-01-09  
**Artifact:** docs/planning/WEEK9_PLAN.md  
**Type:** Plan  
**Author:** Human  
**Reviewer:** HOSTILE_REVIEWER Agent v1.0.0

---

## VERDICT

```
+-------------------------------------------------------------+
|   HOSTILE_REVIEWER: NEEDS REVISION                          |
|                                                             |
|   Critical Issues: 2                                        |
|   Major Issues: 5                                           |
|   Minor Issues: 3                                           |
|                                                             |
|   Disposition: Fix C1-C2, M1-M5 before execution            |
+-------------------------------------------------------------+
```

---

## Executive Summary

The Week 9 plan is **ambitious but under-constrained**. The time estimates are optimistic, several key dependencies are unaddressed, and quality gates lack measurable thresholds. The plan assumes ideal conditions that rarely exist in practice.

**Recommendation:** Revise the plan to address critical gaps before starting Day 1.

---

## Critical Issues (BLOCKING)

### [C1] Missing PyPI Upload Verification (Confidence: 95%)

**Location:** WEEK9_PLAN.md - Day 5, Post-Release Verification

**Issue:**
The plan includes pip install lecture-mind==0.3.0 as a verification step, but:
1. PyPI package name lecture-mind has never been verified as available
2. No PyPI account or API token setup is mentioned
3. No TestPyPI dry-run is planned before real release
4. pyproject.toml shows version 0.2.0 - bump is not in any day deliverables

**Evidence:**
- pyproject.toml:6 shows version = "0.2.0"
- No mention of twine, keyring, or PyPI credentials in plan
- Post-release verification assumes successful PyPI upload

**Impact:** Release may fail silently or get stuck at final step, wasting all prior effort.

**Suggested Fix:**
1. Add TestPyPI dry-run to Day 4 (before Day 5 release)
2. Verify PyPI account and credentials exist
3. Add explicit version bump step to Day 5 with verification
4. Add fallback: release is valid even if PyPI upload fails (GitHub release is primary)

---

### [C2] MkDocs Not Installed, No Dependency Check (Confidence: 98%)

**Location:** WEEK9_PLAN.md - Day 2: MkDocs Framework

**Issue:**
The plan assumes MkDocs and mkdocs-material are available, but:
1. Neither package is installed: pip show mkdocs mkdocs-material returns Package(s) not found
2. Neither package is in pyproject.toml dependencies
3. No pip install step in Day 2 deliverables
4. No docs extras group exists

**Evidence:**
pip show mkdocs mkdocs-material returns WARNING: Package(s) not found: mkdocs, mkdocs-material

**Impact:** Day 2 will fail immediately when mkdocs serve is attempted.

**Suggested Fix:**
Add to pyproject.toml under [project.optional-dependencies]:
docs = ["mkdocs>=1.5.0", "mkdocs-material>=9.0.0"]

Add to Day 2 tasks: pip install -e ".[docs]" before any MkDocs commands.


---

## Major Issues (MUST FIX)

### [M1] Day 1 Quality Criteria Unmeasurable (Confidence: 90%)

**Location:** WEEK9_PLAN.md - Day 1: Quality Criteria

**Issue:**
Quality criteria are subjective:
- Student can follow guide in <10 minutes - No test subject defined, no timing mechanism
- Verified on clean machine (or CI) - No CI workflow for docs exists, parenthetical is cop-out
- Screenshots included for key steps - How many? Which steps are key?

**Evidence:**
There is no CI workflow for docs testing. Only ci.yml exists with no docs validation.

**Impact:** Quality criteria cannot be objectively verified at Day 1 completion.

**Suggested Fix:**
1. Replace clean machine with GitHub Actions Ubuntu runner test (concrete)
2. Define exactly 3-5 key steps requiring screenshots (enumerated)
3. Add <10 minutes heuristic: if word count > 500 or step count > 15, fails

---

### [M2] GitHub Pages Setup Undocumented (Confidence: 85%)

**Location:** WEEK9_PLAN.md - Day 2: MkDocs Framework

**Issue:**
Plan lists GitHub Pages deployment as a Day 2 deliverable but provides no details on:
1. GitHub repo settings changes required (Pages source: gh-pages branch)
2. First-time Pages setup requires repository admin access
3. Custom domain configuration (if any)
4. DNS propagation time (can take 24-48 hours)

**Evidence:**
- mkdocs.yml example shows site_url: https://matte1782.github.io/lecture-mind
- No setup steps for GitHub repository settings

**Impact:** GitHub Pages deployment succeeds quality criteria may not be achievable in 4 hours if setup issues occur.

**Suggested Fix:**
Add explicit steps:
1. Go to repo Settings > Pages
2. Set source to Deploy from a branch > gh-pages
3. Run mkdocs gh-deploy --force
4. Verify at URL (may take 10-15 minutes)

---

### [M3] API Documentation Scope Unclear (Confidence: 88%)

**Location:** WEEK9_PLAN.md - Day 3 and Day 4

**Issue:**
Day 3 allocates 4 hours for API Documentation Part 1 and Day 4 allocates 2 hours for Complete API Docs. But:
1. No enumeration of how many endpoints exist
2. No mention of auto-generating from docstrings (OpenAPI/Swagger already exists via FastAPI)
3. Duplicated effort: FastAPI already generates /docs and /redoc automatically

**Evidence:**
The API already has built-in documentation:
- src/vl_jepa/api/main.py uses FastAPI with Pydantic models
- FastAPI auto-generates OpenAPI spec at /openapi.json
- Swagger UI at /docs, ReDoc at /redoc

**Impact:** 6 hours may be wasted manually documenting what FastAPI auto-documents.

**Suggested Fix:**
1. Day 3 should focus on exporting FastAPI auto-docs to MkDocs format
2. Use mkdocs-swagger-ui-tag or embed OpenAPI spec
3. Manual docs only for usage examples and tutorials, not endpoint reference
4. Reduces effort to 3 hours total

---

### [M4] Demo Recording Tool Availability (Confidence: 75%)

**Location:** WEEK9_PLAN.md - Day 4: Demo Recording

**Issue:**
Plan specifies:
- ScreenToGif (Windows) - Requires download and installation
- gifsicle for optimization - Not commonly installed on Windows

No verification that tools are installed or steps to install them.

**Evidence:**
These are third-party tools, not part of the development environment.

**Impact:** 30-60 minutes may be lost to tool installation and troubleshooting.

**Suggested Fix:**
1. Add prerequisite check at Day 4 start
2. Alternative: use browser-based tools (e.g., CloudConvert, GIPHY Capture)
3. Fallback: short video (MP4) instead of GIF, convert later

---

### [M5] Week 8 Blockers Not Addressed (Confidence: 92%)

**Location:** WEEK9_PLAN.md - Overview (implicit)

**Issue:**
Week 9 plan assumes Week 8 is complete, but ROADMAP.md shows:
- Security fixes C1-C4: Listed as Pending in task table (line 69)
- Hostile review gate: Listed as Pending (line 70)
- docker-compose polish: Listed as Pending (line 71)
- Test coverage: 74% (target 80%) - line 47

**Evidence:**
docs/ROADMAP.md:46-47 shows G6 Security C1-C4 as Pending and G7 Test coverage at 74% current.

However, docs/reviews/REVIEW_hostile_final.md shows security issues ARE fixed as of 2026-01-09.

**Impact:** ROADMAP.md is stale. Creates confusion about actual project state.

**Suggested Fix:**
1. Update ROADMAP.md to reflect actual Week 8 completion before starting Week 9
2. Close out G6 as complete (per hostile review)
3. Accept G7 at 74% or add test coverage improvement to Week 9

---

## Minor Issues (SHOULD FIX)

### [m1] Inconsistent Directory Structure (Confidence: 70%)

**Location:** WEEK9_PLAN.md - Day 2: Directory structure

**Issue:**
Plan shows docs/mkdocs/ subdirectory for MkDocs content, but current project uses docs/ at root level (where ROADMAP.md, SPECIFICATION.md, etc. live).

This creates two documentation systems:
1. docs/*.md - Project documentation (current)
2. docs/mkdocs/*.md - MkDocs site (proposed)

**Suggested Fix:**
Either:
1. Use docs/ directly as MkDocs source (set docs_dir: docs in mkdocs.yml)
2. Move all docs to new structure in one migration

---

### [m2] No Rollback Plan for Release (Confidence: 65%)

**Location:** WEEK9_PLAN.md - Day 5

**Issue:**
No mention of what to do if:
1. GitHub release has errors and needs to be deleted/re-created
2. Documentation site has broken links discovered post-deploy
3. PyPI upload fails or package is broken

**Suggested Fix:**
Add Release Rollback section:
- GitHub releases can be deleted and re-created
- MkDocs can be re-deployed with mkdocs gh-deploy --force
- PyPI yanking is a last resort (document the command)

---

### [m3] CHANGELOG Format Inconsistent (Confidence: 60%)

**Location:** WEEK9_PLAN.md - Day 5: CHANGELOG.md

**Issue:**
The CHANGELOG.md template does not match Keep a Changelog format standard:
- Missing [Unreleased] section header
- Missing comparison links at bottom
- Date placeholder format inconsistent

**Suggested Fix:**
Follow https://keepachangelog.com/en/1.0.0/ exactly, including comparison links.

---

## Feasibility Assessment

| Day | Planned Hours | Realistic Hours | Risk |
|-----|---------------|-----------------|------|
| Day 1 | 4h | 4-5h | LOW - Documentation is well-scoped |
| Day 2 | 4h | 5-6h | MEDIUM - MkDocs setup + GH Pages first-time |
| Day 3 | 4h | 2-3h | LOW - FastAPI already has docs (over-estimated) |
| Day 4 | 4h | 4-5h | MEDIUM - Tool installation + GIF creation |
| Day 5 | 4h | 5-6h | HIGH - Release coordination + verification |

**Total:** 20h planned, 20-25h realistic

**Assessment:** The plan is executable but has ~25% schedule risk. Days 2 and 5 are most likely to overrun.

---

## Dependencies Not Addressed

1. **PyPI credentials** - Required for release
2. **GitHub Pages enabled** - Required for docs site
3. **MkDocs installed** - Required for Day 2
4. **Screen recording tools** - Required for Day 4
5. **Test coverage at 80%** - Still at 74%, not addressed

---

## Recommendations Summary

### Before Starting Week 9:
1. Fix C1: Set up TestPyPI dry-run, verify PyPI credentials
2. Fix C2: Add mkdocs to pyproject.toml[docs], install locally
3. Update ROADMAP.md to reflect Week 8 completion

### During Week 9:
1. Day 2: Budget extra hour for GitHub Pages setup
2. Day 3: Leverage FastAPI auto-docs, reduce scope
3. Day 4: Pre-install screen recording tools
4. Day 5: Have fallback for PyPI issues (GitHub-only release)

### Quality Gates:
1. Add measurable criteria (word counts, step counts)
2. Add CI workflow for MkDocs build verification

---

## Conclusion

The Week 9 plan demonstrates good structure and reasonable scope. However, it contains **2 critical blockers** (MkDocs not installed, PyPI verification missing) that will cause immediate failure if not addressed. The major issues relate to unmeasurable quality criteria and unclear dependencies.

**Revise the plan to address C1-C2 before proceeding.**

---

*HOSTILE_REVIEWER - Trust nothing. Verify everything.*
