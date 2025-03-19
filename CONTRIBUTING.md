# Contributing to Design Review Automation

First off, thank you for considering contributing to Design Review Automation! It's people like you that make this tool better for everyone.

## Quick Links
- [Issue Tracker](https://github.com/yourusername/design-review-automation/issues)
- [Pull Requests](https://github.com/yourusername/design-review-automation/pulls)

## How Can I Contribute?

### 1. Reporting Bugs 🐛
Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or logs
* Include the Python version and operating system

### 2. Suggesting Enhancements 💡
Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### 3. Code Contributions 💻

#### Setting Up Your Development Environment
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
   pip install -e ".[dev]"
   ```

#### Making Changes
1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run the tests:
   ```bash
   pytest
   ```
4. Run the linters:
   ```bash
   black .
   mypy .
   ```
5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add some feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

### Code Style 📝

We use:
- [Black](https://black.readthedocs.io/) for code formatting
- [mypy](http://mypy-lang.org/) for type checking
- [pylint](https://www.pylint.org/) for code quality
- [pytest](https://docs.pytest.org/) for testing

Please ensure your code:
- Is formatted with Black
- Passes mypy type checking
- Has docstrings for public functions and classes
- Includes appropriate tests
- Follows Python's [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide

### Writing Tests 🧪

- Write tests for new features
- Update tests for bug fixes
- Ensure all tests pass before submitting PR
- Include both unit tests and integration tests where appropriate

Example test:
```python
def test_review_design():
    agent = DesignReviewAgent()
    criteria = DesignReviewCriteria(
        problem_statement="Test criteria",
        high_level_design="Test criteria",
        proposal="Test criteria",
        security="Test criteria",
        operating_model="Test criteria",
        resiliency="Test criteria"
    )
    
    result = agent.review_design("test_doc.txt", criteria)
    assert result["status"] == "success"
    assert "review" in result
```

### Documentation 📚

- Update the README.md if you change functionality
- Add docstrings to new functions and classes
- Update the documentation in the docs/ directory
- Include examples in your documentation

### Pull Request Process 🔄

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with a note describing your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards
* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

## Questions? 🤔

Feel free to:
- Open an issue with your question
- Join our discussions
- Contact the maintainers directly

Thank you for contributing! 🙏 