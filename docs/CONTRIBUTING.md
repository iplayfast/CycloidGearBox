# Contributing to CycloidGearBox

Thank you for your interest in contributing to the CycloidGearBox FreeCAD Workbench!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- FreeCAD 0.19 or higher (for full integration testing)
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/iplayfast/CycloidGearBox.git
cd CycloidGearBox
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Code Quality Standards

### Linting and Formatting

We use several tools to maintain code quality:

- **Black**: Code formatting (line length: 127)
- **flake8**: Code linting
- **pylint**: Additional linting
- **mypy**: Static type checking

Run all checks before committing:

```bash
# Format code
black cycloidFun.py cycloidbox.py InitGui.py

# Lint
flake8 .
pylint cycloidFun.py cycloidbox.py

# Type check
mypy cycloidFun.py --ignore-missing-imports
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_cycloidFun.py -v
```

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Maximum line length: 127 characters
- Use type hints for all function parameters and return values
- Write comprehensive docstrings (Google style)

### Function Documentation

```python
def example_function(param1: int, param2: str) -> bool:
    """Short one-line summary.

    Longer description if needed, explaining what the function does,
    any important behavior, or algorithms used.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this is raised
    """
    pass
```

### Commit Messages

Use clear, descriptive commit messages:

```
Short (50 chars or less) summary

More detailed explanatory text, if necessary. Wrap it to about 72
characters. The blank line separating the summary from the body is
critical.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123"
```

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures for common setup
- Aim for >80% code coverage

### Test Example

```python
import pytest
from cycloidFun import validate_parameters, ParameterValidationError

def test_valid_parameters():
    """Test that valid parameters pass validation."""
    params = {
        "tooth_count": 11,
        "eccentricity": 2.0,
        # ... other params
    }
    validate_parameters(params)  # Should not raise

def test_invalid_tooth_count():
    """Test that invalid tooth count raises error."""
    params = {"tooth_count": 1, ...}
    with pytest.raises(ParameterValidationError):
        validate_parameters(params)
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation

3. **Test thoroughly**
   ```bash
   pytest tests/ -v
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

## What to Contribute

### Good First Issues

- Improve documentation
- Add more unit tests
- Fix typos or formatting
- Add type hints to functions

### Enhancements

- New features for gearbox design
- Performance optimizations
- Better error messages
- UI improvements

### Bug Fixes

- Search existing issues
- Create test case that reproduces bug
- Fix the bug
- Verify test passes

## Code Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Questions?

- Open an issue for questions
- Check existing documentation
- Review similar closed issues

## License

By contributing, you agree that your contributions will be licensed under the LGPL V2.1 License.
