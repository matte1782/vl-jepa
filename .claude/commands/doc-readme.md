Execute the DOCWRITER workflow for creating the main README.md (the viral hook).

**Task:** Generate/update README.md with viral design

## Pre-Documentation Verification

Before writing README:

1. [ ] Code is implemented and tested
2. [ ] Benchmark results exist
3. [ ] API is stable
4. [ ] WASM compatibility is verified

## Required Context Files

Ensure these files are loaded:
- `docs/architecture/ARCHITECTURE.md` — Technical overview
- `docs/benchmarks/baseline_[component]_[date].md` — Performance metrics
- `src/lib.rs` — Public API to document
- `Cargo.toml` — Version, dependencies

Use `/add-file` to load these if needed.

## Workflow Steps

### Step 1: Audience Analysis
```markdown
## Target Audience

| Persona | Goal | Time Budget |
|:--------|:-----|:------------|
| Evaluator | "Is this worth using?" | 30 seconds |
| Starter | "How do I get this running?" | 10 minutes |
| Integrator | "How do I use this API?" | 30 minutes |
```

### Step 2: Content Structure

**README.md Structure:**
1. **Hero Section** (30 seconds)
   - Project name + tagline
   - Badges (npm, crates.io, license)
   - Links to demo, docs, benchmarks

2. **Why EdgeVec?** (Feature comparison table)
   - EdgeVec vs sqlite-vec vs FAISS
   - Highlight unique advantages (WASM, npm install, persistence)

3. **Quick Start** (10 minutes)
   - Browser/Node.js example (copy-paste ready)
   - Rust example (copy-paste ready)
   - Show actual output

4. **Performance** (Benchmark summary table)
   - Reference actual benchmark results
   - Include hardware spec

5. **Browser Compatibility** (Compatibility matrix)
   - Chrome, Firefox, Safari, Edge versions
   - Note about SharedArrayBuffer

6. **Documentation Links**
   - Getting Started, API, Architecture, Benchmarks, FAQ

7. **Contributing, License, Footer**

### Step 3: Example Verification

**CRITICAL:** Every code example must:
- Be extracted from working test files
- Work when copy-pasted
- Show expected output
- Be tested in CI

```bash
# Verify examples compile and run
cargo test --doc
npm test -- --grep "readme"
```

### Step 4: Write README.md

Follow the template from agent definition (`agents/docwriter.md`).

**Key Requirements:**
- Use actual benchmark numbers (no invention)
- Reference exact versions
- Include commit hash for reproducibility
- Make comparison tables fair (document methodology differences)

### Step 5: Link Verification

Verify ALL links work:
- [ ] Demo link (if exists)
- [ ] Documentation links
- [ ] Benchmark links
- [ ] GitHub/npm/crates.io links

### Step 6: Accuracy Check

Cross-verify against actual code:
- [ ] API examples match implementation
- [ ] Performance claims match benchmark reports
- [ ] Browser compatibility matches WASM testing
- [ ] Installation instructions work

### Step 7: Handoff

```markdown
## DOCWRITER: README Complete

File: `README.md`

Verification:
- [x] All examples tested and work when copy-pasted
- [x] All links verified
- [x] Performance claims match benchmark report X
- [x] API examples match implementation

Status: PENDING_HOSTILE_REVIEW

Next: Run /review README.md
```

## Anti-Hallucination Clamps

- NO untested examples (must extract from working tests)
- NO unverified performance claims (must reference benchmark reports)
- NO outdated information (must reference exact versions)
- NO broken links
- NO unfair comparisons (document methodology differences)

## Progressive Enhancement

**Minimum Viable README (v0.1.0):**
- Hero section with tagline
- Basic quick start (one example)
- Performance table (even if preliminary)
- Installation instructions

**Enhanced README (v0.2.0+):**
- Comparison table vs competitors
- Live demo link
- Full browser compatibility matrix
- Multiple examples (Rust + JS)

---

**Agent:** DOCWRITER
**Version:** 2.0.0
