# WORKFLOW_ROUTER

**Version:** 1.0.0
**Purpose:** Dispatcher logic for routing user requests to correct agent/command
**Replaces:** PROMPT_MAKER agent from Cursor system

---

## MISSION

This document defines the decision tree for analyzing user requests and routing them to the appropriate Claude Code agent or slash command. It enforces the **Supreme Rule**: `Architecture > Plan > Code`.

---

## PHASE-AWARE ROUTING

**CRITICAL:** The router MUST check which phase the project is in before routing.

### Phase Detection Logic

```markdown
## Phase Detection

Check these files in order:

1. **Is GATE_1_COMPLETE.md present?**
   - NO → Phase 1 (Architecture) — ONLY META_ARCHITECT allowed
   - YES → Check next

2. **Is GATE_2_COMPLETE.md present?**
   - NO → Phase 2 (Planning) — ONLY PLANNER allowed
   - YES → Check next

3. **Is GATE_3_COMPLETE.md present?**
   - NO → Phase 3 (Implementation Setup)
   - YES → Phase 4 (Full Implementation)

4. **Current Weekly Plan Status?**
   - Check WEEKLY_TASK_PLAN.md for status: [APPROVED | IN_PROGRESS | COMPLETE]
```

### Phase-Based Restrictions

| Phase | Allowed Agents | Forbidden Actions |
|:------|:---------------|:------------------|
| **Phase 1** | META_ARCHITECT, HOSTILE_REVIEWER | Code writing, testing, benchmarking |
| **Phase 2** | PLANNER, HOSTILE_REVIEWER | Code writing, testing, benchmarking |
| **Phase 3** | RUST_ENGINEER, TEST_ENGINEER, WASM_SPECIALIST, BENCHMARK_SCIENTIST, HOSTILE_REVIEWER | Architecture changes |
| **Phase 4** | All agents | Architecture changes without approval cycle |

---

## REQUEST CLASSIFICATION MATRIX

### Step 1: Keyword Analysis

Extract keywords from user request and classify intent:

| Keywords | Intent Category | Primary Agent | Secondary Agent |
|:---------|:----------------|:--------------|:----------------|
| "design", "architecture", "how should we", "data layout", "memory" | Architecture Design | META_ARCHITECT | HOSTILE_REVIEWER |
| "plan", "roadmap", "milestone", "timeline", "estimate" | Planning | PLANNER | HOSTILE_REVIEWER |
| "implement", "build", "code", "function", "struct" | Implementation | RUST_ENGINEER | TEST_ENGINEER |
| "test", "verify", "property", "invariant" | Verification | TEST_ENGINEER | RUST_ENGINEER |
| "fuzz", "crash", "edge case", "undefined behavior" | Fuzzing | TEST_ENGINEER | HOSTILE_REVIEWER |
| "WASM", "browser", "binding", "JavaScript", "TypeScript" | WASM Integration | WASM_SPECIALIST | HOSTILE_REVIEWER |
| "benchmark", "performance", "latency", "throughput", "memory usage" | Performance | BENCHMARK_SCIENTIST | HOSTILE_REVIEWER |
| "review", "approve", "reject", "validate", "quality" | Quality Gate | HOSTILE_REVIEWER | (none) |
| "document", "README", "API docs", "changelog" | Documentation | DOCWRITER | HOSTILE_REVIEWER |
| "fix", "bug", "regression", "broken" | Bug Fix | RUST_ENGINEER | TEST_ENGINEER |
| "optimize", "faster", "smaller", "efficiency" | Optimization | RUST_ENGINEER | BENCHMARK_SCIENTIST |

### Step 2: Context Analysis

Check these contextual factors:

1. **Which files are open?**
   - `*.md` in `docs/` → Likely documentation work → DOCWRITER
   - `*.rs` in `src/` → Likely implementation → RUST_ENGINEER
   - `*.rs` in `tests/` or `fuzz/` → Likely testing → TEST_ENGINEER
   - `benches/*.rs` → Likely benchmarking → BENCHMARK_SCIENTIST

2. **What was the last command used?**
   - If last was `/rust-engineer W1.1`, and user says "now test this" → TEST_ENGINEER
   - If last was `/architect-design`, and user says "looks good" → HOSTILE_REVIEWER

3. **Is there a task ID mentioned?**
   - "W1.1", "W2.3" → Implementation task → RUST_ENGINEER
   - "M1.2" → Milestone → PLANNER
   - "GATE_1", "GATE_2" → Gate validation → HOSTILE_REVIEWER

---

## ROUTING DECISION TREE

```
START
  │
  ├─ Request contains "review" or "approve"?
  │  └─ YES → /review [artifact]
  │  └─ NO → Continue
  │
  ├─ Phase 1 (Architecture)?
  │  │
  │  ├─ Request about design/architecture?
  │  │  └─ YES → /architect-design [component]
  │  │  └─ NO → BLOCK: "Architecture must be completed first"
  │  │
  │  └─ Request to validate architecture?
  │     └─ YES → /review ARCHITECTURE.md
  │
  ├─ Phase 2 (Planning)?
  │  │
  │  ├─ Request for roadmap?
  │  │  └─ YES → /planner-roadmap
  │  │
  │  ├─ Request for weekly plan?
  │  │  └─ YES → /planner-weekly [N]
  │  │
  │  └─ Request to validate plan?
  │     └─ YES → /review [ROADMAP.md | WEEKLY_TASK_PLAN.md]
  │
  ├─ Phase 3/4 (Implementation)?
  │  │
  │  ├─ Request about WASM?
  │  │  └─ YES → /wasm-bind [function] or /wasm-types
  │  │
  │  ├─ Request about testing?
  │  │  └─ YES → /test-prop [invariant] or /test-fuzz [module]
  │  │
  │  ├─ Request about benchmarking?
  │  │  └─ YES → /bench-baseline [component] or /bench-compare [competitor]
  │  │
  │  ├─ Request about documentation?
  │  │  └─ YES → /doc-readme or /doc-api [module]
  │  │
  │  ├─ Request to implement task?
  │  │  │
  │  │  ├─ Is WEEKLY_TASK_PLAN.md approved?
  │  │  │  └─ NO → BLOCK: "Plan must be approved first"
  │  │  │  └─ YES → Continue
  │  │  │
  │  │  ├─ Task ID specified (e.g., W1.1)?
  │  │  │  └─ YES → /rust-implement W[N].[X]
  │  │  │  └─ NO → Ask user for task ID
  │  │
  │  └─ Request is vague?
  │     └─ YES → /dispatch (analyze and recommend)
```

---

## PATTERN MATCHING TABLE

Quick lookup for common request patterns:

| User Request Pattern | Recommended Command | Notes |
|:---------------------|:--------------------|:------|
| "Design the HNSW index" | `/architect-design hnsw` | Phase 1 only |
| "Create a roadmap" | `/planner-roadmap` | Requires approved architecture |
| "Plan week 1" | `/planner-weekly 1` | Requires approved roadmap |
| "Implement W1.1" | `/rust-implement W1.1` | Requires approved weekly plan |
| "Test the insert function" | `/test-prop insert` | After implementation |
| "Fuzz the parser" | `/test-fuzz parser` | After implementation |
| "Create WASM bindings for search" | `/wasm-bind search` | After core implementation |
| "Benchmark search latency" | `/bench-baseline search` | After implementation |
| "Compare to sqlite-vec" | `/bench-compare sqlite-vec` | After baseline exists |
| "Review ARCHITECTURE.md" | `/review ARCHITECTURE.md` | Any phase |
| "Update README" | `/doc-readme` | After implementation exists |
| "Document the API" | `/doc-api [module]` | After API is stable |
| "Fix bug in HNSW" | `/rust-implement [bug-task-id]` | Must have task ID in plan |
| "Optimize search" | `/rust-implement [opt-task-id]` | Must have task ID; then `/bench-baseline` |

---

## CONTRACT VIOLATION DETECTION

Before routing, check for these violations:

### Violation 1: Bypassing Architecture

**Trigger:**
- User requests code without approved ARCHITECTURE.md
- User requests plan without approved ARCHITECTURE.md

**Response:**
```
⛔ CONTRACT VIOLATION: Supreme Rule Broken

The request "[user request]" violates the Supreme Rule:
Architecture > Plan > Code

Current Status: Phase [N]
Required: [What must be approved first]

Recommended Action:
1. Complete architecture: /architect-design [component]
2. Get hostile review: /review ARCHITECTURE.md
3. Then proceed with: [original request]
```

### Violation 2: Bypassing Planning

**Trigger:**
- User requests code without approved WEEKLY_TASK_PLAN.md

**Response:**
```
⛔ CONTRACT VIOLATION: Coding Without Approved Plan

The request "[user request]" attempts to write code without an approved plan.

Current Status: No approved WEEKLY_TASK_PLAN.md
Required: PLANNER must create and HOSTILE_REVIEWER must approve weekly plan

Recommended Action:
1. Create plan: /planner-weekly [N]
2. Get approval: /review WEEKLY_TASK_PLAN.md
3. Then proceed with: /rust-implement [task-id]
```

### Violation 3: Scope Creep

**Trigger:**
- User requests work not in approved WEEKLY_TASK_PLAN.md

**Response:**
```
⚠️ SCOPE CREEP DETECTED

The request "[user request]" is not in the current approved plan.

Current Week's Tasks: [List from WEEKLY_TASK_PLAN.md]
Requested: [user request]

Options:
1. Add to next week's plan (recommended)
2. Request plan amendment (requires HOSTILE_REVIEWER approval)
3. Defer to backlog

Recommended Action:
/planner-replan "[reason for amendment]"
```

---

## TRIVIALITY FAST-TRACKING

Some requests can bypass the full pipeline:

### Trivial Changes (Fast Track to DOCWRITER)

**Criteria:**
- Typo fixes
- Comment updates
- README formatting
- Link corrections

**Route directly to:**
- `/doc-readme` or `/doc-api [module]`

**No review required IF:**
- No code logic changes
- No API changes
- No architectural impact

### Documentation-Only Changes

**Criteria:**
- README updates
- Example additions
- Comment improvements

**Route to:**
- DOCWRITER → HOSTILE_REVIEWER (lightweight review)

---

## AMBIGUOUS REQUEST HANDLING

If user request is unclear:

### Step 1: Clarification Questions

Ask these questions:

1. **"What phase are you in?"**
   - Are you designing, planning, or implementing?

2. **"What artifact do you want to produce?"**
   - Architecture doc? Plan? Code? Tests? Benchmarks?

3. **"Is this in the current plan?"**
   - If Phase 3+: Does this task exist in WEEKLY_TASK_PLAN.md?

### Step 2: Recommend Options

```
📋 REQUEST ANALYSIS

Based on your request "[user request]", here are the options:

Option A: Design/Architecture
- If you want to design this feature first
- Command: /architect-design [component]
- Next: /review ARCHITECTURE.md

Option B: Planning
- If you want to plan the implementation
- Command: /planner-weekly [N]
- Next: /review WEEKLY_TASK_PLAN.md

Option C: Implementation
- If architecture and plan are approved
- Command: /rust-implement [task-id]
- Next: /test-prop [task-id]

Which option matches your intent?
```

---

## HANDOFF CHAIN LOGIC

After routing to an agent, the dispatcher must suggest the next command:

| Current Command | Expected Next Command | Condition |
|:----------------|:----------------------|:----------|
| `/architect-design` | `/review ARCHITECTURE.md` | Design complete |
| `/review ARCHITECTURE.md` (approved) | `/planner-roadmap` | Gate 1 passed |
| `/planner-roadmap` | `/review ROADMAP.md` | Roadmap complete |
| `/review ROADMAP.md` (approved) | `/planner-weekly 1` | Gate 2 passed |
| `/planner-weekly N` | `/review WEEKLY_TASK_PLAN.md` | Plan complete |
| `/review WEEKLY_TASK_PLAN.md` (approved) | `/rust-implement W[N].1` | Gate 3 passed |
| `/rust-implement W[N].[X]` | `/test-prop W[N].[X]` | Implementation complete |
| `/test-prop W[N].[X]` | `/test-fuzz [module]` | Property tests pass |
| `/test-fuzz [module]` | `/wasm-bind [function]` (if WASM) or `/bench-baseline [component]` | Fuzzing complete |
| `/wasm-bind [function]` | `/bench-baseline [component]` | WASM bindings complete |
| `/bench-baseline [component]` | `/review [all deliverables]` | Benchmarks complete |
| `/review [task output]` (approved) | `/doc-api [module]` or next task | Task approved |

---

## SPECIAL ROUTING CASES

### Case 1: Bug Reports

If user reports a bug:

1. **Check if bug is in current plan**
   - YES → Route to assigned agent
   - NO → Create bug task in WEEKLY_TASK_PLAN.md

2. **Determine affected component**
   - Core logic → RUST_ENGINEER
   - WASM binding → WASM_SPECIALIST
   - Documentation → DOCWRITER

3. **Route with test requirement**
   - `/rust-implement [bug-task-id]` + `/test-regression [bug-id]`

### Case 2: Optimization Requests

If user requests optimization:

1. **Require baseline first**
   - Has baseline? → Proceed
   - No baseline? → `/bench-baseline [component]` first

2. **Create optimization task**
   - Add to WEEKLY_TASK_PLAN.md
   - Requires HOSTILE_REVIEWER approval

3. **Route with benchmark comparison**
   - `/rust-implement [opt-task-id]` + `/bench-compare baseline`

### Case 3: Refactoring Requests

If user requests refactoring:

1. **Require tests first**
   - Have tests? → Proceed
   - No tests? → `/test-prop [module]` first

2. **Check if in plan**
   - In plan? → Route to RUST_ENGINEER
   - Not in plan? → Require planning cycle

3. **Route with regression check**
   - `/rust-implement [refactor-task-id]` + `/test-regression` + `/bench-regression`

---

## DISPATCHER OUTPUT FORMAT

When `/dispatch` is invoked, output:

```markdown
## WORKFLOW_ROUTER: Request Analysis

### User Request
"[Original request]"

### Phase Detection
Current Phase: [1 | 2 | 3 | 4]
Gate Status: GATE_[N]_[COMPLETE | INCOMPLETE]
Weekly Plan: [APPROVED | PENDING | NONE]

### Intent Classification
Primary Intent: [Architecture | Planning | Implementation | Testing | etc.]
Keywords Detected: [list]

### Contract Validation
- [ ] Architecture approved (if required)
- [ ] Plan approved (if required)
- [ ] Task in current plan (if required)
Status: [VALID | VIOLATION]

### Recommended Command
Primary: /[command-name] [args]
Rationale: [Why this command]

Next Step: /[next-command] [args]

### Alternative Options
- Option A: /[alt-command-1] — [When to use]
- Option B: /[alt-command-2] — [When to use]

### Required Context Files
Before executing, ensure these files are loaded:
- [ ] [file1.md]
- [ ] [file2.md]
Use: `/add` for each file
```

---

## EXECUTION TRIGGERS

### Trigger: `/dispatch`

Analyze user's current request and recommend appropriate command.

**Usage:**
```
/dispatch
```

**No arguments required** — The dispatcher analyzes the conversation context.

---

*Router Version: 1.0.0*
*Project: EdgeVec*
*Authority: Enforces Supreme Rule*
