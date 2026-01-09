# Week 10 Unified Plan Re-Review

**Date:** 2026-01-09
**Reviewer:** HOSTILE_REVIEWER
**Artifact:** docs/planning/WEEK10_UNIFIED_PLAN.md
**Previous Review:** docs/reviews/REVIEW_week10_plans.md

---

## Previous Issues Status

| Issue | Status | Evidence | Notes |
|-------|--------|----------|-------|
| C1 | RESOLVED | Lines 22-38 | Week 10A (Storage, 20h) + Week 10B (Design, 20h) = 40h total across 2 weeks |
| C2 | RESOLVED | Lines 458-474 | Canonical file structure uses flat -v2 suffix for CSS, storage/ subdirectory for JS |
| C3 | RESOLVED | Lines 67-81 | All 10 stores explicitly defined with keyPath and indexes |
| C4 | RESOLVED | Lines 50-53 | Day 1 Prerequisites: fake-indexeddb, Jest configuration, test script |
| C5 | RESOLVED | Lines 17, 25-38 | 40h total (20h/week x 2 weeks) matches actual scope |
| C6 | RESOLVED | Lines 385-409, 442-443 | Week 10B Day 5 includes Storage Integration + CSS-to-storage mapping |

---

## Critical Issues Verification Details

### C1: Timeline Conflict (40h vs 20h)
**Claim:** Fixed via Week 10A + 10B split

**Verification:**
Week 10A - Storage Foundation - 20h - 5 days (4h/day)
Week 10B - Design System - 20h - 5 days (4h/day)
Total: 40h across 10 days

**Verdict:** RESOLVED. The math checks out. 40h of work now has 40h of budget.

---

### C2: File Structure Mismatch
**Claim:** Fixed via flat structure

**Verdict:** RESOLVED. Single canonical structure. No conflicts.

---

### C3: Schema Mismatch (4 vs 10 stores)
**Claim:** Fixed via 10 stores
**Verdict:** RESOLVED. All 10 stores defined with keyPath and indexes.

---

### C4: No JS Test Infrastructure
**Claim:** Fixed via Day 1 prerequisite
**Verdict:** RESOLVED. Test infrastructure is now a blocking prerequisite.

---

### C5: Impossible Budget
**Claim:** Fixed via 40h total
**Verdict:** RESOLVED. Budget is realistic.

---

### C6: No Integration Plan
**Claim:** Fixed via Week 10B Day 5
**Verdict:** RESOLVED. Integration is explicitly planned with time allocation.

---

## New Issues Found

### N1: Major - SM-2 Algorithm Duplication Risk Remains
**Location:** Lines 170-191
**Issue:** SM-2 implementation is defined in the unified plan, but the original WEEK10_STORAGE_PLAN.md also has SM-2 code. If both documents are referenced during implementation, divergence risk exists.
**Impact:** Medium. Could cause inconsistent flashcard scheduling.
**Mitigation:** Mark unified plan as CANONICAL SOURCE. Archive or mark other plans as SUPERSEDED.
**Severity:** MAJOR

---

### N2: Minor - Test File Location Inconsistency
**Location:** Lines 65, 103, 154
**Issue:** Test files are placed alongside source files but Week 10 Plan referenced tests/js/storage/db.test.js. Mixed convention.
**Severity:** MINOR

---

### N3: Minor - Missing npm Package Verification
**Location:** Lines 50-53
**Issue:** Prerequisites say Install fake-indexeddb but no package.json exists in the project.
**Severity:** MINOR

---

### N4: Minor - Acceptance Criteria Not Machine-Verifiable
**Location:** Lines 83-88, 133-138
**Issue:** Acceptance criteria are manual checks. No automated verification commands provided.
**Severity:** MINOR

---

### N5: Minor - Dark Mode Testing Not Automated
**Location:** Lines 310-314, 367-380
**Issue:** Week 10B acceptance criteria include dark mode verification but no automated test approach.
**Severity:** MINOR

---

### N6: Major - Safari Browser Compatibility Untestable
**Location:** Lines 449-454 (Risk table)
**Issue:** Plan mentions Safari compatibility risk but project is running on Windows. No Safari testing infrastructure available.
**Impact:** Medium. Safari IndexedDB bugs could go undetected.
**Mitigation:** Defer Safari testing OR use BrowserStack. Be explicit about which browsers are ACTUALLY tested vs deferred.
**Severity:** MAJOR

---

### N7: Minor - Offline Sync Server Endpoints Still Missing
**Location:** Lines 231
**Issue:** Plan correctly notes Server endpoints are NOT implemented yet but does not specify when they will be implemented.
**Severity:** MINOR

---

### N8: Minor - Quality Gate Checklist Duplicated
**Location:** Lines 414-433
**Issue:** Quality gate checklist appears multiple times with some overlap.
**Severity:** MINOR (Informational)

---

## Cross-Reference Verification

| Document | Status |
|----------|--------|
| WEEK10_PLAN.md | SUPERSEDED by UNIFIED |
| WEEK10_STORAGE_PLAN.md | SUPERSEDED by UNIFIED |
| WEEK10_DESIGN_PLAN.md | SUPERSEDED by UNIFIED |
| WEEK10_UNIFIED_PLAN.md | CANONICAL |

**Note:** The superseded documents should be marked as such or moved to an archive directory to prevent confusion.

---

## Risk Assessment Update

| Risk | Original Concern | Unified Plan Response | Verdict |
|------|------------------|----------------------|---------|
| Schedule overrun | 40h in 20h | Split to 2 weeks | Mitigated |
| File conflict | Multiple structures | Single canonical | Mitigated |
| Schema conflict | 4 vs 10 stores | 10 stores canonical | Mitigated |
| Test infrastructure | None defined | Day 1 prerequisite | Mitigated |
| Integration gap | CSS/JS disconnect | Day 5 integration | Mitigated |

New risks identified:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Document divergence | Medium | Low | Mark superseded docs |
| Safari bugs | Medium | Medium | Defer with acknowledgment |
| No automated CSS tests | Low | Low | Manual acceptable |

---

## Verdict

```
+--------------------------------------------------+
|   HOSTILE_REVIEWER: APPROVED                     |
|                                                  |
|   Critical Issues: 0 (6 resolved from previous)  |
|   Major Issues: 2 (new: N1, N6)                  |
|   Minor Issues: 6 (new: N2-N5, N7-N8)            |
|                                                  |
|   Disposition: PROCEED WITH CONDITIONS           |
+--------------------------------------------------+
```

---

## Conditions for Approval

The unified plan is APPROVED for execution with the following conditions:

### Must Do Before Execution Starts:

1. Mark superseded documents - Add header to WEEK10_PLAN.md, WEEK10_STORAGE_PLAN.md, WEEK10_DESIGN_PLAN.md stating they are superseded by WEEK10_UNIFIED_PLAN.md

### Must Address During Week 10A:

2. N1 - SM-2 Single Source - When implementing SM-2 in repositories.js, use ONLY the unified plan code (lines 170-191). Do not reference other documents.

3. N6 - Safari Scope - Add explicit statement to acceptance criteria: Tested in Chrome, Firefox, Edge (Safari deferred to Week 11)

### Acceptable Deferrals:

N2-N5, N7-N8: Minor issues can be addressed during implementation or deferred to polish phase.

---

## Final Notes

The unified plan successfully addresses all 6 critical issues from the previous review. The 2-week split (Week 10A + 10B) is a pragmatic solution that maintains scope while providing realistic time allocation.

The new issues found (N1-N8) are either major issues with clear mitigations or minor issues that do not block execution. None rise to the level of stop work.

**Recommendation:** Begin Week 10A execution. Address conditions before Day 1 work starts.

---

*Review completed: 2026-01-09*
*Reviewer: HOSTILE_REVIEWER*
*Verdict: APPROVED (with conditions)*
