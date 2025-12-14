# Contributing to NyxOS AI Engine

Thank you for your interest in contributing to NyxOS AI Engine! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### Setup Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-engine.git
   cd ai-engine
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guide

3. Format your code:
   ```bash
   black .
   ```

4. Check for issues:
   ```bash
   flake8 .
   ```

5. Run tests:
   ```bash
   pytest
   ```

## Code Style Guide

- Follow PEP 8 standards
- Use type hints where possible
- Write docstrings for all modules, classes, and functions
- Maximum line length: 120 characters
- Use meaningful variable names

### Example

```python
def calculate_attention_scores(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Calculate attention scores using scaled dot-product attention.
    
    Args:
        query: Query tensor of shape (batch, seq_len, d_k)
        key: Key tensor of shape (batch, seq_len, d_k)
        value: Value tensor of shape (batch, seq_len, d_v)
        mask: Optional attention mask
        
    Returns:
        Attention output tensor of shape (batch, seq_len, d_v)
    """
    # Implementation
    pass
```

## Commit Messages

Follow conventional commits format:

```
type(scope): short description

Longer description explaining the change, why it was made,
and any side effects or relevant information.
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`

Examples:
- `feat(model): add multi-head attention mechanism`
- `fix(api): resolve CORS configuration issue`
- `docs(readme): update installation instructions`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass: `pytest`
4. Push to your fork
5. Create a Pull Request to the `main` branch
6. Provide a clear description of changes
7. Link any related issues

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_model.py

# Run with coverage
pytest --cov=.
```

### Writing Tests

Tests should be placed in a `tests/` directory mirroring the source structure.

```python
import pytest
from model.attention import MultiHeadAttention

def test_attention_output_shape():
    """Test that attention produces correct output shape."""
    attn = MultiHeadAttention(d_model=256, num_heads=8)
    # Test implementation
    assert output.shape == expected_shape
```

## Documentation

- Update README.md for significant changes
- Add docstrings to all public functions
- Update DEPLOYMENT.md if deployment process changes
- Include examples for new features

## Reporting Issues

Use the GitHub Issues template to report bugs or suggest features:

- **Bug Reports**: Describe the issue, steps to reproduce, and expected behavior
- **Feature Requests**: Explain the use case and benefits
- **Questions**: Use Discussions instead

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for bugs or feature requests
- Start a Discussion for questions
- Read the DEPLOYMENT.md for deployment-related questions

Thank you for contributing!
