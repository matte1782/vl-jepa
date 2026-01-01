# VL-JEPA Agentic Framework — Quickstart Guide

> **Framework Version:** 1.0.0
> **Created:** 2024-12-30
> **Project:** Event-Aware Lecture Summarizer

---

## 1. Quickstart Sequence

Start a new project session with these commands:

```bash
# Step 1: Check current gate status
ls .claude/gates/

# Step 2: Current status shows Gate 0 complete
# Proceed with Gate 1: Architecture

# Step 3: Design architecture
/arch:design

# Step 4: Review architecture (hostile review)
/review:hostile docs/architecture/ARCHITECTURE.md

# Step 5: After approval, create test strategy
/qa:testplan

# Step 6: Create roadmap
/plan:roadmap

# Step 7: Create weekly plan
/plan:weekly 1

# Step 8: Implement with TDD
/ml:implement W1.1

# Step 9: Continue through all tasks...

# Step 10: Final validation
/review:hostile --comprehensive

# Step 11: Release
/release:checklist
```

**Or run the full pipeline:**
```bash
/pipeline:all
```

---

## 2. Commands by Role

### Executive Layer

| Command | Purpose | Agent |
|---------|---------|-------|
| `/pm:prd` | Create Product Requirements | PM |
| `/research:scan TOPIC` | Literature review | RESEARCH_LEAD |

### Architecture Layer

| Command | Purpose | Agent |
|---------|---------|-------|
| `/arch:design` | System architecture | ARCHITECT |
| `/arch:adr TITLE` | Decision record | ARCHITECT |

### Planning Layer

| Command | Purpose | Agent |
|---------|---------|-------|
| `/plan:roadmap` | Development roadmap | PLANNER |
| `/plan:weekly N` | Weekly task plan | PLANNER |

### Engineering Layer

| Command | Purpose | Agent |
|---------|---------|-------|
| `/ml:implement TASK` | TDD implementation | ML_ENGINEER |
| `/qa:testplan` | Test strategy | QA_LEAD |
| `/qa:generate MODULE` | Generate test stubs | QA_LEAD |

### Security & Ops Layer

| Command | Purpose | Agent |
|---------|---------|-------|
| `/sec:threat` | Threat model | SECURITY_LEAD |
| `/docs:write TOPIC` | Documentation | DOCS_WRITER |
| `/release:checklist` | Release validation | DEVOPS |

### Quality Gate

| Command | Purpose | Agent |
|---------|---------|-------|
| `/review:hostile ARTIFACT` | Adversarial review | HOSTILE_REVIEWER |
| `/pipeline:all` | Full lifecycle | ORCHESTRATOR |

---

## 3. Full Pipeline Command

The `/pipeline:all` command orchestrates the entire lifecycle:

```
/pipeline:all

Options:
  --from N     Start from gate N
  --to N       Stop at gate N
  --dry-run    Show plan without executing
```

**Pipeline Flow:**
```
Gate 0 → Gate 1 → Gate 2 → Gate 3 → Gate 4 → Gate 5 → Gate 6 → Gate 7
Problem   Arch     Spec     Tests    Plan     Impl     Valid    Release
```

---

## 4. Generated Framework Structure

```
vl-jepa/
├── CLAUDE.md                    # Project DNA (main instructions)
├── project_brief.md             # Original requirements
├── .claude/
│   ├── settings.json            # Permissions & hooks
│   ├── agents/                  # 10 specialized agents
│   │   ├── architect.md
│   │   ├── planner.md
│   │   ├── ml-engineer.md
│   │   ├── qa-lead.md
│   │   ├── research-lead.md
│   │   ├── security-lead.md
│   │   ├── devops.md
│   │   ├── docs-writer.md
│   │   ├── orchestrator.md
│   │   └── hostile-reviewer.md  # KILL AUTHORITY
│   ├── commands/                # 14 slash commands
│   │   ├── pm/prd.md
│   │   ├── arch/design.md, adr.md
│   │   ├── plan/roadmap.md, weekly.md
│   │   ├── ml/implement.md
│   │   ├── qa/testplan.md, generate.md
│   │   ├── sec/threat.md
│   │   ├── docs/write.md
│   │   ├── review/hostile.md
│   │   ├── release/checklist.md
│   │   ├── research/scan.md
│   │   └── pipeline/all.md
│   ├── rules/                   # Coding standards
│   │   ├── python.md
│   │   ├── testing.md
│   │   └── ml.md
│   └── gates/                   # Gate completion markers
│       └── GATE_0_COMPLETE.md
└── docs/
    ├── QUALITY_GATES.md         # Gate system documentation
    ├── architecture/            # Design docs (Gate 1)
    ├── planning/                # Roadmaps (Gate 4)
    ├── research/                # Literature (Gate 0)
    ├── reviews/                 # Hostile reviews
    └── ADR/                     # Decision records
```

---

## 5. TODOs Requiring Human Decisions

### Immediate

1. **VL-JEPA vs V-JEPA Decision**
   - VL-JEPA weights may not be publicly available
   - Decide: Wait for release or use V-JEPA approximation?
   - Impact: Architecture design

2. **Hardware Target**
   - Primary: GPU or CPU?
   - Impact: Performance targets, batch sizes

3. **Data Sources**
   - Which lecture recordings to use for testing?
   - Privacy/licensing considerations

### Before Gate 1

4. **Encoder Selection**
   - ViT-L/16 (larger, more accurate) vs ViT-B/16 (smaller, faster)?
   - Create ADR with `/arch:adr "Encoder Selection"`

5. **Text Encoder**
   - all-MiniLM-L6-v2 vs alternatives?
   - Evaluate embedding compatibility

### Before Gate 5

6. **Test Data**
   - Acquire or create test lecture videos
   - Ensure proper licensing

7. **Evaluation Protocol**
   - Manual annotations for event detection ground truth
   - Question-answer pairs for retrieval evaluation

---

## 6. Session Start Protocol

Every development session:

```bash
# 1. Check gate status
ls .claude/gates/

# 2. Identify current gate (lowest incomplete)
# Gate 0: COMPLETE ✓
# Gate 1: Next

# 3. Run appropriate command for current gate
/arch:design   # If Gate 1
/qa:testplan   # If Gate 3
/plan:roadmap  # If Gate 4
# etc.

# 4. After completing work, submit for review
/review:hostile <artifact>
```

---

## 7. Quality Standards Summary

| Standard | Target | Check |
|----------|--------|-------|
| Test Coverage | >90% | `pytest --cov` |
| Type Safety | 100% | `mypy --strict` |
| Lint | 0 warnings | `ruff check` |
| Frame Latency | <200ms (CPU) | Benchmark |
| Query Latency | <100ms | Benchmark |

---

## 8. Emergency Procedures

### If Hostile Review Fails

1. Read rejection document completely
2. Address ALL critical issues first
3. Address ALL major issues
4. Update artifact with changes
5. Resubmit: `/review:hostile <artifact>`

### If Stuck

1. Check gate status: `ls .claude/gates/`
2. Read CLAUDE.md for workflow
3. Use `/pipeline:all --dry-run` to see next steps
4. Ask for help with specific gate

---

*Framework created by Agentic Engineering Environment v1.0.0*
*FORTRESS 2.0 — Design > Code. Validation > Speed. Correctness > Convenience.*
