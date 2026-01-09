# Week 10 Plans Review

**Date:** 2026-01-09
**Reviewer:** HOSTILE_REVIEWER
**Artifacts Reviewed:**
- docs/planning/WEEK10_PLAN.md (Master Plan)
- docs/planning/WEEK10_STORAGE_PLAN.md (Storage/Architecture)
- docs/planning/WEEK10_DESIGN_PLAN.md (Design/Frontend)

---

## Summary
- **Issues:** 6 critical, 8 major, 12 minor
- **Recommendation:** NEEDS_REVISION

The Week 10 plans are comprehensive and well-structured. However, there are significant inconsistencies between the three documents, timeline conflicts, and missing integration points that must be addressed before execution begins.

---

## Critical Issues (must fix before starting)

### C1: Conflicting Day-by-Day Task Assignments
**Location:** All three documents, Daily Breakdown sections
**Issue:** The three plans define completely different work for the same days.

The Master Plan assigns Day 1 to design and Day 2-3 to storage, while the sub-plans each claim ALL 5 days for their respective domains. This is a 40-hour plan crammed into 20 hours.

**Impact:** Execution will fail immediately. Either storage OR design will not get done, or both will be half-finished.

**Fix:** Create a unified schedule. Either:
1. Interleave tasks (AM storage, PM design)
2. Split Week 10 into Week 10A (storage) and Week 10B (design)
3. Reduce scope of one domain to 2 days

### C2: Master Plan References Non-Existent File Structure
**Location:** WEEK10_PLAN.md, lines 448-463
**Issue:** Master Plan specifies storage/db.js and animations/transitions.js but Design Plan specifies tokens-v2.css and animations-v2.css. Different approaches.
**Impact:** Developers will create conflicting file structures.
**Fix:** Align on Design Plan approach (flat structure with -v2 suffix).

### C3: Storage Schema Mismatch Between Master and Storage Plans
**Location:** WEEK10_PLAN.md lines 90-110 vs WEEK10_STORAGE_PLAN.md lines 126-138
**Issue:** Master Plan shows 4 stores; Storage Plan shows 10 stores.
**Impact:** If developer follows Master Plan, 6 stores will be missing.
**Fix:** Update Master Plan schema to match Storage Plan (10 stores).

### C4: Test Infrastructure Missing
**Location:** All plans reference tests/js/ directory
**Issue:** No plan addresses what test runner, how to run in CI, or how to mock IndexedDB.
**Impact:** Write unit tests tasks will block on undefined test setup.
**Fix:** Add Day 0 prerequisite: Set up JavaScript test infrastructure.

### C5: 20-Hour Budget is Impossible
**Location:** All three documents claim 20 hours
**Issue:** Storage Plan = 20h + Design Plan = 20h + Review = 4h = 44h total. Budget = 20h.
**Impact:** Plans will fail by Day 3.
**Fix:** Double timeline to 2 weeks OR cut scope by 50 percent.

### C6: No Integration Plan Between Storage and Design
**Location:** All three documents (missing)
**Issue:** Storage creates JS modules. Design creates CSS files. Neither addresses integration.
**Impact:** CSS and storage will not talk to each other.
**Fix:** Add integration tasks for storage-aware components.

---

## Major Issues (fix within Day 1-2)

### M1: SM-2 Algorithm Implementation Defined Twice
Both documents define SM-2. If implemented independently, may diverge.

### M2: Acceptance Criteria Not Testable
No linter rules, no automated checks for criteria.

### M3: tokens-v2.css vs tokens.css Enhancement Conflict
Master Plan expects enhanced tokens.css. Design Plan creates tokens-v2.css.

### M4: Offline Sync References Non-Existent Endpoints
SyncManager references /api/confusion, /api/lectures, /api/courses.

### M5: No localStorage Migration Verification
Migration code references localStorage keys without verification.

### M6: Animation File Conflicts
Three different animation file approaches in two documents.

### M7: Missing ESLint/Stylelint Configuration
Quality gates reference non-existent linting checks.

### M8: Browser Compatibility Untestable
Safari testing requires macOS but Windows detected.

---

## Minor Issues (nice to fix)

- m1: Inconsistent Agent Assignments
- m2: Documentation File Location Mismatch
- m3: Risk R5 --sp- Prefix Not Applied
- m4: ADR Document Referenced But Not Created
- m5: Magic Numbers in Animation Timing
- m6: Test File Naming Inconsistency
- m7: Missing Imports in Code Examples
- m8: No Error Boundary for Storage Failures
- m9: Accessibility Missing Keyboard Shortcuts
- m10: No Mobile Touch Gesture Specification
- m11: Database Version Hardcoded Multiple Places
- m12: Quality Gate Coverage Target Unclear

---

## Positive Findings

1. Comprehensive Data Model in Storage Plan
2. SM-2 Algorithm Correctness
3. Accessibility First approach
4. Reduced Motion Support
5. Migration Strategy thoughtfully planned
6. Dark Mode Coverage systematic
7. Component Pattern Library with BEM naming
8. Risk Identification realistic

---

## Verdict

HOSTILE_REVIEWER: NEEDS_REVISION

Critical Issues: 6
Major Issues: 8
Minor Issues: 12

Disposition: Cannot approve as-is. The three documents are internally
well-crafted but externally inconsistent. A unified timeline that
resolves the 40h vs 20h conflict is required before execution begins.

Recommended Action:
1. Create unified WEEK10_UNIFIED_PLAN.md
2. Resolve all Critical issues
3. Re-submit for hostile review

### Blocking Items (Must Fix Before START)
1. C1: Unified timeline (40h of work in 20h budget)
2. C2: Canonical file structure
3. C3: Authoritative schema (10 stores)
4. C4: JavaScript test infrastructure prerequisite
5. C5: Realistic hour budget
6. C6: Storage-to-design integration tasks

### Conditions for Approval
If the above 6 critical issues are addressed, plans can proceed with
Major issues being tracked as Day 1-2 tasks. Minor issues can be
deferred to Week 11 polish.

---

*Review completed: 2026-01-09*
*Reviewer: HOSTILE_REVIEWER*
*Verdict: NEEDS_REVISION*
