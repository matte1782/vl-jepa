# Command: /planner-roadmap

Execute the PLANNER workflow to create a comprehensive 6-month roadmap for EdgeVec.

## Pre-Execution Checklist

Before beginning, verify:
- [ ] `.claude/GATE_1_COMPLETE.md` exists (architecture approved)
- [ ] Required context files are available:
  - docs/architecture/ARCHITECTURE.md
  - docs/architecture/DATA_LAYOUT.md
  - docs/architecture/WASM_BOUNDARY.md
- [ ] No approved roadmap exists (check docs/planning/)

## Agent Reference

This command invokes the **PLANNER** agent.
See: `.claude/agents/planner.md` for complete mandate.

## Usage

```
/planner-roadmap
```

## Expected Workflow

1. Agent will follow Chain of Thought Protocol (5 steps):
   - Architecture decomposition
   - Critical path analysis
   - Risk assessment
   - Milestone definition
   - Phase breakdown
2. Agent will generate planning documents:
   - `docs/planning/ROADMAP.md`
   - `docs/planning/RISK_REGISTER.md`
   - `docs/planning/DEPENDENCY_GRAPH.md`
3. Agent will request hostile review via `/review ROADMAP.md`

## Next Steps

After roadmap is created and approved:
1. Run `/review ROADMAP.md` for approval
2. If approved, proceed to weekly planning
3. Run `/planner-weekly 1` to create Week 1 plan

## Constraints

- **ARCHITECTURE FIRST:** Will fail if GATE 1 not passed
- **NO CODE:** Planning phase does not write implementation code
- **ESTIMATION:** Must apply 3x rule and complexity multipliers

---

*Invokes: PLANNER agent*
*Phase: 2 (Planning)*
*Gate: Creates prerequisites for GATE 2*
