# Contributing to DevInt

Thank you for your interest in contributing to DevInt! We welcome contributions from everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Install development dependencies:
   ```bash
   poetry install --with dev
   ```
4. Create a new branch for your changes
5. Make your changes and ensure tests pass
6. Submit a pull request

## Development Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write docstrings for all public functions and classes
- Add type hints for better code clarity
- Write tests for new features and bug fixes
- Update documentation when adding new features

## Testing

Run tests with:

```bash
make test
```

## Code Style

We use `black` for code formatting and `isort` for import sorting. Before committing, run:

```bash
make format
```

## Reporting Issues

When reporting issues, please include:
- Version of DevInt
- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
