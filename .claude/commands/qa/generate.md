---
description: Generate test stubs for a module
---

# /qa:generate — Generate Tests

Generate test stubs for a specific module based on specifications.

## Usage

```
/qa:generate $ARGUMENTS
```

Where `$ARGUMENTS` is the module name (e.g., "encoder", "event")

## Protocol

### Step 1: Find Specifications

```bash
# Find relevant specs
grep -r "S00" docs/SPECIFICATION.md
grep -r "S00" docs/architecture/
```

### Step 2: Generate Test File

Invoke **QA_LEAD** agent to create test stubs:

```python
# tests/unit/test_{module}.py

"""
Tests for {module} module.

SPEC: S00X
"""

import pytest
import torch
from hypothesis import given, strategies as st

from vl_jepa.{module} import {Class}


class Test{Class}:
    """Tests for {Class}."""

    @pytest.mark.skip(reason="Stub - implement with S00X")
    def test_basic_functionality(self) -> None:
        """
        SPEC: S00X
        TEST_ID: T00X.1

        [Description of what this tests]
        """
        # Arrange
        instance = {Class}()
        input_data = ...

        # Act
        result = instance.method(input_data)

        # Assert
        assert result == expected

    @pytest.mark.skip(reason="Stub - implement with S00X")
    def test_edge_case_empty(self) -> None:
        """
        SPEC: S00X
        TEST_ID: T00X.2

        Test behavior with empty input.
        """
        instance = {Class}()
        with pytest.raises(ValueError):
            instance.method([])

    @pytest.mark.skip(reason="Stub - implement with S00X")
    def test_edge_case_invalid_type(self) -> None:
        """
        SPEC: S00X
        TEST_ID: T00X.3

        Test behavior with invalid input type.
        """
        instance = {Class}()
        with pytest.raises(TypeError):
            instance.method("invalid")


class Test{Class}Properties:
    """Property-based tests for {Class}."""

    @pytest.mark.skip(reason="Stub - implement with S00X")
    @given(size=st.integers(min_value=1, max_value=10))
    def test_output_size_matches_input(self, size: int) -> None:
        """
        SPEC: S00X
        TEST_ID: T00X.4

        Property: Output batch size equals input batch size.
        """
        instance = {Class}()
        input_data = torch.randn(size, 3, 224, 224)
        result = instance.method(input_data)
        assert result.shape[0] == size
```

### Step 3: Update Test Matrix

Update `docs/TEST_MATRIX.md` with new test IDs.

### Step 4: Handoff

```markdown
## QA_LEAD: Tests Generated

Module: {module}
Stubs Created: N
Test IDs: T00X.1 - T00X.N

File: tests/unit/test_{module}.py

Next: /ml:implement WN.X (after plan approval)
```

## Arguments

- `$ARGUMENTS` — Module name (required, e.g., "encoder")

## Output

- `tests/unit/test_{module}.py` with stubs
- Updated `docs/TEST_MATRIX.md`
