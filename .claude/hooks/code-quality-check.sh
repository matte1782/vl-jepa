#!/bin/bash
# Reddit-style problem detection script
# Catches issues like those identified by Reddit user chillfish8
# Run: bash .claude/hooks/code-quality-check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== EdgeVec Code Quality Check ==="
echo "Project: $PROJECT_ROOT"
echo ""

ERRORS=0

# 1. Comment Quality Check - No rambling internal monologue
echo "=== [1/5] Comment Quality Check ==="
RAMBLING=$(grep -rn "Actually,\|Better fix:\|No, silence\|Let's just assume\|But strictly\|Best effort:" "$PROJECT_ROOT/src/" 2>/dev/null || true)
if [ -n "$RAMBLING" ]; then
    echo "ERROR: Rambling/unprofessional comments detected:"
    echo "$RAMBLING"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No rambling comments found"
fi
echo ""

# 2. Code Duplication Check - Popcount implementations
echo "=== [2/5] Popcount Duplication Check ==="
POPCOUNT_FILES=$(grep -l "count_ones\|popcount" "$PROJECT_ROOT/src/"**/*.rs 2>/dev/null | wc -l || echo "0")
if [ "$POPCOUNT_FILES" -gt 5 ]; then
    echo "WARNING: Popcount logic found in $POPCOUNT_FILES files (consider consolidation)"
    grep -l "count_ones\|popcount" "$PROJECT_ROOT/src/"**/*.rs 2>/dev/null | head -8
else
    echo "PASS: Popcount implementations appear consolidated ($POPCOUNT_FILES files)"
fi
echo ""

# 3. Safety Documentation Check - SAFETY docs should be on functions, not inside
echo "=== [3/5] Safety Doc Placement Check ==="
INLINE_SAFETY=$(grep -rn "// SAFETY:" "$PROJECT_ROOT/src/" 2>/dev/null | grep -v "/// # Safety" | grep -v "//! # Safety" || true)
if [ -n "$INLINE_SAFETY" ]; then
    COUNT=$(echo "$INLINE_SAFETY" | wc -l)
    echo "INFO: Found $COUNT inline SAFETY comments (consider moving to doc comments):"
    echo "$INLINE_SAFETY" | head -5
else
    echo "PASS: Safety documentation properly placed in doc comments"
fi
echo ""

# 4. Lookup Table SIMD Check - Should use native instructions when available
echo "=== [4/5] SIMD Optimization Check ==="
LOOKUP_SIMD=$(grep -rn "setr_epi8.*popcount\|lookup.*nibble\|lookup table.*popcount" "$PROJECT_ROOT/src/" 2>/dev/null || true)
if [ -n "$LOOKUP_SIMD" ]; then
    echo "WARNING: Lookup table SIMD detected (consider native instructions):"
    echo "$LOOKUP_SIMD"
else
    echo "PASS: No suboptimal lookup table SIMD patterns found"
fi
echo ""

# 5. HTML Duplicate Check
echo "=== [5/5] HTML Duplicate Check ==="
if [ -d "$PROJECT_ROOT/wasm/examples" ]; then
    HTML_COUNT=$(ls "$PROJECT_ROOT/wasm/examples/"*.html 2>/dev/null | wc -l || echo "0")
    echo "Found $HTML_COUNT HTML files in wasm/examples/"

    # Check for obvious duplicates (v060_demo.html vs v060_cyberpunk_demo.html pattern)
    if [ -f "$PROJECT_ROOT/wasm/examples/v060_demo.html" ] && [ -f "$PROJECT_ROOT/wasm/examples/v060_cyberpunk_demo.html" ]; then
        echo "WARNING: Potential duplicate demos detected (v060_demo.html & v060_cyberpunk_demo.html)"
        ERRORS=$((ERRORS + 1))
    else
        echo "PASS: No obvious HTML duplicates"
    fi
else
    echo "SKIP: wasm/examples directory not found"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ $ERRORS -gt 0 ]; then
    echo "FAILED: $ERRORS issue(s) require attention"
    exit 1
else
    echo "PASSED: All Reddit-style checks passed"
    exit 0
fi
