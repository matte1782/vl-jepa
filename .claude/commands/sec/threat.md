---
description: Create threat model for the system
---

# /sec:threat — Threat Model

Create a comprehensive threat model using STRIDE methodology.

## Usage

```
/sec:threat
/sec:threat $ARGUMENTS  # Focus on specific component
```

## Protocol

### Step 1: Load Context

Read:
- `docs/architecture/ARCHITECTURE.md`
- `docs/PRD.md` (if exists)

### Step 2: Invoke SECURITY_LEAD

Create `docs/THREAT_MODEL.md`:

```markdown
# VL-JEPA Threat Model

**Date:** YYYY-MM-DD
**Author:** SECURITY_LEAD
**Scope:** Full system

---

## 1. System Overview

[Brief description + data flow diagram]

## 2. Assets

| Asset | Sensitivity | Location |
|-------|-------------|----------|
| Lecture videos | HIGH | Local disk |
| Embeddings | MEDIUM | Local DB |
| User queries | LOW | Memory |
| Model weights | MEDIUM | Local disk |

## 3. Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| Malicious file | LOW | Exploit via video |
| Local attacker | MEDIUM | Data theft |
| Insider | HIGH | Privacy violation |

## 4. STRIDE Analysis

### Spoofing
- **Threat:** [Description]
- **Mitigation:** [Control]

### Tampering
- **Threat:** [Description]
- **Mitigation:** [Control]

### Repudiation
- **Threat:** [Description]
- **Mitigation:** [Control]

### Information Disclosure
- **Threat:** [Description]
- **Mitigation:** [Control]

### Denial of Service
- **Threat:** [Description]
- **Mitigation:** [Control]

### Elevation of Privilege
- **Threat:** [Description]
- **Mitigation:** [Control]

## 5. Attack Surface

| Surface | Vectors | Risk | Mitigation |
|---------|---------|------|------------|
| Video input | Malicious file | MEDIUM | Sandboxed decode |
| Model loading | Pickle exploit | HIGH | Safe loading |

## 6. Privacy Considerations

- Local-only processing by default
- No network calls without consent
- User controls data retention

## 7. Security Controls

| Control | Purpose | Status |
|---------|---------|--------|
| Input validation | Prevent injection | TODO |
| Secure model loading | Prevent RCE | TODO |
```

### Step 3: Handoff

```markdown
## SECURITY_LEAD: Threat Model Complete

Artifact: docs/THREAT_MODEL.md
Threats Identified: N
Mitigations Defined: M

Status: READY_FOR_REVIEW

Next: /review:hostile docs/THREAT_MODEL.md
```

## Arguments

- `$ARGUMENTS` — Optional component focus

## Output

- `docs/THREAT_MODEL.md`
