# Command: /test-prop

Execute the TEST_ENGINEER workflow to create property tests for invariant: $ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] Invariant to verify is specified
- [ ] Invariant is documented in ARCHITECTURE.md
- [ ] Implementation exists in `src/`

## Agent Reference

This command invokes the **TEST_ENGINEER** agent.
See: `.claude/agents/test-engineer.md` for complete mandate.

## Usage

```
/test-prop [invariant_name]
```

**Examples:**
```
/test-prop graph_connectivity
/test-prop hnsw_hierarchy
/test-prop vector_id_validity
```

## Expected Workflow

1. Agent will extract invariant from ARCHITECTURE.md
2. Agent will design property test strategy
3. Agent will implement `proptest` suite
4. Agent will run 1000+ test cases
5. Agent will report verification results

## Next Steps

After property tests pass:
1. Add to main test suite
2. Run in CI for regression detection
3. Document which invariants are property-tested

## Constraints

- **ARCHITECTURAL REFERENCE:** Must reference specific invariant
- **MEANINGFUL PROPERTIES:** Not tautologies or trivial checks
- **SUFFICIENT CASES:** Minimum 1000 generated test cases

---

*Invokes: TEST_ENGINEER agent*
*Phase: 3 (Implementation - QA)*
*Verification: Property Testing*
