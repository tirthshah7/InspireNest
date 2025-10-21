# Contributing to InspireNest

Thank you for your interest in contributing to InspireNest! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- System information (OS, Python version, etc.)

### Suggesting Enhancements

We welcome feature requests! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** (`pytest`)
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/InspireNest.git
cd InspireNest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks (if available)
pre-commit install

# Run tests
pytest
```

## 📝 Code Style

### Python
- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Maximum line length: 100 characters

### JavaScript/React
- Use ESLint and Prettier configurations
- Use functional components with hooks
- Follow React best practices

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ai_nester.py

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_ai_nester.py::test_ai_analysis
```

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names
- Cover edge cases
- Aim for >80% code coverage

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation for endpoint changes
- Create/update docs in `docs/` for major features

## 🔀 Git Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation updates
- `refactor/refactor-description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(ai): add geometric complexity classifier
fix(dxf): correct hole positioning in export
docs(readme): update installation instructions
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Machine learning model for algorithm selection
- [ ] Performance optimization for large part counts
- [ ] Additional test files and benchmarks
- [ ] Mobile-responsive UI improvements

### Medium Priority
- [ ] Integration with popular CAD software
- [ ] Advanced visualization features
- [ ] Real-time collaborative nesting
- [ ] Cloud deployment guides

### Good First Issues
- [ ] Add more unit tests
- [ ] Improve error messages
- [ ] Documentation improvements
- [ ] UI/UX enhancements

## ❓ Questions?

Feel free to:
- Open an issue for questions
- Reach out to maintainers
- Join our community discussions

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on collaboration
- Help others learn and grow

## 🙏 Thank You!

Your contributions make InspireNest better for everyone!

