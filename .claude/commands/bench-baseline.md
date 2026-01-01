Execute the BENCHMARK_SCIENTIST workflow for establishing baseline performance metrics.

**Task:** Establish baseline metrics for $ARGUMENTS

## Pre-Benchmark Verification

Before running benchmarks:

1. [ ] Code is implemented and compiles
2. [ ] Tests pass (`cargo test`)
3. [ ] `docs/architecture/ARCHITECTURE.md` exists (performance budget reference)
4. [ ] Hardware specification is documented

## Required Context Files

Ensure these files are loaded:
- `docs/architecture/ARCHITECTURE.md` — Performance budget reference
- `Cargo.toml` — Verify benchmark dependencies (criterion)

Use `/add-file` to load these if needed.

## Workflow Steps

### Step 1: Benchmark Design
- Define what metrics to measure (latency P50/P99, throughput, memory)
- Define test parameters (vector counts, dimensions, k values)
- Document expected scaling behavior

### Step 2: Implement Benchmark Code
- Create benchmark in `benches/[component]_bench.rs`
- Use deterministic seeded RNG (seed=42)
- Follow benchmark template from agent definition
- Include both latency and throughput measurements

### Step 3: Memory Profiling (if applicable)
- Create memory profiling example in `examples/memory_profile.rs`
- Use tracking allocator pattern
- Measure bytes per vector at multiple scales

### Step 4: Run Benchmarks
```bash
cargo bench --bench [component]_bench
cargo run --release --example memory_profile
```

### Step 5: Baseline Report
- Generate baseline report in `docs/benchmarks/baseline_[component]_[date].md`
- Document hardware specification
- Document commit hash
- Include reproducibility instructions

### Step 6: Handoff
```markdown
## BENCHMARK_SCIENTIST: Baseline Complete

Component: [component]
Report: `docs/benchmarks/baseline_[component]_[date].md`

Summary:
- [Metric 1]: [Value] ✅/❌
- [Metric 2]: [Value] ✅/❌
- [Metric 3]: [Value] ✅/❌

Status: PENDING_HOSTILE_REVIEW

Next: Run /review docs/benchmarks/baseline_[component]_[date].md
```

## Anti-Hallucination Clamps

- NO benchmark report without hardware specification
- NO results without commit hash
- NO single-run results (minimum 3 runs)
- NO cherry-picked metrics (report P50 AND P99)

---

**Agent:** BENCHMARK_SCIENTIST
**Version:** 2.0.0
