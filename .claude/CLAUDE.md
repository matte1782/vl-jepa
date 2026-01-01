# EdgeVec Project Rules — Claude Code Edition
# Version: 2.0.0 | Military-Grade Development Protocol
# Converted from Cursor IDE format: 2025-12-11

---

## 0. THE SUPREME MANDATE

> **"Design > Code. Validation > Speed. Correctness > Convenience."**

This workspace builds **EdgeVec**, a high-performance embedded vector database in Rust/WASM. We follow a **military-grade development protocol** where:

1. **No code is written without an approved plan.**
2. **No plan is created without approved architecture.**
3. **No artifact proceeds without HOSTILE_REVIEWER approval.**

---

## 1. THE AGENT ROSTER

EdgeVec uses a specialized agent system. Each agent has a specific mandate and output format.

| Agent | Slash Command | Role | Output | Kill Authority |
|:------|:--------------|:-----|:-------|:---------------|
| **META_ARCHITECT** | `/architect-design [component]` | System design | `ARCHITECTURE.md`, `DATA_LAYOUT.md` | NO |
| **PLANNER** | `/planner-roadmap`<br>`/planner-weekly [N]` | Roadmap & tasks | `ROADMAP.md`, `WEEKLY_TASK_PLAN.md` | NO |
| **RUST_ENGINEER** | `/rust-implement W[N].[X]` | Core implementation | Rust code in `src/` | NO |
| **TEST_ENGINEER** | `/test-fuzz [module]`<br>`/test-prop [invariant]` | QA & Fuzzing | Tests, Fuzz targets, Regression suites | NO |
| **WASM_SPECIALIST** | `/wasm-bind [function]` | Browser integration | WASM bindings, TypeScript | NO |
| **BENCHMARK_SCIENTIST** | `/bench-baseline [component]`<br>`/bench-compare [competitor]` | Performance testing | Benchmark reports | NO |
| **HOSTILE_REVIEWER** | `/review [artifact]` | Quality gate | GO/NO_GO verdicts | **YES** |
| **DOCWRITER** | `/doc-readme`<br>`/doc-api [module]` | Documentation | README, API docs | NO |
| **PROMPT_MAKER** | `/dispatch` | Meta-agent dispatcher, quality control, workflow routing | Recommended command + constraint-aware prompts | NO |

### Agent Definitions

All agents are defined in `.claude/agents/*.md`. Each agent file contains:
- Mandate and principles
- Chain of thought protocol
- Output formats
- Anti-hallucination clamps
- Hostile gate protocol

### Command Invocation

All slash commands are defined in `.claude/commands/*.md`. To invoke:

```
/architect-design gap_analysis
/planner-weekly 1
/rust-implement W1.1
/review ARCHITECTURE.md
```

### Using the PROMPT_MAKER Meta-Agent

**The `/dispatch` command activates PROMPT_MAKER**, which operates in three sequential modes:

**MODE 1: Safety Scanner**
- Detects current project phase
- Validates all contracts (Architecture > Plan > Code)
- Checks for gate completions and prerequisites
- Outputs ✅ VALID or ⛔ VIOLATION

**MODE 2: Agent Router**
- Classifies request intent
- Maps to correct specialized agent
- Plans multi-agent pipelines if needed
- Recommends specific command with arguments

**MODE 3: Prompt Generator**
- Loads relevant context (architecture, plans, etc.)
- Injects constraints from ARCHITECTURE.md, CLAUDE.md, etc.
- Creates structured, atomic task descriptions
- Includes validation criteria and next steps
- Manages context window to prevent overflow

**When to use `/dispatch`:**
- You're unsure which agent/command to use
- You want to verify a request won't violate contracts
- You need a structured prompt with all relevant constraints
- You want to see the full pipeline for a complex task

**Example:**
```
/dispatch

[PROMPT_MAKER analyzes your recent message and outputs:]
- Current phase detection
- Contract validation
- Recommended command
- Expected outcome
- Next step in pipeline
```

---

## 2. THE WORKFLOW (GENESIS SEQUENCE)

```
┌──────────────────────────────────────────────────────────────────────┐
│                   GENESIS WORKFLOW (RIGID SEQUENCE)                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 0: Setup                                                      │
│  ├── [x] Create .claude/ configuration                              │
│  ├── [x] Create agent definitions                                   │
│  └── [ ] Initialize Cargo project                                   │
│                                                                      │
│  Phase 1: Architecture (No Code Allowed)                            │
│  ├── [ ] Run /architect-design → creates ARCHITECTURE.md            │
│  ├── [ ] Run /architect-design → creates DATA_LAYOUT.md             │
│  ├── [ ] Run /architect-design → creates WASM_BOUNDARY.md           │
│  ├── [ ] Run /review ARCHITECTURE.md                                │
│  └── [ ] GATE 1: .claude/GATE_1_COMPLETE.md created                 │
│                                                                      │
│  Phase 2: Planning (No Code Allowed)                                │
│  ├── [ ] Run /planner-roadmap → creates ROADMAP.md                  │
│  ├── [ ] Run /review ROADMAP.md                                     │
│  ├── [ ] Run /planner-weekly 1 → creates WEEKLY_TASK_PLAN.md        │
│  ├── [ ] Run /review WEEKLY_TASK_PLAN.md                            │
│  └── [ ] GATE 2: .claude/GATE_2_COMPLETE.md created                 │
│                                                                      │
│  Phase 3: Implementation (Code Allowed — For Approved Tasks Only)   │
│  ├── [ ] Run /rust-implement W[N].[X] for approved tasks            │
│  ├── [ ] Run /test-fuzz [module] for complex logic                  │
│  ├── [ ] Run /test-prop [invariant] for invariants                  │
│  ├── [ ] Run /wasm-bind [function] for WASM exports                 │
│  ├── [ ] Run /bench-baseline [component] for performance            │
│  ├── [ ] Run /review [deliverable] for each artifact                │
│  └── [ ] GATE 3: .claude/GATE_3_COMPLETE.md created                 │
│                                                                      │
│  Phase 4: Polish & Launch                                           │
│  ├── [ ] Run /doc-readme → creates README.md                        │
│  ├── [ ] Run /review README.md                                      │
│  ├── [ ] GATE 4: .claude/GATE_4_COMPLETE.md created                 │
│  └── [ ] Ship v0.1.0                                                │
│                                                                      │
│ └──────────────────────────────────────────────────────────────────────┘
```

---

## 3. QUALITY STANDARDS

### 3.1 Code Standards

| Standard | Requirement | Enforcement |
|:---------|:------------|:------------|
| **Testing** | 100% coverage for public API | `cargo tarpaulin` |
| **Verification** | Property tests for all algos | `proptest` |
| **Fuzzing** | Fuzzing for all parsers/inputs | `cargo fuzz` |
| **Formatting** | `cargo fmt` | Auto-run via PostEdit hook |
| **Linting** | `cargo clippy -- -D warnings` | Auto-run via PostEdit hook |
| **Safety** | No `unsafe` without proof | HOSTILE_REVIEWER gate |
| **Errors** | No `unwrap()` in library code | HOSTILE_REVIEWER gate |

### 3.2 Architecture Standards

| Standard | Requirement |
|:---------|:------------|
| **Struct Sizes** | All structs have documented size and alignment |
| **Memory Budget** | Calculated for 1M vectors |
| **WASM Boundary** | All exported functions are FFI-safe |
| **Performance Budget** | <10ms search for 100k vectors |
| **Persistence Format** | Magic number + version + checksum |

### 3.3 Planning Standards

| Standard | Requirement |
|:---------|:------------|
| **Task Size** | No task > 16 hours (must decompose) |
| **Estimation** | 3x rule applied to all estimates |
| **Acceptance** | Every task has binary pass/fail criteria |
| **Dependencies** | All dependencies are specific and verifiable |

---

## 4. HOSTILE GATE PROTOCOL

### 4.1 Gate Checkpoints

```
┌─────────────────────────────────────────────────────────────┐
│   GATE 1: Architecture → Planning                           │
│   Requires: /review approval of:                            │
│   - ARCHITECTURE.md                                         │
│   - DATA_LAYOUT.md                                          │
│   - WASM_BOUNDARY.md                                        │
│   Creates: .claude/GATE_1_COMPLETE.md                       │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│   GATE 2: Planning → Implementation                         │
│   Requires: /review approval of:                            │
│   - ROADMAP.md                                              │
│   - WEEKLY_TASK_PLAN.md                                     │
│   Creates: .claude/GATE_2_COMPLETE.md                       │
│   Unlocks: Write access to src/**                           │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│   GATE 3: Implementation → Merge                            │
│   Requires: /review approval of:                            │
│   - All code changes                                        │
│   - All unit/prop/fuzz tests pass                           │
│   - Benchmark validates performance                         │
│   Creates: .claude/GATE_3_COMPLETE.md                       │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│   GATE 4: Documentation → Release                           │
│   Requires: /review approval of:                            │
│   - README.md                                               │
│   - API documentation                                       │
│   - CHANGELOG.md                                            │
│   Creates: .claude/GATE_4_COMPLETE.md                       │
│   Unlocks: cargo publish permission                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Gate Enforcement

**Automated via Hooks:**
- PreToolUse hooks check for gate completion files before allowing risky operations
- PostToolUse hooks run quality checks after edits
- Permission system denies operations before gates pass

**Manual Override:**
If human explicitly overrides with `[HUMAN_OVERRIDE]` tag:
1. Document the override in git commit
2. Log the justification
3. Proceed with explicit acknowledgment of bypassed gate

---

## 5. DIRECTORY STRUCTURE

```
edgevec/
├── .claude/
│   ├── CLAUDE.md                          # This file (project rules)
│   ├── HOSTILE_GATE_CHECKLIST.md          # Quality gate criteria
│   ├── WORKFLOW_ROUTER.md                 # Dispatcher logic
│   ├── settings.json                      # Permissions, hooks, env
│   ├── agents/
│   │   ├── meta-architect.md
│   │   ├── planner.md
│   │   ├── rust-engineer.md
│   │   ├── test-engineer.md
│   │   ├── wasm-specialist.md
│   │   ├── benchmark-scientist.md
│   │   ├── hostile-reviewer.md
│   │   └── docwriter.md
│   ├── commands/
│   │   ├── dispatch.md
│   │   ├── architect-design.md
│   │   ├── planner-roadmap.md
│   │   ├── planner-weekly.md
│   │   ├── rust-implement.md
│   │   ├── test-fuzz.md
│   │   ├── test-prop.md
│   │   ├── wasm-bind.md
│   │   ├── bench-baseline.md
│   │   ├── bench-compare.md
│   │   ├── review.md
│   │   └── doc-readme.md
│   ├── hooks/
│   │   └── pre-commit-review.sh
│   ├── GATE_1_COMPLETE.md                 # Created after arch approval
│   ├── GATE_2_COMPLETE.md                 # Created after plan approval
│   ├── GATE_3_COMPLETE.md                 # Created after impl approval
│   └── GATE_4_COMPLETE.md                 # Created after doc approval
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md                # System design
│   │   ├── DATA_LAYOUT.md                 # Memory layouts
│   │   ├── WASM_BOUNDARY.md               # WASM interface
│   │   └── TEST_STRATEGY.md               # Testing approach
│   ├── planning/
│   │   ├── ROADMAP.md                     # 6-month plan
│   │   ├── weeks/
│   │   │   └── week_*/
│   │   │       └── WEEKLY_TASK_PLAN.md    # Weekly plans
│   │   └── RISK_REGISTER.md               # Known risks
│   ├── reviews/
│   │   └── [YYYY-MM-DD]_[artifact].md     # Hostile reviews
│   └── benchmarks/
│       └── [YYYY-MM-DD]_report.md         # Performance reports
├── src/
│   ├── lib.rs                             # Library root
│   └── ...                                # Implementation
├── benches/
│   └── ...                                # Benchmarks
├── tests/
│   └── ...                                # Tests
├── fuzz/
│   └── ...                                # Fuzz targets
├── Cargo.toml
├── README.md
└── CHANGELOG.md
```

---

## 6. TECHNICAL CONSTRAINTS

### 6.1 Rust Constraints

| Constraint | Reason |
|:-----------|:-------|
| Edition 2021 | Modern Rust features |
| MSRV 1.70 | WASM stability |
| `#![no_std]` optional | Embedded support |
| No external C deps | WASM compatibility |

### 6.2 WASM Constraints

| Constraint | Reason |
|:-----------|:-------|
| Target: `wasm32-unknown-unknown` | Universal support |
| Bundle size < 500KB | Fast loading |
| No `std::thread` | Use `wasm-bindgen-rayon` |
| No `std::fs` | Use IndexedDB |

### 6.3 Performance Constraints

| Metric | Target | Constraint |
|:-------|:-------|:-----------|
| Search latency (100k) | <10ms | P99 |
| Insert latency | <2ms (Quant) / <5ms (F32) | Mean |
| Memory per vector | <100 bytes | Including index |
| Index load time | <500ms | 100k vectors |

---

## 7. SALVAGED CODE POLICY

### From binary_semantic_cache

The following code is **approved for salvage**:

| File | Lines | Function | Status |
|:-----|:------|:---------|:-------|
| `similarity.rs` | 286-292 | `hamming_distance_single` | ✅ APPROVED |
| `similarity.rs` | 308-310 | `distance_to_similarity` | ✅ APPROVED |
| `encoder.rs` | 316-336 | `project_single` | ✅ APPROVED |
| `encoder.rs` | 343-359 | `binarize_and_pack_single` | ✅ APPROVED |

**Attribution Required:**
```rust
// Adapted from binary_semantic_cache v1.0 (MIT License)
// Copyright (c) 2024 Matteo Panzeri
// Original: https://github.com/[user]/binary_semantic_cache
```

**Everything Else:** Must be written from scratch.

---

## 8. COMMUNICATION PROTOCOL

### 8.1 Agent Handoffs

Every agent must end their work with an explicit handoff:

```markdown
## [AGENT]: Task Complete

Artifacts generated:
- [List files]

Status: [PENDING_HOSTILE_REVIEW | READY_FOR_NEXT_PHASE]

Next: [/review [artifact] | /next-command]
```

### 8.2 Status Tags

| Tag | Meaning |
|:----|:--------|
| `[DRAFT]` | Work in progress |
| `[PROPOSED]` | Ready for hostile review |
| `[APPROVED]` | Passed hostile review |
| `[REJECTED]` | Failed hostile review |
| `[REVISED]` | Updated after rejection |

---

## 9. EMERGENCY PROCEDURES

### 9.1 If Hostile Review Fails

1. Read rejection document carefully
2. Address ALL critical issues
3. Address ALL major issues
4. Update artifact with `[REVISED]` tag
5. Resubmit via `/review [artifact]`

### 9.2 If Stuck

1. Run `/dispatch [describe situation]` to get routing recommendation
2. Check `docs/INVOCATION_REFERENCE.md` for correct command
3. Check `docs/MIGRATION_GUIDE.md` if coming from Cursor IDE

---

## 10. MIGRATION NOTES

This project was converted from Cursor IDE format to Claude Code format on 2025-12-11.

**Key Changes:**
- `@AGENT_NAME` → `/command-name` invocation pattern
- `.cursorrules` → split into user-level and project-level CLAUDE.md
- `.cursor/commands/` → `.claude/agents/` + `.claude/commands/`
- Manual gate enforcement → Automated via hooks and permissions
- No permission system → Explicit permissions in settings.json

**See:**
- `docs/MIGRATION_GUIDE.md` for detailed migration guide
- `docs/INVOCATION_REFERENCE.md` for command quick reference
- `docs/CURSOR_TO_CLAUDE_MAPPING.md` for complete conversion mapping

---

## REVISION HISTORY

| Version | Date | Change |
|:--------|:-----|:-------|
| 1.0.0 | 2025-12-04 | Initial EdgeVec Genesis Protocol (Cursor format) |
| 1.1.0 | 2025-12-05 | Added TEST_ENGINEER and PROMPT_MAKER |
| 2.0.0 | 2025-12-11 | Converted to Claude Code format with hooks/permissions |

---

**END OF EDGEVEC PROJECT RULES**
