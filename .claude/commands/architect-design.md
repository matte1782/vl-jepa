# Command: /architect-design

Execute the META_ARCHITECT workflow to design system architecture for: $ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] Required context files are available:
  - ASSET_FIT_REPORT.md (if exists)
  - 10_HOSTILE_GATE.md (if exists)
  - Any existing specs in docs/
- [ ] No approved architecture exists (check docs/architecture/)
- [ ] This is Phase 1 of the Genesis Workflow

## Agent Reference

This command invokes the **META_ARCHITECT** agent.
See: `.claude/agents/meta-architect.md` for complete mandate.

## Usage

```
/architect-design [component_name]
```

**Examples:**
```
/architect-design gap_analysis
/architect-design hnsw_index
/architect-design persistence_layer
```

## Expected Workflow

1. Agent will follow Chain of Thought Protocol (5 steps)
2. Agent will generate architecture documents:
   - `docs/architecture/ARCHITECTURE.md`
   - `docs/architecture/DATA_LAYOUT.md`
   - `docs/architecture/WASM_BOUNDARY.md`
3. Agent will request hostile review via `/review ARCHITECTURE.md`

## Next Steps

After architecture documents are created:
1. Run `/review ARCHITECTURE.md` for approval
2. If approved, GATE 1 passes
3. Proceed to planning phase with `/planner-roadmap`

## Constraints

- **NO CODE:** Architecture phase does not write implementation code
- **NO PLANNING:** Do not create roadmaps or task plans
- **COMPLETENESS:** All three documents (ARCHITECTURE, DATA_LAYOUT, WASM_BOUNDARY) must be created

---

*Invokes: META_ARCHITECT agent*
*Phase: 1 (Architecture)*
*Gate: Creates prerequisites for GATE 1*
