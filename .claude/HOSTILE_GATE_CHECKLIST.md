# HOSTILE_GATE_CHECKLIST

**Version:** 1.0.0
**Purpose:** Comprehensive quality gate criteria for HOSTILE_REVIEWER validation
**Authority:** BLOCKING — All criteria must be met for approval

---

## HOW TO USE THIS CHECKLIST

This checklist is organized by artifact type. When HOSTILE_REVIEWER evaluates an artifact, they must verify ALL applicable criteria for that type. Any failure results in REJECTION with required actions.

**Severity Levels:**
- **CRITICAL [C]** — Blocks approval immediately
- **MAJOR [M]** — Must be fixed before approval
- **MINOR [m]** — Should be fixed; may be tracked for later

---

## PART 1: ARCHITECTURE DOCUMENTS

### Completeness Criteria

**CRITICAL:**
- [ ] All core components are defined with clear responsibilities
- [ ] All data structures include size calculations (bytes)
- [ ] WASM boundary functions are completely specified
- [ ] Persistence format includes binary layout with byte offsets
- [ ] Performance budget includes P50 and P99 targets
- [ ] Memory calculations provided for 1M vector scale

**MAJOR:**
- [ ] All component interactions are documented
- [ ] All invariants are explicitly stated
- [ ] Thread safety guarantees are specified
- [ ] Error handling strategy is defined
- [ ] Graceful degradation paths are documented

**MINOR:**
- [ ] Diagrams are clear and unambiguous
- [ ] Terminology is consistent throughout
- [ ] Related work is cited where applicable

### Consistency Criteria

**CRITICAL:**
- [ ] DATA_LAYOUT.md and ARCHITECTURE.md agree on struct sizes
- [ ] Performance budget calculations match memory layout
- [ ] WASM_BOUNDARY.md functions match ARCHITECTURE.md exports
- [ ] No contradictions between documents

**MAJOR:**
- [ ] Naming conventions are consistent across documents
- [ ] Type definitions match across all specs
- [ ] Version numbers are synchronized

### Feasibility Criteria

**CRITICAL:**
- [ ] Timeline is realistic (verified against PLANNER estimates)
- [ ] Memory budget fits within WASM constraints (Safari: ~1GB)
- [ ] Performance targets are achievable (verified by similar systems)
- [ ] WASM constraints are respected (no threads without SharedArrayBuffer fallback)

**MAJOR:**
- [ ] Dependencies are available and compatible
- [ ] Browser API availability is verified (with MDN references)
- [ ] Rust crate ecosystem supports requirements

### Durability Criteria

**CRITICAL:**
- [ ] Design handles 1M vectors without collapse
- [ ] IndexedDB failure has recovery protocol
- [ ] Graceful degradation paths are defined
- [ ] Concurrent access patterns are safe

**MAJOR:**
- [ ] Performance degrades gracefully under load
- [ ] Memory pressure is handled
- [ ] Browser-specific limitations are addressed

### Anti-Hallucination Criteria

**CRITICAL:**
- [ ] No `[UNKNOWN]` items remain unaddressed
- [ ] All technical claims are tagged `[FACT]` with source or `[HYPOTHESIS]`
- [ ] No magic numbers without named constants and justification
- [ ] All size calculations include padding, metadata, and safety margin

---

## PART 2: PLANS (ROADMAP & WEEKLY_TASK_PLAN)

### Dependency Criteria

**CRITICAL:**
- [ ] Every dependency references a specific, verifiable artifact
- [ ] Blocked tasks are explicitly listed with unblock conditions
- [ ] Critical path is identified and realistic
- [ ] No circular dependencies

**MAJOR:**
- [ ] Inter-task dependencies are complete
- [ ] External dependencies (crates, APIs) are versioned
- [ ] Dependency graph is acyclic

### Estimation Criteria

**CRITICAL:**
- [ ] 3x rule applied to all optimistic estimates
- [ ] No tasks exceed 16 hours (must be decomposed)
- [ ] Timeline includes 30% contingency buffer
- [ ] Complexity multipliers are applied correctly

**MAJOR:**
- [ ] Historical velocity is considered
- [ ] Learning curve for new APIs is factored in
- [ ] Testing time is included (not just coding)

### Acceptance Criteria

**CRITICAL:**
- [ ] Every task has measurable acceptance criteria
- [ ] Every task specifies verification strategy (unit/prop/fuzz/bench)
- [ ] Every task has binary pass/fail condition
- [ ] Acceptance criteria reference specific tests or benchmarks

**MAJOR:**
- [ ] Criteria are objective, not subjective
- [ ] Success is independently verifiable
- [ ] No vague statements like "works correctly"

### Risk Criteria

**CRITICAL:**
- [ ] All HIGH and MEDIUM risks are identified
- [ ] Every risk has mitigation strategy
- [ ] Worst-case scenarios are documented
- [ ] Fallback plans exist for blockers

**MAJOR:**
- [ ] Risk likelihood is estimated
- [ ] Risk impact is quantified
- [ ] Risk ownership is assigned

### Architecture Dependency

**CRITICAL:**
- [ ] ARCHITECTURE.md is approved before ROADMAP.md
- [ ] ROADMAP.md is approved before WEEKLY_TASK_PLAN.md
- [ ] No coding tasks exist without approved plan

---

## PART 3: CODE IMPLEMENTATIONS

### Correctness Criteria

**CRITICAL:**
- [ ] All tests pass: `cargo test` exits 0
- [ ] All edge cases have explicit tests
- [ ] Error handling is complete (no panics in library code)
- [ ] No `unwrap()` in production code (use `?` or explicit handling)

**MAJOR:**
- [ ] Boundary conditions are tested (empty, single, large)
- [ ] Concurrent access is tested (if `Send + Sync`)
- [ ] Integration tests cover public API
- [ ] Regression tests exist for known bugs

**MINOR:**
- [ ] Test coverage is documented
- [ ] Property tests exist for invariants
- [ ] Fuzz targets exist for parsers

### Safety Criteria

**CRITICAL:**
- [ ] No `unsafe` blocks without documented justification
- [ ] Every `unsafe` includes safety proof
- [ ] Invariants are documented in struct comments
- [ ] No undefined behavior (Miri passes)

**MAJOR:**
- [ ] Lifetime semantics are explicit
- [ ] Ownership is documented
- [ ] Drop behavior is documented (if non-trivial)

### Performance Criteria

**CRITICAL:**
- [ ] Benchmarks exist for hot paths
- [ ] Performance meets ARCHITECTURE.md budget
- [ ] No regressions vs baseline (or justified)
- [ ] Complexity analysis is documented (Big-O)

**MAJOR:**
- [ ] Allocations are minimized in hot paths
- [ ] Memory usage is documented
- [ ] Profile-guided optimizations are noted

### Maintainability Criteria

**CRITICAL:**
- [ ] No `TODO` or `FIXME` without issue reference
- [ ] No commented-out code
- [ ] No magic numbers (use named constants)
- [ ] Documentation comments exist for all public items

**MAJOR:**
- [ ] Code passes `cargo clippy` with zero warnings
- [ ] Code is formatted: `cargo fmt --check`
- [ ] Examples compile and run
- [ ] Module structure is logical

**MINOR:**
- [ ] Function length is reasonable (<100 lines)
- [ ] Nesting depth is reasonable (<4 levels)
- [ ] Variable names are descriptive

### Plan Compliance

**CRITICAL:**
- [ ] Implementation matches WEEKLY_TASK_PLAN.md task ID
- [ ] All acceptance criteria from plan are met
- [ ] No scope creep beyond approved task

---

## PART 4: BENCHMARKS

### Reproducibility Criteria

**CRITICAL:**
- [ ] Hardware specification is documented (CPU, RAM, OS)
- [ ] Rust version and commit hash are documented
- [ ] RNG seed is fixed (deterministic results)
- [ ] Reproduction commands are provided
- [ ] Another engineer can reproduce within ±5%

**MAJOR:**
- [ ] Multiple runs are performed (minimum 3)
- [ ] Standard deviation is reported
- [ ] Outliers are identified and explained

### Integrity Criteria

**CRITICAL:**
- [ ] P50 AND P99 are reported (not just mean)
- [ ] No cherry-picked results
- [ ] Worst-case scenarios are included
- [ ] Raw data is available

**MAJOR:**
- [ ] Results match performance budget from ARCHITECTURE.md
- [ ] No misleading visualizations
- [ ] Regression baselines are established

### Comparison Criteria

**CRITICAL (if comparing to competitors):**
- [ ] Same hardware for all systems
- [ ] Same dataset for all systems
- [ ] Same recall target for all systems
- [ ] All methodology differences are documented

**MAJOR:**
- [ ] Version numbers of competitors are specified
- [ ] Compilation flags are identical where possible
- [ ] Warm-up runs are performed

### Verification Handshake

**CRITICAL:**
- [ ] BENCHMARK_SCIENTIST confirms results with TEST_ENGINEER
- [ ] Optimizations did not compromise correctness
- [ ] Tests still pass after optimization

---

## PART 5: DOCUMENTATION

### Accuracy Criteria

**CRITICAL:**
- [ ] All code examples are tested in CI
- [ ] All API signatures match implementation
- [ ] All performance claims reference benchmark reports
- [ ] All browser support claims are verified

**MAJOR:**
- [ ] Version-specific information is tagged
- [ ] Deprecation warnings are clear
- [ ] Error messages match actual errors

### Completeness Criteria

**CRITICAL:**
- [ ] All public API items are documented
- [ ] All parameters are explained
- [ ] All error conditions are listed
- [ ] All examples show expected output

**MAJOR:**
- [ ] Getting started guide exists
- [ ] API reference is complete
- [ ] Architecture overview exists (public version)
- [ ] FAQ addresses common issues

### Usability Criteria

**CRITICAL:**
- [ ] Examples are copy-paste ready
- [ ] Examples work when pasted (tested)
- [ ] Installation instructions are complete
- [ ] Quickstart works in <10 minutes

**MAJOR:**
- [ ] Progressive disclosure (simple → advanced)
- [ ] Internal links work
- [ ] External links are valid
- [ ] Diagrams are clear

### Virality Criteria (README.md)

**MAJOR:**
- [ ] "Why use this?" is answered in 30 seconds
- [ ] Demo link is live
- [ ] Comparison table is fair and accurate
- [ ] Badge links are valid

---

## PART 6: WASM BINDINGS

### Compilation Criteria

**CRITICAL:**
- [ ] Builds for `wasm32-unknown-unknown` target
- [ ] `wasm-pack build --target web` succeeds
- [ ] `wasm-pack build --target bundler` succeeds
- [ ] `wasm-pack build --target nodejs` succeeds

**MAJOR:**
- [ ] No incompatible dependencies in Cargo.toml
- [ ] Bundle size is documented
- [ ] Build warnings are addressed

### Browser Compatibility Criteria

**CRITICAL:**
- [ ] Tested in Chrome (latest)
- [ ] Tested in Firefox (latest)
- [ ] Tested in Safari (latest)
- [ ] Tested in Edge (latest)
- [ ] Feature detection exists for optional APIs

**MAJOR:**
- [ ] Graceful degradation without SharedArrayBuffer
- [ ] Memory limits respected (Safari: ~1GB)
- [ ] Cross-origin isolation requirements documented

### Type Safety Criteria

**CRITICAL:**
- [ ] TypeScript definitions are complete
- [ ] All WASM exports have TypeScript signatures
- [ ] Error types are properly typed
- [ ] BigInt handling is documented

**MAJOR:**
- [ ] JSDoc comments exist
- [ ] Examples show TypeScript usage
- [ ] Type errors are caught at compile time

---

## PART 7: TESTS (Property-Based, Fuzzing)

### Coverage Criteria

**CRITICAL:**
- [ ] All invariants from ARCHITECTURE.md have property tests
- [ ] All parsers have fuzz targets
- [ ] All `unsafe` blocks are tested with Miri
- [ ] Property tests run 1000+ cases

**MAJOR:**
- [ ] Fuzz targets run for 1 hour minimum
- [ ] Integration tests cover public API
- [ ] Regression tests exist for all filed bugs

### Quality Criteria

**CRITICAL:**
- [ ] Property tests define meaningful properties (not tautologies)
- [ ] Fuzz targets accept arbitrary byte sequences
- [ ] Miri passes with zero errors
- [ ] No test flakiness (passes consistently)

**MAJOR:**
- [ ] Test names describe what they verify
- [ ] Test failures have clear error messages
- [ ] Test data generation is documented

---

## HOSTILE_REVIEWER REJECTION TRIGGERS

**AUTOMATIC REJECTION if ANY of these are true:**

### Architecture Phase
1. Contains `[UNKNOWN]` without explicit plan to resolve
2. WASM boundary has `String` or other non-FFI-safe types
3. Memory budget calculation missing or unrealistic
4. Contradictions between documents
5. No performance budget specified

### Planning Phase
1. Task > 16 hours without decomposition
2. Vague acceptance criteria (e.g., "works correctly")
3. Missing critical path analysis
4. No contingency buffer
5. ARCHITECTURE.md not approved

### Implementation Phase
1. Tests fail
2. Clippy warnings exist
3. `unsafe` without safety proof
4. Panics in library code
5. WEEKLY_TASK_PLAN.md not approved
6. Magic numbers without constants
7. Performance regression without justification

### Benchmarking Phase
1. Hardware not documented
2. Results not reproducible
3. Unfair comparisons
4. Cherry-picked results

### Documentation Phase
1. Code examples don't compile
2. API signatures don't match code
3. Performance claims without benchmark reference
4. Broken links

---

## APPROVAL PROTOCOL

### Required for Approval

1. **ALL CRITICAL criteria met** — No exceptions
2. **ALL MAJOR criteria met** — Or explicitly deferred with issue tracking
3. **MINOR criteria** — Best effort; failures tracked but don't block

### Resubmission Process

If REJECTED:
1. Address ALL critical issues
2. Address ALL major issues
3. Tag artifact `[REVISED]`
4. Resubmit for hostile review
5. Include "Changes Made" section

---

## OVERRIDE PROTOCOL

If human explicitly overrides with `[HUMAN_OVERRIDE]` tag:

**Required:**
1. Document the override in artifact
2. Log the justification
3. Acknowledge bypassed gate explicitly
4. Track technical debt if applicable

**HOSTILE_REVIEWER must:**
- Record override in review document
- State which criteria were bypassed
- Warn of consequences

---

*Checklist Version: 1.0.0*
*Project: EdgeVec*
*Authority: HOSTILE_REVIEWER — ULTIMATE VETO POWER*
