# Command: /rust-implement

Execute the RUST_ENGINEER workflow to implement task: W$ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] `.claude/GATE_2_COMPLETE.md` exists (plan approved)
- [ ] Task W[N].[X] exists in approved WEEKLY_TASK_PLAN.md
- [ ] Task is not blocked (check "BLOCKED TASKS" section)
- [ ] All dependencies are satisfied

## Agent Reference

This command invokes the **RUST_ENGINEER** agent.
See: `.claude/agents/rust-engineer.md` for complete mandate.

## Usage

```
/rust-implement W[N].[X]
```

**Examples:**
```
/rust-implement W1.1
/rust-implement W2.3
```

## Expected Workflow

1. Agent will follow Chain of Thought Protocol (4 steps):
   - Task analysis
   - Test design (BEFORE implementation)
   - Implementation
   - Self-review
2. Agent will create/modify:
   - Rust source files in `src/`
   - Test files in `tests/` or inline
   - Documentation comments
3. Agent will run quality checks:
   - `cargo fmt` (auto via PostEdit hook)
   - `cargo clippy`
   - `cargo test`
4. Agent will request hostile review

## Next Steps

After implementation:
1. If complex logic (parsing, state machines, unsafe):
   - Run `/test-fuzz [module]` for fuzzing
   - Run `/test-prop [invariant]` for property tests
2. Run `/bench-baseline [component]` for performance validation
3. Run `/review [artifact]` for approval

## Constraints

- **PLAN FIRST:** Will fail if GATE 2 not passed
- **TDD:** Tests designed before implementation
- **NO PANICS:** Library code uses `Result<T, E>`
- **NO UNWRAP:** Production code doesn't use `unwrap()`
- **NO UNSAFE WITHOUT PROOF:** Unsafe blocks need justification

---

*Invokes: RUST_ENGINEER agent*
*Phase: 3 (Implementation)*
*Gate: Contributes to GATE 3 completion*
