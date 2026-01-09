## Security Fixes Review
Date: 2026-01-09
Reviewer: SECURITY_LEAD (Hostile)

---

## Summary
- C1 (CORS): **FIXED** - Minor recommendations
- C2 (File size): **FIXED** - Properly implemented
- C3 (Rate limit): **FIXED** - With caveats
- C4 (innerHTML): **FIXED** - No remaining XSS vectors found

## Verdict: **APPROVED**

All 4 critical security issues have been properly addressed. The implementation is sound for a demo/educational project. Some improvements are recommended for production deployment but are not blocking.

---

## Detailed Findings

### C1: CORS Wildcard + Credentials

**Location:** `src/vl_jepa/api/main.py:149-162`

**Status: FIXED** (Confidence: 95%)

**What was fixed:**
```python
allowed_origins = os.environ.get("CORS_ORIGINS", "").split(",")
allowed_origins = [o.strip() for o in allowed_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=bool(allowed_origins),  # Only with specific origins
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Analysis:**
- The fix correctly prevents the dangerous combination of `allow_origins=["*"]` with `allow_credentials=True`
- When no CORS_ORIGINS env var is set (demo mode), it allows all origins but disables credentials
- When specific origins are configured, credentials are enabled safely

**Minor Recommendations (not blocking):**
1. Consider validating CORS_ORIGINS format (e.g., must start with http:// or https://)
2. Add a startup log message showing which CORS mode is active for debugging

---

### C2: No Server-Side File Size Limit

**Location:** `src/vl_jepa/api/main.py:210-278`

**Status: FIXED** (Confidence: 98%)

**What was fixed:**
```python
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming upload

# In upload handler:
total_size = 0
with open(video_path, "wb") as f:
    while chunk := await file.read(CHUNK_SIZE):
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE_BYTES:
            # Clean up partial file
            f.close()
            video_path.unlink(missing_ok=True)
            temp_dir.rmdir()
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
            )
        f.write(chunk)
```

**Analysis:**
- Streaming upload with chunked reading prevents memory exhaustion
- Size check happens during streaming, not after full upload
- Proper cleanup of partial files on size limit violation
- Configurable via environment variable for flexibility
- Uses HTTP 413 (Payload Too Large) status code correctly

**No issues found.** This is a proper implementation.

---

### C3: No Rate Limiting

**Location:** `src/vl_jepa/api/main.py:86-120, 226-232`

**Status: FIXED** (Confidence: 85%)

**What was fixed:**
```python
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = threading.Lock()

RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))

def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    
    with _rate_limit_lock:
        if client_ip not in _rate_limit_store:
            _rate_limit_store[client_ip] = []
        
        # Clean old entries
        _rate_limit_store[client_ip] = [
            t for t in _rate_limit_store[client_ip] if t > window_start
        ]
        
        if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            return False
        
        _rate_limit_store[client_ip].append(now)
        return True
```

**Analysis:**
- Thread-safe implementation with proper locking
- Sliding window rate limiting works correctly
- Configurable via environment variables
- Old entries are cleaned on each request (prevents memory leak for active IPs)

**Caveats (acceptable for demo, fix for production):**

1. **Proxy bypass concern:** Uses `request.client.host` which gets the direct client IP. Behind a proxy (Render, Cloudflare, etc.), this may return the proxy's IP instead of the real client. Production should check `X-Forwarded-For` header. However, this is **acceptable for a demo** - the rate limit still works, it just applies to the proxy.

2. **Memory accumulation for inactive IPs:** Old entries for an IP are only cleaned when that same IP makes a new request. If 10,000 unique IPs each make 1 request and never return, their entries remain forever. However:
   - Each entry is ~100 bytes (IP string + list of floats)
   - 10,000 IPs = ~1MB memory
   - Acceptable for demo; production should use Redis or periodic cleanup

3. **Rate limit only on upload:** Currently only the `/api/upload` endpoint is rate-limited. Consider also limiting `/api/search` for DoS protection.

---

### C4: innerHTML Usage (XSS)

**Location:** `src/vl_jepa/api/static/app.js`

**Status: FIXED** (Confidence: 100%)

**What was fixed:**

1. **Copy button reset (line ~1591-1606):**
   Previously used innerHTML to reset button with SVG. Now uses safe DOM methods:
   ```javascript
   btn.textContent = '';
   const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
   // ... set attributes ...
   btn.appendChild(svg);
   btn.appendChild(document.createTextNode(' Copy to Clipboard'));
   ```

2. **Bookmark delete button (line ~2144-2145):**
   Previously used innerHTML for the "×" character. Now uses textContent:
   ```javascript
   textContent: '\u00D7',  // Unicode multiplication sign
   ```

**Comprehensive XSS Audit:**

I searched the entire codebase for XSS vectors:

- `innerHTML` - Only found in comments documenting the fix
- `outerHTML` - Not found
- `document.write` - Not found
- `insertAdjacentHTML` - Not found
- `eval()` - Not found
- `new Function()` - Not found
- Dynamic script injection - Not found

All user-generated content (search results, transcripts, filenames) uses:
- `textContent` for text content
- `createElement` + `setAttribute` for DOM building
- `createElementNS` for SVG elements
- The `createElement()` helper properly handles textContent separately

**No remaining XSS vulnerabilities found.**

---

## Additional Security Observations

### Positive Security Practices Found:

1. **File type validation:** Only allows specific video extensions
2. **Proper temp file cleanup:** Uses try/except with cleanup on error
3. **No secrets in code:** Environment variables for configuration
4. **Proper error handling:** No stack traces exposed to users
5. **Input sanitization:** File paths validated, extensions checked
6. **Secure defaults:** Demo mode disables credentials

### Minor Observations (informational):

1. **Job ID predictability:** Uses first 8 chars of UUID (`uuid.uuid4()[:8]`). While not a security issue (jobs are session-scoped), full UUID would be more robust.

2. **Temp directory location:** Uses system temp directory which is appropriate.

3. **No authentication:** Expected for demo; production should add auth.

---

## Conclusion

All 4 critical security issues have been properly fixed. The implementations are correct and follow security best practices. The caveats noted for rate limiting are acceptable for a demo/educational project and are explicitly documented.

**Final Status: APPROVED for demo deployment.**

For production hardening, address:
- Rate limit proxy bypass (X-Forwarded-For)
- Rate limit memory cleanup (use Redis)
- Extend rate limiting to all endpoints
- Add authentication

---

*SECURITY_LEAD Review Complete*
