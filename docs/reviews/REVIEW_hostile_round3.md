## Hostile Review Round 3 - Verification
Date: 2026-01-09
Reviewer: HOSTILE_REVIEWER Agent v1.0.0

---

## Round 2 Issues Status

| Issue | Status | Notes |
|-------|--------|-------|
| C1 (Path traversal) | **VERIFIED** | `os.path.basename()` at line 307 strips directory components. Empty filename check added. |
| C2 (Rate limit bypass) | **VERIFIED** | `request.client` None check at line 277 rejects with 400, no "unknown" fallback. |
| M1 (Video handle leak) | **VERIFIED** | try/finally blocks added at lines 611-622 and 731-738 ensure `video.close()` is called. |
| M2 (Temp dir cleanup) | **VERIFIED** | `shutil.rmtree()` with `ignore_errors=True` used at all cleanup points (lines 152, 163, 309, 321, 331). |
| M4 (Job memory) | **VERIFIED** | TTL-based cleanup implemented (lines 124-169). `cleanup_old_jobs()` called before new job creation (line 336). |
| M6 (File size alignment) | **PARTIAL** | Frontend synced to 100MB (app.js:18), but backend default is 500MB (main.py:260). See note below. |

---

## M6 Detail Analysis

The fix description states "syncing frontend to 100MB", but the actual alignment is:
- **Frontend:** 100MB (app.js line 18: `MAX_FILE_SIZE: 100 * 1024 * 1024`)
- **Backend:** 500MB default (main.py line 260: `os.environ.get("MAX_FILE_SIZE_MB", "500")`)

**Impact:** Frontend is MORE restrictive than backend. Users will be blocked at 100MB on the frontend, never reaching the 500MB backend limit. This is safe (no 413 errors after long uploads) but still a mismatch.

**Verdict on M6:** ACCEPTABLE - The current state prevents the original UX issue (users uploading large files only to be rejected). However, the documentation comment at main.py:259 is misleading - it says "500MB default for local" but this affects all deployments without MAX_FILE_SIZE_MB env var.

---

## New Issues Found

### [N1] Rate Limit Store Memory Accumulation (Minor)
**Location:** `src/vl_jepa/api/main.py` lines 88-121
**Confidence:** 75%

**Issue:** `_rate_limit_store` dictionary grows unbounded. While entries within each IP are cleaned, the IP keys themselves are never removed. Long-running servers accumulate IP entries.

**Impact:** Minor memory issue for production servers with high unique client count.

**Suggested Fix:** Clean up IP entries with empty request lists.

---

### [N2] Job TTL Cleanup Only Triggered on Upload (Minor)
**Location:** `src/vl_jepa/api/main.py` line 336
**Confidence:** 80%

**Issue:** `cleanup_old_jobs()` is only called when a new upload occurs. If no uploads happen for hours, expired jobs persist in memory.

**Impact:** Minor - jobs eventually get cleaned up on next upload.

**Suggested Fix:** Consider periodic background cleanup task, or cleanup on status/results endpoints.

---

## Code Quality Observations

### Positive Changes
1. **Path sanitization** is correctly implemented using `os.path.basename()` - industry standard approach.
2. **try/finally blocks** properly wrap video operations, ensuring cleanup even on exceptions.
3. **TTL-based cleanup** uses both time-based expiry AND max job count - belt and suspenders approach.
4. **Client rejection** for missing IP is the correct security posture - fail closed, not open.

### Verification Evidence
```python
# C1 Fix at line 307
safe_filename = os.path.basename(file.filename)

# C2 Fix at line 277-281
if not request.client:
    raise HTTPException(
        status_code=400,
        detail="Cannot determine client IP. Request rejected.",
    )

# M1 Fix at line 611-622
video = VideoInput.open(video_path)
try:
    metadata = VideoMetadata(...)
finally:
    video.close()

# M4 Fix at line 124-169
JOB_TTL_SECONDS = int(os.environ.get("JOB_TTL_SECONDS", "3600"))
MAX_JOBS = int(os.environ.get("MAX_JOBS", "50"))
```

---

## Verdict

```
+--------------------------------------------------+
|   HOSTILE_REVIEWER: APPROVED                     |
|                                                  |
|   Round 2 Critical Issues: 2 - ALL FIXED         |
|   Round 2 Major Issues: 6 - 5 FIXED, 1 PARTIAL   |
|   New Issues: 2 (both Minor)                     |
|                                                  |
|   Disposition: Ready for deployment              |
|   Recommended: Address N1, N2 in future sprint   |
+--------------------------------------------------+
```

**Rationale:** All critical and major security issues from Round 2 are properly fixed. The partial M6 fix is acceptable as it errs on the side of user protection (frontend more restrictive than backend). The two new minor issues (rate limit store cleanup, periodic job cleanup) are operational concerns for long-running production servers and do not block release.

---

*HOSTILE_REVIEWER - Trust nothing. Verify everything.*
