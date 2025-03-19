# Contributing to Design Review Automation

Thank you for your interest in contributing to Design Review Automation! This document provides guidelines and steps for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/design-review-automation.git
   cd design-review-automation
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use type hints with mypy

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Maintain or improve test coverage

### Documentation

- Update README.md for significant changes
- Add docstrings to new functions and classes
- Update type hints and comments

## Pull Request Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request from your fork to the main repository

### Pull Request Guidelines

- Use a clear and descriptive title
- Provide a detailed description of your changes
- Include any relevant issue numbers
- Add tests for new features
- Update documentation as needed

## Code Review Process

1. All PRs will be reviewed by maintainers
2. Address any feedback and make requested changes
3. Once approved, your PR will be merged

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. The release will trigger the publish workflow

## Getting Help

- Open an issue for bug reports or feature requests
- Join discussions in existing issues
- Contact maintainers for questions

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 