---
description: Run pre-release validation checklist
---

# /release:checklist — Release Checklist

Validate release readiness with comprehensive checklist.

## Usage

```
/release:checklist
/release:checklist $ARGUMENTS  # Version number
```

## Protocol

### Step 1: Verify Gates

```bash
# All gates must be complete
for i in $(seq 1 6); do
  if [ ! -f ".claude/gates/GATE_${i}_COMPLETE.md" ]; then
    echo "ERROR: Gate $i not complete"
    exit 1
  fi
done
```

### Step 2: Run Checklist

```markdown
# Release Checklist: v$VERSION

**Date:** YYYY-MM-DD
**Author:** DEVOPS

---

## Code Quality

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage >90%: `pytest --cov`
- [ ] Type check clean: `mypy src/ --strict`
- [ ] Lint clean: `ruff check src/`
- [ ] No TODO/FIXME without issue

## Documentation

- [ ] README.md up to date
- [ ] CHANGELOG.md updated
- [ ] API docs generated
- [ ] All examples tested

## Security

- [ ] No secrets in code
- [ ] Dependencies audited: `pip-audit`
- [ ] Threat model reviewed

## Git

- [ ] All changes committed
- [ ] Branch is clean
- [ ] Version bumped in pyproject.toml

## Build

- [ ] Package builds: `python -m build`
- [ ] Wheel installs correctly
- [ ] Entry points work

## Pre-Release

- [ ] Test install in fresh venv
- [ ] Smoke test core functionality
- [ ] Performance baseline met
```

### Step 3: Run Automated Checks

```bash
# Tests
pytest tests/ -v --cov=src/vl_jepa

# Type check
mypy src/ --strict

# Lint
ruff check src/

# Security audit
pip-audit

# Build
python -m build
```

### Step 4: Document Results

```markdown
## Release Validation: v$VERSION

### Automated Checks
| Check | Status | Details |
|-------|--------|---------|
| Tests | ✅ PASS | 142/142 |
| Coverage | ✅ PASS | 94% |
| Types | ✅ PASS | Clean |
| Lint | ✅ PASS | Clean |
| Security | ✅ PASS | No vulns |
| Build | ✅ PASS | Wheel OK |

### Manual Checks
- [x] README reviewed
- [x] CHANGELOG updated
- [x] Examples work

### Verdict

✅ READY FOR RELEASE
```

### Step 5: Handoff

```markdown
## DEVOPS: Release Checklist Complete

Version: $VERSION
All Checks: ✅ PASS

Ready: YES

Next Steps:
1. git tag v$VERSION
2. git push --tags
3. python -m twine upload dist/*
```

## Arguments

- `$ARGUMENTS` — Optional version number (defaults to current)

## Output

- Release validation report
- Ready/not ready verdict
