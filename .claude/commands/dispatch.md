# Command: dispatch

**Purpose:** Analyze user request and recommend the appropriate agent/command
**Agent:** PROMPT_MAKER (see `.claude/agents/prompt-maker.md`)
**Version:** 2.0.0

---

## OVERVIEW

This command activates the **PROMPT_MAKER** meta-agent, which operates in three sequential modes:

1. **MODE 1: Safety Scanner** — Validate contracts and detect violations
2. **MODE 2: Agent Router** — Map request to correct agent/command
3. **MODE 3: Prompt Generator** — Create structured, constraint-aware prompts

**Authority:** PROMPT_MAKER has **NO KILL AUTHORITY** — it enforces contracts but cannot override Supreme Rules.

---

## EXECUTION

When this command is invoked, follow this protocol:

### Step 1: Load Context

Read the following files to understand project state:

```
REQUIRED CONTEXT:
- .claude/WORKFLOW_ROUTER.md — Decision tree logic
- README.md — Current project status
- .claude/CLAUDE.md — Global rules (if exists)

OPTIONAL CONTEXT (check if exists):
- GATE_1_COMPLETE.md — Architecture approval status
- GATE_2_COMPLETE.md — Planning approval status
- GATE_3_COMPLETE.md — Implementation approval status
- WEEKLY_TASK_PLAN.md — Current week's approved tasks
- ARCHITECTURE.md — Design reference
- ROADMAP.md — Overall plan
```

### Step 2: Execute MODE 1 — Safety Scanner

**CRITICAL:** This mode MUST complete before routing. It validates all contracts.

**Protocol:**
1. **Detect Current Phase**
   - Check which GATE_*.md files exist in `.claude/` and root
   - Determine: Phase 1 (Architecture) | Phase 2 (Planning) | Phase 3+ (Implementation)

2. **Extract Intent**
   - Parse keywords from user request (see WORKFLOW_ROUTER.md keyword matrix)
   - Classify: Architecture | Planning | Implementation | Testing | Benchmarking | Documentation | Review

3. **Validate Contracts**
   - Check if request violates Supreme Rule (Architecture > Plan > Code)
   - Verify required gate completions (GATE_1_COMPLETE.md, etc.)
   - Verify required approvals exist (WEEKLY_TASK_PLAN.md if implementation)
   - Detect scope creep (task not in approved plan)

4. **Output Verdict**
   - **✅ VALID:** All contracts satisfied → Proceed to MODE 2
   - **⛔ VIOLATION:** Contract broken → Output violation details and HALT

**If VIOLATION detected:** Skip to "Contract Violation Response" section below.

### Step 3: Execute MODE 2 — Agent Router

**Only execute if MODE 1 returned ✅ VALID**

**Protocol:**
1. **Pattern Match**
   - Use the Pattern Matching Table from WORKFLOW_ROUTER.md
   - Find closest match to user's request

2. **Apply Context Clues**
   - Which files are open/mentioned?
   - What was the last command?
   - Are task IDs mentioned (W1.1, etc.)?

3. **Select Primary Agent**
   - Map intent to specialized agent
   - Verify agent is allowed in current phase

4. **Identify Pipeline**
   - Determine if multi-agent orchestration needed
   - Plan handoff sequence
   - Identify next step after current command

### Step 4: Execute MODE 3 — Prompt Generator

**Only execute if MODE 2 selected an agent successfully**

**Protocol:**
1. **Load Constraint Sources**
   - Read ARCHITECTURE.md (if relevant sections exist)
   - Read DATA_LAYOUT.md (if relevant for implementation)
   - Read WASM_BOUNDARY.md (if WASM-related)
   - Read current WEEKLY_TASK_PLAN.md (if implementation phase)

2. **Inject Constraints**
   - Extract relevant sections from architecture documents
   - Quote exact constraints that apply to the task
   - Include section numbers (e.g., "Per ARCHITECTURE.md §3.2")

3. **Generate Structured Prompt**
   - Create atomic, measurable task description
   - List required context files
   - Provide step-by-step instructions (max 7 steps)
   - Include validation criteria
   - Specify expected outputs
   - State next command in pipeline

4. **Verify Context Window**
   - Check total token usage
   - Apply progressive disclosure if approaching limits

### Step 5: Generate Recommendation

Output the following analysis:

```markdown
## WORKFLOW_ROUTER: Request Analysis

### User Request
"[Quote the user's original request]"

---

### Phase Detection

**Current Phase:** [1 | 2 | 3 | 4]

**Evidence:**
- GATE_1_COMPLETE.md: [EXISTS | MISSING]
- GATE_2_COMPLETE.md: [EXISTS | MISSING]
- GATE_3_COMPLETE.md: [EXISTS | MISSING]
- WEEKLY_TASK_PLAN.md: [APPROVED | PENDING | MISSING]

---

### Intent Classification

**Primary Intent:** [Architecture Design | Planning | Implementation | Testing | Benchmarking | Documentation | Review | Bug Fix | Optimization]

**Keywords Detected:** [list of relevant keywords]

**Context Clues:**
- Open files: [list]
- Last command used: [if known]
- Task IDs mentioned: [if any]

---

### Contract Validation

- [ ] Architecture approved (required for: Planning, Implementation)
- [ ] Plan approved (required for: Implementation)
- [ ] Task in current WEEKLY_TASK_PLAN.md (required for: Implementation tasks)

**Status:** [✅ VALID | ⛔ VIOLATION]

**Violation Details (if any):**
[Explain what contract is broken and why]

---

### Recommended Command

**Primary Recommendation:**
```
/[command-name] [arguments]
```

**Rationale:**
[Explain why this is the correct command based on:
- Current phase
- User intent
- Project state
- Contract requirements]

**Expected Outcome:**
[What artifact will be produced]

---

### Next Step in Pipeline

After completing the recommended command:
```
/[next-command] [arguments]
```

**Pipeline Sequence:**
[Current Command] → [Next Command] → [Final Command]

---

### Alternative Options

**Option A:** `/[alternative-command-1] [args]`
- **When to use:** [Scenario]
- **Pros:** [Benefits]
- **Cons:** [Drawbacks]

**Option B:** `/[alternative-command-2] [args]`
- **When to use:** [Scenario]
- **Pros:** [Benefits]
- **Cons:** [Drawbacks]

---

### Required Context Files

Before executing the recommended command, ensure these files are loaded in the conversation:

- [ ] `[file1.md]` — [Why needed]
- [ ] `[file2.md]` — [Why needed]
- [ ] `[file3.rs]` — [Why needed]

**Load with:** Use the file browser or `/add` command for each file.

---

### Warnings

**⚠️ Potential Issues:**
[List any concerns, blockers, or dependencies that might affect success]

**🛡️ Quality Gates:**
[Remind about required HOSTILE_REVIEWER approval steps]

---

## Ready to Proceed?

Copy and execute the recommended command above, or ask for clarification if the recommendation doesn't match your intent.
```

---

## CONTRACT VIOLATION RESPONSE

**If MODE 1 detects a violation, output this format:**

```markdown
## WORKFLOW_ROUTER: Contract Violation Detected

### User Request
"[Original request]"

---

### MODE 1: Safety Scanner — ⛔ VIOLATION

**Violation Type:** [Phase Skip | Scope Creep | Architecture Mutation | Missing Prerequisites]

**Details:**
[Explain exactly what contract is broken and why]

**Current State:**
- Phase: [Current phase]
- Gates: GATE_[N]_COMPLETE.md [EXISTS/MISSING]
- Plan: WEEKLY_TASK_PLAN.md [APPROVED/MISSING]

**Required Before Proceeding:**
1. [First prerequisite action with command]
2. [Second prerequisite action with command]
3. [Then original request can be executed]

---

### Recommended Corrective Action

**Step-by-Step Recovery:**
```
# Step 1: [What to do]
/[command-1] [args]

# Step 2: [What to do]
/[command-2] [args]

# Step 3: [Then proceed]
/[original-command] [args]
```

**Rationale:** [Why this sequence is required by the Supreme Rule]

---

### Override Protocol

**Can this be overridden?** [YES/NO]
**Override authority:** [HOSTILE_REVIEWER | HUMAN | NONE]
**Override tag:** `[HUMAN_OVERRIDE]`

[If YES: Explain override process]
[If NO: Explain why this is non-negotiable]

**Recommendation:** [Do NOT override | Override only if...]
```

**HALT:** Do not proceed with MODE 2 or MODE 3 when a violation is detected.

---

## CONSTRAINT INJECTION EXAMPLES

**When generating prompts in MODE 3, inject constraints like this:**

### Example 1: Implementation Task

```markdown
## Constraints

**From ARCHITECTURE.md §3.2.1 (HNSW Insert Algorithm):**
> "All neighbor updates must maintain bidirectional consistency. If A→B is added, B→A must be updated atomically."

**Impact:** Your implementation must update both neighbor lists in a single transaction.

**From DATA_LAYOUT.md (HnswNode structure):**
> "HnswNode size: 16 bytes | Alignment: 8 bytes | Neighbors stored separately via VByte encoding"

**Impact:** Do not modify HnswNode size. Use VectorId references, not inline storage.

**From CLAUDE.md (Rust Standards):**
> "No `unwrap()` in library code. All public APIs must return `Result<T, EdgeVecError>`."

**Impact:** Every function in `src/` must handle errors explicitly.
```

### Example 2: WASM Task

```markdown
## Constraints

**From WASM_BOUNDARY.md (FFI Safety Rules):**
> "No `String` types across boundary. Use `*const u8` with length parameter."

**Impact:** All WASM exports must use C-compatible types.

**From WASM_BOUNDARY.md (Error Handling):**
> "WASM functions must not panic. Use `Result<T, EdgeVecError>` and convert to error codes."

**Impact:** Wrap all operations in `catch_unwind` or ensure no panic paths exist.
```

### Example 3: Testing Task

```markdown
## Constraints

**From TEST_STRATEGY.md ("Nvidia Grade" Standard):**
> "Property tests required for all algorithms. Fuzz targets for all parsers."

**Impact:** This implementation requires:
- Unit tests for individual functions
- Property tests for algorithmic correctness
- Fuzz targets for snapshot loading

**From TEST_STRATEGY.md (Coverage Target):**
> "100% coverage for public API. No untested `pub fn`."

**Impact:** Run `cargo tarpaulin` and ensure all `pub fn` are tested.
```

---

## EXAMPLE OUTPUTS

### Example 1: Architecture Phase Request

**User Request:** "Design the HNSW index structure"

**Output:**
```markdown
## WORKFLOW_ROUTER: Request Analysis

### User Request
"Design the HNSW index structure"

---

### Phase Detection

**Current Phase:** 1 (Architecture)

**Evidence:**
- GATE_1_COMPLETE.md: MISSING
- GATE_2_COMPLETE.md: MISSING
- GATE_3_COMPLETE.md: MISSING
- WEEKLY_TASK_PLAN.md: MISSING

---

### Intent Classification

**Primary Intent:** Architecture Design

**Keywords Detected:** design, HNSW, index, structure

---

### Contract Validation

- [ ] Architecture approved (N/A — we're creating it)
- [ ] Plan approved (N/A — not at this phase)
- [ ] Task in plan (N/A — not at this phase)

**Status:** ✅ VALID

---

### Recommended Command

**Primary Recommendation:**
```
/architect-design hnsw
```

**Rationale:**
- Phase 1 (Architecture) is active
- Request explicitly mentions design
- HNSW is a core component requiring detailed specification
- No architecture exists yet, so we must start here

**Expected Outcome:**
- ARCHITECTURE.md with HNSW component specification
- DATA_LAYOUT.md with struct definitions and sizes
- WASM_BOUNDARY.md if WASM interaction needed

---

### Next Step in Pipeline

After completing architecture design:
```
/review ARCHITECTURE.md
```

**Pipeline Sequence:**
/architect-design hnsw → /review ARCHITECTURE.md → /planner-roadmap

---

### Required Context Files

Before executing the recommended command, ensure these files are loaded:

- [ ] `ASSET_FIT_REPORT.md` — Salvaged code inventory
- [ ] `10_HOSTILE_GATE.md` — Requirements and constraints
- [ ] Any existing `docs/*.md` — Previous design decisions

---

### Warnings

**⚠️ Potential Issues:**
- This is the first major deliverable; expect HOSTILE_REVIEWER scrutiny
- Memory calculations must be precise (include alignment padding)
- WASM constraints must be researched (no assumptions)

**🛡️ Quality Gates:**
- HOSTILE_REVIEWER must approve before proceeding to planning
- All struct sizes must be calculated
- No [UNKNOWN] items can remain without explicit resolution plan
```

---

### Example 2: Implementation Request (Valid)

**User Request:** "Implement W1.1 - HNSW insert function"

**Output:**
```markdown
## WORKFLOW_ROUTER: Request Analysis

### User Request
"Implement W1.1 - HNSW insert function"

---

### Phase Detection

**Current Phase:** 3 (Implementation)

**Evidence:**
- GATE_1_COMPLETE.md: EXISTS
- GATE_2_COMPLETE.md: EXISTS
- GATE_3_COMPLETE.md: EXISTS
- WEEKLY_TASK_PLAN.md: APPROVED (Week 1)

---

### Intent Classification

**Primary Intent:** Implementation

**Keywords Detected:** implement, W1.1 (task ID), HNSW, insert, function

**Task IDs Mentioned:** W1.1

---

### Contract Validation

- [x] Architecture approved (GATE_1_COMPLETE.md exists)
- [x] Plan approved (WEEKLY_TASK_PLAN.md is APPROVED)
- [x] Task W1.1 in current WEEKLY_TASK_PLAN.md

**Status:** ✅ VALID

---

### Recommended Command

**Primary Recommendation:**
```
/rust-implement W1.1
```

**Rationale:**
- Task W1.1 exists in approved WEEKLY_TASK_PLAN.md
- All gates are passed (Architecture → Planning → Coding unlocked)
- Explicit task ID mentioned, unambiguous intent
- RUST_ENGINEER is the correct agent for implementation

**Expected Outcome:**
- `src/hnsw.rs` with `insert()` function
- Unit tests for `insert()`
- Documentation comments

---

### Next Step in Pipeline

After completing implementation:
```
/test-prop W1.1
```

**Pipeline Sequence:**
/rust-implement W1.1 → /test-prop W1.1 → /review W1.1-output → /planner-weekly 2

---

### Required Context Files

Before executing, ensure these files are loaded:

- [x] `WEEKLY_TASK_PLAN.md` — Task details and acceptance criteria
- [x] `ARCHITECTURE.md` — HNSW design specification
- [x] `DATA_LAYOUT.md` — Struct definitions

---

### Warnings

**⚠️ Potential Issues:**
- Ensure acceptance criteria from WEEKLY_TASK_PLAN.md are clear
- Memory layout must match DATA_LAYOUT.md exactly
- No `unsafe` without documented justification

**🛡️ Quality Gates:**
- All tests must pass before submission
- HOSTILE_REVIEWER will check for: panics, unwrap(), magic numbers
- TEST_ENGINEER will verify correctness after implementation
```

---

### Example 3: Contract Violation (Code Without Plan)

**User Request:** "Let's implement the HNSW search algorithm"

**Output:**
```markdown
## WORKFLOW_ROUTER: Request Analysis

### User Request
"Let's implement the HNSW search algorithm"

---

### Phase Detection

**Current Phase:** 2 (Planning)

**Evidence:**
- GATE_1_COMPLETE.md: EXISTS
- GATE_2_COMPLETE.md: MISSING
- GATE_3_COMPLETE.md: MISSING
- WEEKLY_TASK_PLAN.md: MISSING

---

### Intent Classification

**Primary Intent:** Implementation

**Keywords Detected:** implement, HNSW, search, algorithm

---

### Contract Validation

- [x] Architecture approved (GATE_1_COMPLETE.md exists)
- [ ] Plan approved (WEEKLY_TASK_PLAN.md is MISSING)
- [ ] Task in plan (No plan exists)

**Status:** ⛔ VIOLATION — Supreme Rule Broken

**Violation Details:**
The request attempts to write code without an approved plan. This violates the Supreme Rule: "No code without an approved plan."

Current state:
- Architecture: ✅ Approved (GATE_1_COMPLETE.md)
- Planning: ❌ Not started (ROADMAP.md, WEEKLY_TASK_PLAN.md missing)
- Implementation: ⛔ BLOCKED until planning completes

---

### Recommended Command

**You CANNOT implement yet. First, create a plan:**

**Step 1:** Create roadmap
```
/planner-roadmap
```

**Step 2:** Get roadmap approved
```
/review ROADMAP.md
```

**Step 3:** Create weekly plan
```
/planner-weekly 1
```

**Step 4:** Get weekly plan approved
```
/review WEEKLY_TASK_PLAN.md
```

**Step 5:** THEN implement
```
/rust-implement W1.[X]
```

**Rationale:**
The Supreme Rule requires: Architecture > Plan > Code

You've completed Architecture (✅), but have not completed Planning (❌).

---

### Required Actions Before Implementation

**BLOCKING TASKS:**
1. ⛔ Create ROADMAP.md via PLANNER
2. ⛔ Get ROADMAP.md approved by HOSTILE_REVIEWER
3. ⛔ Create WEEKLY_TASK_PLAN.md via PLANNER
4. ⛔ Get WEEKLY_TASK_PLAN.md approved by HOSTILE_REVIEWER

**THEN:** You may implement tasks listed in WEEKLY_TASK_PLAN.md

---

### Alternative Options

**Option A:** Fast-track to planning (if architecture is solid)
```
/planner-roadmap
```
- Creates full 6-month roadmap
- Decomposes architecture into tasks
- Identifies dependencies and critical path

**Option B:** Skip straight to weekly planning (if scope is small)
```
/planner-weekly 1
```
- Creates first week's tasks directly
- Faster but less strategic
- Only recommended for small projects

---

### Warnings

**⚠️ Why This Matters:**
Coding without a plan leads to:
- Scope creep (implementing undefined features)
- Missing dependencies (building wrong order)
- Wasted effort (implementing wrong approach)
- Failed reviews (HOSTILE_REVIEWER rejects unplanned work)

**🛡️ Quality Gates:**
HOSTILE_REVIEWER will automatically REJECT any code submitted without an approved WEEKLY_TASK_PLAN.md reference.
```

---

## ANTI-HALLUCINATION RULES

When generating dispatch recommendations:

1. **No Invented Phase Status**
   - Only report phase based on actual file existence
   - Check: GATE_1_COMPLETE.md, GATE_2_COMPLETE.md, GATE_3_COMPLETE.md

2. **No Invented Task IDs**
   - If user mentions W1.1, verify it exists in WEEKLY_TASK_PLAN.md
   - If no task ID mentioned and code is requested, require plan first

3. **No Optimistic Contract Validation**
   - If architecture doesn't exist, status is VIOLATION (not "probably fine")
   - If plan doesn't exist, block implementation (no shortcuts)

4. **No Vague Recommendations**
   - Always specify exact command with arguments
   - Always explain why this is the correct command
   - Always state the expected outcome

---

## INVOCATION

**Trigger:** `/dispatch`

**No arguments required.** The dispatcher analyzes the conversation context automatically.

---

*Command Version: 1.0.0*
*Project: EdgeVec*
*Purpose: Workflow Dispatch & Contract Enforcement*
