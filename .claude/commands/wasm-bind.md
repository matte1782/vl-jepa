# Command: /wasm-bind

Execute the WASM_SPECIALIST workflow to create WASM bindings for: $ARGUMENTS

## Pre-Execution Checklist

Before beginning, verify:
- [ ] `.claude/GATE_2_COMPLETE.md` exists (plan approved)
- [ ] Function to bind is specified (e.g., /wasm-bind search)
- [ ] Function is documented in WASM_BOUNDARY.md
- [ ] Core Rust implementation exists and compiles

## Agent Reference

This command invokes the **WASM_SPECIALIST** agent.
See: `.claude/agents/wasm-specialist.md` for complete mandate.

## Usage

```
/wasm-bind [function_name]
```

**Examples:**
```
/wasm-bind search
/wasm-bind insert
/wasm-bind save
```

## Expected Workflow

1. Agent will analyze WASM boundary requirements
2. Agent will create WASM bindings in `src/wasm.rs`
3. Agent will generate TypeScript types in `pkg/*.d.ts`
4. Agent will create browser tests
5. Agent will verify builds for all targets (web, bundler, nodejs)
6. Agent will test in multiple browsers

## Next Steps

After bindings are created:
1. Test in actual browser environments
2. Verify bundle size (should be < 500KB)
3. Run `/review src/wasm.rs` for approval

## Constraints

- **BROWSER REALITY:** Test in actual browsers, not just Node
- **FFI-SAFE:** All boundary types must be FFI-safe
- **FEATURE DETECTION:** Must gracefully handle missing features
- **MEMORY LIMITS:** Must respect Safari's ~1GB WASM limit

---

*Invokes: WASM_SPECIALIST agent*
*Phase: 3 (Implementation - WASM)*
*Gate: Contributes to GATE 3 completion*
