# Command: /planner-weekly

Execute the PLANNER workflow to create a weekly task plan for EdgeVec: Week $ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] `.claude/GATE_1_COMPLETE.md` exists (architecture approved)
- [ ] `docs/planning/ROADMAP.md` exists and is approved
- [ ] Week number is specified (e.g., /planner-weekly 1)

## Agent Reference

This command invokes the **PLANNER** agent.
See: `.claude/agents/planner.md` for complete mandate.

## Usage

```
/planner-weekly [week_number]
```

**Examples:**
```
/planner-weekly 1
/planner-weekly 2
```

## Expected Workflow

1. Agent will create weekly plan based on roadmap
2. Agent will generate:
   - `docs/planning/weeks/week_[N]/WEEKLY_TASK_PLAN.md`
3. Agent will request hostile review via `/review WEEKLY_TASK_PLAN.md`
4. **CRITICAL:** Only after HOSTILE_REVIEWER approves can coding begin

## Next Steps

After weekly plan is approved:
1. Run `/review WEEKLY_TASK_PLAN.md` for approval
2. If approved, GATE 2 passes (`.claude/GATE_2_COMPLETE.md` created)
3. Implementation agents can now execute tasks:
   - `/rust-implement W[N].[X]`
   - `/test-fuzz [module]`
   - `/wasm-bind [function]`

## Constraints

- **THE UNLOCK DOCUMENT:** This plan unlocks coding access
- **NO TASKS > 16 HOURS:** Must be decomposed
- **SPECIFIC ACCEPTANCE:** Every task needs measurable acceptance criteria
- **VERIFICATION STRATEGY:** Every task specifies Unit/Fuzz/Prop/Integration

---

*Invokes: PLANNER agent*
*Phase: 2 (Planning)*
*Gate: Creates the unlock document for GATE 2*
