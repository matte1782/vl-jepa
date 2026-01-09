# HOSTILE_REVIEWER: Day 1 Documentation Review

**Date:** 2026-01-09
**Artifacts Reviewed:**
- `docs/local-setup.md` - Local setup guide
- `README.md` - Updated with "Try It Now" section

**Review Type:** Documentation Quality Gate

---

## Summary

| Category | Issues Found |
|----------|--------------|
| **Critical (BLOCKING)** | 1 |
| **Major (MUST FIX)** | 3 |
| **Minor (SHOULD FIX)** | 4 |

---

## Critical Issues (BLOCKING)

### [C1] CLI Help Output Inconsistency (95% confidence)

**Location:** `docs/local-setup.md:194`, `README.md:68-77`

**Issue:** Documentation references `lecture-mind` as the CLI command, which works correctly. However, the help output shows `vl-jepa` as the program name (due to `prog="vl-jepa"` in `cli.py:27`). This will confuse students when they run `lecture-mind --help` and see `usage: vl-jepa`.

**Evidence:**
```
$ lecture-mind --help
usage: vl-jepa [-h] [--verbose] {process,query,events,demo} ...
```

**Impact:** Students may think they installed incorrectly or are using the wrong command.

**Suggested Fix:** Either:
1. Change `prog="vl-jepa"` to `prog="lecture-mind"` in `cli.py:27`, OR
2. Document both commands work (aliased via pyproject.toml)

---

## Major Issues (MUST FIX)

### [M1] Missing API Dependency Clarification (85% confidence)

**Location:** `docs/local-setup.md:69-75`

**Issue:** The installation section offers `[all]` or `[api]` but running the uvicorn command requires the `api` extra. The `[api]` extra is mentioned but not clearly linked to the "Running the Web UI" section.

**Evidence:** A student installing with just `pip install -e "."` will get `ModuleNotFoundError: No module named 'uvicorn'` when trying to run the server.

**Suggested Fix:** Add explicit note before the "Running the Web UI" section:
```markdown
> **Prerequisite:** This section requires the API dependencies. 
> If you haven't already, install with: `pip install -e ".[api]"`
```

### [M2] Relative Link May Break (80% confidence)

**Location:** `docs/local-setup.md:193`

**Issue:** Link `[docs/ARCHITECTURE.md](ARCHITECTURE.md)` uses a relative path. When viewed from different contexts (GitHub root vs docs folder), the link may not resolve correctly.

**Evidence:** The file exists at `docs/ARCHITECTURE.md` but the link assumes you're already in the `docs/` folder.

**Suggested Fix:** Use explicit path: `[Architecture Documentation](./ARCHITECTURE.md)` or the full path from root: `[Architecture](../docs/ARCHITECTURE.md)`

### [M3] No Python Version Verification Command for Windows (75% confidence)

**Location:** `docs/local-setup.md:11`

**Issue:** Check command shows `python --version` but on some Windows systems, Python 3 is installed as `py` or `python3`. The document doesn't clarify this.

**Evidence:** On fresh Windows installs from Microsoft Store, the command may be `py --version`.

**Suggested Fix:** Add note:
```markdown
| Python | 3.10+ | `python --version` or `py --version` (Windows) |
```

---

## Minor Issues (SHOULD FIX)

### [m1] Inconsistent Repository Clone URL (60% confidence)

**Location:** `docs/local-setup.md:51`

**Issue:** Clone command uses `https://github.com/matte1782/lecture-mind.git` which is correct (verified), but should confirm this is the actual public repository URL.

**Verified:** Git remote shows this is the correct URL. No action needed unless repo changes.

### [m2] Missing Virtual Environment Deactivation (55% confidence)

**Location:** `docs/local-setup.md:57-65`

**Issue:** Shows how to activate virtual environment but doesn't mention how to deactivate (`deactivate` command).

**Suggested Fix:** Add after activation:
```markdown
# To exit the virtual environment later
deactivate
```

### [m3] CUDA_VISIBLE_DEVICES Incorrect for Disable (70% confidence)

**Location:** `docs/local-setup.md:134-138`

**Issue:** Using `CUDA_VISIBLE_DEVICES=-1` may not work consistently. The standard way to force CPU is empty string or specific device exclusion.

**Evidence:** PyTorch documentation recommends `CUDA_VISIBLE_DEVICES=""` or setting device in code.

**Suggested Fix:**
```bash
# Windows
set CUDA_VISIBLE_DEVICES=

# macOS/Linux
export CUDA_VISIBLE_DEVICES=""
```

### [m4] FFmpeg PATH Command May Not Persist (50% confidence)

**Location:** `docs/local-setup.md:120-121`

**Issue:** The `setx PATH "%PATH%;C:\ffmpeg\bin"` command appends to PATH but the actual ffmpeg location varies. Also `setx` requires a new terminal session.

**Suggested Fix:** Add note that user needs to open a new terminal after running setx, and verify their actual ffmpeg location.

---

## Consistency Check: README vs local-setup.md

| Aspect | README | local-setup.md | Consistent? |
|--------|--------|----------------|-------------|
| Python version | 3.10+ | 3.10+ | YES |
| Package name | lecture-mind | lecture-mind | YES |
| Installation extras | `[ml]`, `[audio]`, `[all]`, `[dev]` | `[all]`, `[api]` | PARTIAL |
| CLI command | `lecture-mind` | `lecture-mind` | YES |
| Cloud demo URL | lecture-mind.onrender.com | lecture-mind.onrender.com | YES |
| GitHub URL | matte1782/lecture-mind | matte1782/lecture-mind | YES |

**Note:** README documents more installation extras than local-setup.md, which is acceptable since local-setup focuses on the common path.

---

## Verification Results

| Test | Result |
|------|--------|
| `python -c "from vl_jepa import VideoInput; print('OK')"` | PASS |
| `lecture-mind --help` | PASS (but shows vl-jepa in usage) |
| `vl-jepa --help` | PASS |
| API module import | PASS |
| GitHub repo URL accessible | PASS (HTTP 200) |
| README imports valid | PASS |

---

## VERDICT

```
+--------------------------------------------------+
|   HOSTILE_REVIEWER: NEEDS REVISION               |
|                                                  |
|   Critical Issues: 1                             |
|   Major Issues: 3                                |
|   Minor Issues: 4                                |
|                                                  |
|   Disposition: Fix C1 and M1-M3 before approval  |
+--------------------------------------------------+
```

### Required Actions Before Approval

1. **[C1]** Fix CLI program name inconsistency - change `prog="vl-jepa"` to `prog="lecture-mind"` in `src/vl_jepa/cli.py:27`
2. **[M1]** Add prerequisite note before "Running the Web UI" section
3. **[M2]** Fix relative link to ARCHITECTURE.md
4. **[M3]** Add Windows `py` command alternative for Python version check

### Recommended Actions

- Address minor issues m2, m3, m4 for improved student experience
- Consider adding a "Common Setup Patterns" section for different use cases

---

*HOSTILE_REVIEWER: Trust nothing. Verify everything.*
*Review completed: 2026-01-09*
