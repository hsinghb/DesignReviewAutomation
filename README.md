# Design Review Automation

An AI-powered tool for automating the review of software design documents using OpenAI's GPT-4.

## Features

- Comprehensive design document review across multiple sections:
  - Problem Statement
  - High Level Design
  - Proposal
  - Security
  - Operating Model
  - Resiliency
- Customizable evaluation criteria
- Organization-specific criteria support
- Template-based prompts for flexible review formats
- Structured JSON output
- Detailed recommendations and scoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DesignReviewAutomation.git
cd DesignReviewAutomation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Create your design document in text format.

2. Initialize the review agent:
```python
from design_reviewer import DesignReviewAgent, DesignReviewCriteria

agent = DesignReviewAgent(prompt_templates_dir="prompt_templates")
```

3. Define your review criteria:
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
        "Scalability considerations"
    ],
    org_proposal_criteria=[
        "Cost efficiency",
        "Implementation timeline",
        "Resource requirements"
    ]
)
```

4. Run the review:
```python
result = agent.review_design(design_doc, criteria)
if result["status"] == "success":
    formatted_output = agent.format_review_output(result["review"])
    print(formatted_output)
```

## Custom Templates

You can create custom prompt templates in JSON format in the `prompt_templates` directory:

```json
{
    "name": "problem_statement_prompt",
    "content": "Your template content here with {variables}",
    "variables": ["variable1", "variable2"],
    "format": "text"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 