# Design Review Automation

[![CI](https://github.com/yourusername/design-review-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/design-review-automation/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/yourusername/design-review-automation/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/design-review-automation)
[![PyPI version](https://badge.fury.io/py/design-review-automation.svg)](https://badge.fury.io/py/design-review-automation)
[![Python Versions](https://img.shields.io/pypi/pyversions/design-review-automation.svg)](https://pypi.org/project/design-review-automation/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful tool for automated technical design document review using OpenAI's GPT models. This tool helps streamline the design review process by providing comprehensive, structured feedback on technical design documents.

## Quick Start ⚡

### 1. Install from GitHub
```bash
# Method 1: Clone and install
git clone https://github.com/yourusername/design-review-automation.git
cd design-review-automation
pip install -e .

# Method 2: Direct pip install from GitHub
pip install git+https://github.com/yourusername/design-review-automation.git
```

### 2. Set up OpenAI API Key
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Run Your First Review
```python
from design_review_automation import DesignReviewAgent, DesignReviewCriteria

# Initialize agent
agent = DesignReviewAgent()

# Create basic criteria
criteria = DesignReviewCriteria(
    problem_statement="Clear problem definition",
    high_level_design="System architecture and patterns",
    proposal="Solution approach",
    security="Security measures",
    operating_model="Operations and monitoring",
    resiliency="System reliability"
)

# Review a document
result = agent.review_design("your_design_doc.docx", criteria)
print(agent.format_review_output(result["review"]))
```

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

## Requirements

- Python 3.8 or higher
- OpenAI API key
- Required Python packages (automatically installed):
  - openai>=1.0.0
  - python-dotenv>=0.19.0
  - pydantic>=2.0.0
  - python-docx>=0.8.11
  - PyPDF2>=3.0.0
  - markdown>=3.4.0
  - python-magic>=0.4.27

## Detailed Installation Options

### From GitHub (Development Version)
```bash
# Clone with specific branch
git clone -b main https://github.com/yourusername/design-review-automation.git
cd design-review-automation

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### From Source Archive
```bash
# Download source archive
wget https://github.com/yourusername/design-review-automation/archive/refs/heads/main.zip
unzip main.zip
cd design-review-automation-main

# Install
pip install .
```

## Usage Examples

### Basic Document Review
```python
from design_review_automation import DesignReviewAgent, DesignReviewCriteria

# Initialize the agent
agent = DesignReviewAgent()

# Define basic criteria
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

### Custom Organization Criteria
```python
# Define criteria with organization-specific requirements
criteria = DesignReviewCriteria(
    # ... basic criteria ...
    org_design_criteria=[
        "Alignment with company architecture standards",
        "Use of approved design patterns",
        "Integration with existing systems",
        "Scalability considerations"
    ],
    org_proposal_criteria=[
        "Resource requirements and availability",
        "Implementation timeline",
        "Risk assessment and mitigation",
        "Cost-benefit analysis"
    ],
    min_score_threshold=7,
    require_security_review=True
)
```

### Using Custom Templates
```python
# Initialize agent with custom templates
agent = DesignReviewAgent(prompt_templates_dir="my_templates")

# Create custom template file: my_templates/security_prompt.json
{
    "name": "security_prompt",
    "content": "As a security expert, review this section:\n\n{content}\n\nFocus on:\n{criteria}",
    "variables": ["content", "criteria"],
    "format": "text"
}
```

## Common Use Cases

1. **Design Document Review**
   - Technical design documents
   - Architecture proposals
   - System design specifications

2. **Security Review**
   - Security architecture review
   - Threat modeling validation
   - Compliance verification

3. **Quality Assurance**
   - Design pattern validation
   - Best practices verification
   - Standards compliance

## Troubleshooting

### Common Issues

1. **API Key Issues**
```python
# Check if API key is properly loaded
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found!")
```

2. **Document Processing Issues**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

3. **Memory Issues with Large Documents**
```python
# Adjust chunk size for large documents
agent = DesignReviewAgent(max_chunk_size=4000)
```

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the Repository**
   - Create your feature branch (`git checkout -b feature/AmazingFeature`)
   - Commit your changes (`git commit -m 'Add some AmazingFeature'`)
   - Push to the branch (`git push origin feature/AmazingFeature`)
   - Open a Pull Request

2. **Report Issues**
   - Use the GitHub issue tracker
   - Include detailed description and steps to reproduce
   - Attach sample files if possible

3. **Suggest Improvements**
   - Open discussions for feature requests
   - Share your use cases and requirements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
This means you can:
- ✅ Use the code commercially
- ✅ Modify the code
- ✅ Distribute the code
- ✅ Use the code privately
- ✅ Use the code for patent purposes

The only requirement is to include the original copyright notice and license.

## Support

Need help? Here's how to get support:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/yourusername/design-review-automation/issues)
3. Open a new issue
4. Contact the maintainers

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history. 
