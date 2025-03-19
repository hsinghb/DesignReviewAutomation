# Design Review Automation

A Python tool for automating the review of technical design documents using OpenAI's GPT-4. This tool can analyze design documents in various formats and provide structured feedback based on predefined criteria.

## Features

- Support for multiple document formats:
  - DOCX (Microsoft Word)
  - PDF
  - Markdown
  - Plain Text
- Comprehensive design review covering:
  - Problem Statement
  - High Level Design
  - Proposal
  - Security
  - Operating Model
  - Resiliency
- Organization-specific evaluation criteria
- Template-based prompts for customization
- Large document handling with automatic chunking
- Structured JSON output
- Detailed formatted reports

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/design-review-automation.git
cd design-review-automation
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```python
from design_reviewer import DesignReviewAgent, DesignReviewCriteria

# Initialize the agent
agent = DesignReviewAgent(prompt_templates_dir="prompt_templates")

# Define review criteria
criteria = DesignReviewCriteria(
    problem_statement="",
    high_level_design="",
    proposal="",
    security="",
    operating_model="",
    resiliency=""
)

# Review a document
result = agent.review_design("path/to/design.docx", criteria)

# Format and print the results
if result["status"] == "success":
    formatted_output = agent.format_review_output(result["review"])
    print(formatted_output)
else:
    print(f"Error during review: {result['message']}")
```

### Using Organization-Specific Criteria

```python
criteria = DesignReviewCriteria(
    problem_statement="",
    high_level_design="",
    proposal="",
    security="",
    operating_model="",
    resiliency="",
    org_design_criteria=[
        "Architecture alignment with company standards",
        "Component reusability",
        "Scalability considerations",
        "Integration patterns"
    ],
    org_proposal_criteria=[
        "Cost efficiency",
        "Implementation timeline",
        "Resource requirements",
        "Risk mitigation strategy"
    ]
)
```

### Custom Prompt Templates

Create JSON files in the `prompt_templates` directory with the following structure:

```json
{
    "name": "section_prompt",
    "content": "Your prompt template here with {variables}",
    "variables": ["variable1", "variable2"],
    "format": "text"
}
```

## Document Size Limits

The tool can handle documents of various sizes:
- Small documents (< 8000 tokens): Processed directly
- Large documents (> 8000 tokens): Automatically chunked and summarized
- Maximum document size: ~96,000 words (192 pages at 500 words per page)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 