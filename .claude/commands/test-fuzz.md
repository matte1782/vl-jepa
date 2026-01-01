# Command: /test-fuzz

Execute the TEST_ENGINEER workflow to create fuzz targets for: $ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] Module to fuzz is specified (e.g., /test-fuzz parser)
- [ ] Implementation exists in `src/`
- [ ] Module handles external input (parsing, deserialization, etc.)

## Agent Reference

This command invokes the **TEST_ENGINEER** agent.
See: `.claude/agents/test-engineer.md` for complete mandate.

## Usage

```
/test-fuzz [module_name]
```

**Examples:**
```
/test-fuzz parser
/test-fuzz hnsw
/test-fuzz persistence
```

## Expected Workflow

1. Agent will analyze module for fuzzing surfaces
2. Agent will create fuzz targets in `fuzz/fuzz_targets/`
3. Agent will run initial fuzz campaign (100k+ iterations)
4. Agent will report findings and corpus

## Next Steps

After fuzz targets are created:
1. Run extended fuzzing: `cargo fuzz run [target] -- -runs=1000000`
2. If crashes found, create regression tests
3. Add to CI/CD for continuous fuzzing

## Constraints

- **MEANINGFUL FUZZING:** Targets must exercise actual logic
- **MINIMUM RUNTIME:** Initial run must be at least 100k iterations
- **CORPUS MANAGEMENT:** Interesting inputs saved to corpus/

---

*Invokes: TEST_ENGINEER agent*
*Phase: 3 (Implementation - QA)*
*Verification: Fuzzing*
