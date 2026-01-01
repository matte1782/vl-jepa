Execute the DOCWRITER workflow for creating complete API reference documentation.

**Task:** Generate API documentation for $ARGUMENTS

## Pre-Documentation Verification

Before writing API docs:

1. [ ] Module is implemented: $ARGUMENTS
2. [ ] Public API is stable
3. [ ] Tests exist for all public functions
4. [ ] Code has docstring comments (`///`)

## Required Context Files

Ensure these files are loaded:
- `src/$ARGUMENTS.rs` — Module to document (or src/lib.rs for full API)
- `tests/**/*_test.rs` — Test files for examples
- `docs/architecture/ARCHITECTURE.md` — Context

Use `/add-file` to load these if needed.

## Workflow Steps

### Step 1: API Inventory

Enumerate ALL public items in the module:
```markdown
## API Inventory: $ARGUMENTS

### Public Structs
- [ ] `StructName` — [Brief description]

### Public Functions
- [ ] `function_name()` — [Brief description]

### Public Types
- [ ] `TypeName` — [Brief description]

### Public Errors
- [ ] `ErrorVariant` — [Brief description]
```

### Step 2: Documentation Template

For EACH public item, create documentation following this template:

**Struct:**
```markdown
## StructName

[One-line description]

### Fields
| Name | Type | Description |
|:-----|:-----|:------------|
| `field1` | `Type` | [Description] |

### Methods
- [`new()`](#structname-new) — [Description]
- [`method()`](#structname-method) — [Description]

### Example
```[language]
[Working, copy-paste ready example extracted from tests]
```
```

**Function:**
```markdown
## function_name()

```typescript
function_name(param1: Type1, param2: Type2): ReturnType
```

[Detailed description]

**Parameters:**
| Name | Type | Description |
|:-----|:-----|:------------|
| `param1` | `Type1` | [Description] |
| `param2` | `Type2` | [Description] |

**Returns:**
`ReturnType` — [Description]

**Throws/Errors:**
- `ErrorType` if [condition]

**Example:**
```[language]
[Working, copy-paste ready example extracted from tests]
```

**Performance:**
- Time complexity: O(?)
- Space complexity: O(?)
```

**Error Enum:**
```markdown
## ErrorName

[Description of error type]

### Variants

#### ErrorVariant1
```
ErrorMessage
```
**Cause:** [What causes this error]
**Example:**
```[language]
[Example that triggers this error]
```
```

### Step 3: Extract Examples from Tests

**CRITICAL:** Do NOT invent examples. Extract them from actual test files:

```bash
# Find test functions for the module
rg "fn test_.*$ARGUMENTS" tests/
```

For each documented function:
1. Find corresponding test
2. Extract minimal working example
3. Verify it compiles and runs
4. Include expected output

### Step 4: Generate API Document

Create `docs/API.md` or `docs/api/$ARGUMENTS.md`:

```markdown
# EdgeVec API Reference — $ARGUMENTS

**Version:** [from Cargo.toml]
**Module:** $ARGUMENTS

## Table of Contents

[Auto-generated TOC]

---

[Documentation for each public item following templates above]

---

## Complete Example

[Full working example using multiple API items together]

---

## See Also

- [Architecture Overview](ARCHITECTURE.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [Benchmarks](BENCHMARKS.md)
```

### Step 5: Verification

**Example Test:**
```bash
# Extract all examples from API docs
sed -n '/```rust/,/```/p' docs/api/$ARGUMENTS.md > /tmp/api_examples.rs

# Verify they compile (if Rust)
rustc --test /tmp/api_examples.rs
```

**Link Verification:**
- [ ] All internal cross-references work
- [ ] All anchor links (#section) work
- [ ] All external links are valid

**Accuracy Check:**
- [ ] Function signatures match implementation
- [ ] Error descriptions match actual error messages
- [ ] Performance characteristics are documented (if benchmarked)

### Step 6: Handoff

```markdown
## DOCWRITER: API Documentation Complete

Module: $ARGUMENTS
File: `docs/api/$ARGUMENTS.md` (or `docs/API.md` for full API)

Coverage:
- Public structs: [N] documented
- Public functions: [N] documented
- Public types: [N] documented
- Public errors: [N] documented

Verification:
- [x] All examples extracted from tests
- [x] All examples compile and run
- [x] All links verified
- [x] Signatures match implementation

Status: PENDING_HOSTILE_REVIEW

Next: Run /review docs/api/$ARGUMENTS.md
```

## Anti-Hallucination Clamps

- NO invented examples (must extract from actual tests)
- NO undocumented public functions
- NO incorrect function signatures
- NO broken internal links
- NO unverified performance claims

## TypeScript Bindings (for WASM)

If documenting WASM-exported API:
1. Document both Rust and TypeScript signatures
2. Document JavaScript usage patterns
3. Document browser-specific considerations
4. Include WASM initialization example

```typescript
// WASM-specific documentation
import init, { EdgeVecIndex } from 'edgevec';

// Initialize WASM module
await init();

// Now use the API
const index = new EdgeVecIndex(128);
```

---

**Agent:** DOCWRITER
**Version:** 2.0.0
