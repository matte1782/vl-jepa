---
paths: "tests/**/*.py"
---

# Testing Standards

Rules for all test code.

## Test Structure

Use pytest with clear naming:

```python
class TestEncoder:
    """Tests for Encoder class."""

    def test_encode_returns_correct_shape(self) -> None:
        """Test that encode returns expected tensor shape."""
        # Arrange
        encoder = Encoder()
        frames = torch.randn(4, 3, 224, 224)

        # Act
        result = encoder.encode(frames)

        # Assert
        assert result.shape == (4, 768)
```

## Test Naming

- `test_[method]_[scenario]_[expected]`
- Examples:
  - `test_encode_batch_returns_correct_shape`
  - `test_encode_empty_raises_value_error`
  - `test_detect_events_single_frame_returns_empty`

## Required Test Types

### Unit Tests (tests/unit/)
- One test file per module
- Mock external dependencies
- Target: >90% coverage

### Integration Tests (tests/integration/)
- Test component interactions
- Use real (local) dependencies
- Focus on critical paths

### Property Tests (tests/property/)
- Use hypothesis for invariants:

```python
from hypothesis import given, strategies as st

@given(batch_size=st.integers(1, 8))
def test_output_preserves_batch(self, batch_size: int) -> None:
    frames = torch.randn(batch_size, 3, 224, 224)
    result = encoder.encode(frames)
    assert result.shape[0] == batch_size
```

## Test Traceability

Every test MUST reference spec:

```python
def test_encode_shape(self) -> None:
    """
    SPEC: S001
    TEST_ID: T001.1

    Verify encode returns correct shape.
    """
```

## Edge Cases Checklist

Every module should test:
- [ ] Empty input
- [ ] Single item
- [ ] Maximum size
- [ ] Invalid type
- [ ] Boundary values

## Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/vl_jepa --cov-report=term

# Run property tests
pytest tests/property/ --hypothesis-seed=42

# Run specific test
pytest tests/unit/test_encoder.py -v
```
