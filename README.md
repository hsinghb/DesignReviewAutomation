# Design Review Automation

[![CI](https://github.com/yourusername/design-review-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/design-review-automation/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/yourusername/design-review-automation/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/design-review-automation)
[![PyPI version](https://badge.fury.io/py/design-review-automation.svg)](https://badge.fury.io/py/design-review-automation)
[![Python Versions](https://img.shields.io/pypi/pyversions/design-review-automation.svg)](https://pypi.org/project/design-review-automation/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful tool for automated technical design document review using OpenAI's GPT models. This tool helps streamline the design review process by providing comprehensive, structured feedback on technical design documents.

## Features

- Automated review of technical design documents
- Support for multiple document formats (PDF, DOCX, Markdown, plain text)
- Comprehensive evaluation across multiple criteria:
  - Problem Statement
  - High Level Design
  - Proposal
  - Security
  - Operations
- Detailed reasoning and recommendations for each section
- Organization-specific criteria support
- Large document handling with smart chunking
- Extensive error handling and logging
- Customizable prompt templates

## Installation

### From PyPI

```bash
pip install design-review-automation
```

### From Source

```bash
git clone https://github.com/yourusername/design-review-automation.git
cd design-review-automation
pip install -e .
```

## Usage

### Basic Usage

```python
from design_review_automation import DesignReviewAgent, DesignReviewCriteria

# Initialize the agent
agent = DesignReviewAgent(prompt_templates_dir="prompt_templates")

# Define review criteria
criteria = DesignReviewCriteria(
    problem_statement="Clear problem definition with scope and impact",
    high_level_design="Comprehensive system architecture and design patterns",
    proposal="Detailed solution approach and implementation strategy",
    security="Security measures and compliance requirements",
    operating_model="Operational procedures and monitoring",
    resiliency="System reliability and disaster recovery"
)

# Review a design document
result = agent.review_design("path/to/design.docx", criteria)

if result["status"] == "success":
    print(agent.format_review_output(result["review"]))
else:
    print(f"Error during review: {result['message']}")
```

### Command Line Interface

```bash
design-review --input path/to/design.docx --output review_results.txt
```

### Custom Templates

Create custom prompt templates in JSON format:

```json
{
    "name": "problem_statement_prompt",
    "content": "Review the following problem statement:\n\n{content}\n\nEvaluation Criteria:\n{criteria}",
    "variables": ["content", "criteria"],
    "format": "text"
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MAX_CHUNK_SIZE`: Maximum tokens per chunk (default: 8000)

### Review Criteria

Customize review criteria by setting organization-specific requirements:

```python
criteria = DesignReviewCriteria(
    # ... other criteria ...
    org_design_criteria=[
        "Custom design criterion 1",
        "Custom design criterion 2"
    ],
    org_proposal_criteria=[
        "Custom proposal criterion 1",
        "Custom proposal criterion 2"
    ],
    min_score_threshold=8,
    require_security_review=True,
    require_resiliency_review=True
)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/design-review-automation.git
cd design-review-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
mypy .
```

### Running Tests

```bash
pytest tests/
```

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history. 
