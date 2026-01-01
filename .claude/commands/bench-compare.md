Execute the BENCHMARK_SCIENTIST workflow for comparing EdgeVec performance against a competitor.

**Task:** Compare EdgeVec vs $ARGUMENTS

## Pre-Comparison Verification

Before comparing:

1. [ ] EdgeVec baseline exists
2. [ ] Competitor is specified: $ARGUMENTS
3. [ ] Fair comparison methodology is defined
4. [ ] Both systems will use same hardware, dataset, and parameters

## Required Context Files

Ensure these files are loaded:
- `docs/benchmarks/baseline_[component]_[date].md` — EdgeVec baseline
- `docs/architecture/ARCHITECTURE.md` — Performance targets

Use `/add-file` to load these if needed.

## Workflow Steps

### Step 1: Comparison Design
```markdown
## Comparison Design: EdgeVec vs [Competitor]

### Fair Comparison Criteria
- [ ] Same hardware
- [ ] Same dataset (specify: ANN-Benchmarks SIFT-1M, etc.)
- [ ] Same k value
- [ ] Same recall target (~0.95)
- [ ] Document ALL methodology differences

### Metrics to Compare
- Search latency (P50, P99)
- Memory per vector
- Insert throughput
- Bundle size (for WASM)
- Persistence support
```

### Step 2: Competitor Setup
- Document competitor version
- Document installation/build steps
- Document configuration (to match EdgeVec settings)

### Step 3: Run Comparative Benchmarks
```bash
# EdgeVec
cargo bench --bench [component]_bench

# Competitor (document exact commands)
[competitor commands]
```

### Step 4: Comparison Report
Generate comparison report in `docs/benchmarks/comparison_[competitor]_[date].md`:
- Side-by-side metrics table
- Percentage differences
- Fair comparison checklist
- Methodology differences section
- Reproducibility instructions for BOTH systems

### Step 5: Handoff
```markdown
## BENCHMARK_SCIENTIST: Comparison Complete

Competitor: [name]
Report: `docs/benchmarks/comparison_[competitor]_[date].md`

Summary:
| Metric | EdgeVec | [Competitor] | Δ |
|:-------|:--------|:-------------|:--|
| P50 latency | X ms | Y ms | ±Z% |
| Memory/vec | X B | Y B | ±Z% |

Fair Comparison: [YES/NO - explain if NO]

Status: PENDING_HOSTILE_REVIEW

Next: Run /review docs/benchmarks/comparison_[competitor]_[date].md
```

## Anti-Hallucination Clamps

- NO unfair comparisons (different hardware, different datasets)
- NO undocumented methodology differences
- NO cherry-picked metrics
- NO misleading percentage calculations

---

**Agent:** BENCHMARK_SCIENTIST
**Version:** 2.0.0
