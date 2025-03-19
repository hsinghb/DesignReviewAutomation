# Design Document Review Automation

This tool automates the review of design documents using OpenAI's GPT-4 model. It evaluates design documents based on specific criteria including problem statement, high-level design, proposal, security, operating model, and resiliency.

## Features

- Automated design document review
- Comprehensive evaluation across multiple criteria
- Detailed feedback with strengths and areas for improvement
- Scoring system for each section
- Final verdict with recommendations

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Prepare your design document as a string
2. Create a `DesignReviewCriteria` instance with your specific criteria
3. Run the script:
   ```bash
   python design_reviewer.py
   ```

## Review Criteria

The tool evaluates design documents based on the following criteria:

1. Problem Statement
   - Clarity of Problem definition
   - Dependencies
   - Risks
   - Literal clarity

2. High Level Design
   - L1 design depth
   - Explanation quality

3. Proposal
   - Problem-solving effectiveness
   - L2 level design explanation

4. Security
   - Threat Modeling
   - ASRA/ACRA
   - CARA
   - Penn Testing

5. Operating Model
   - Healthchecks
   - Monitoring

6. Resiliency

## Output

The review will provide:
- Detailed analysis for each section
- Strengths and areas for improvement
- Specific recommendations
- Score (1-10) for each section
- Final verdict (Approve/Approve with Comments/Reject)

## Example

```python
from design_reviewer import DesignReviewer, DesignReviewCriteria

reviewer = DesignReviewer()

design_doc = """
[Your design document content here]
"""

criteria = DesignReviewCriteria(
    problem_statement="",
    high_level_design="",
    proposal="",
    security="",
    operating_model="",
    resiliency=""
)

result = reviewer.review_design(design_doc, criteria)
print(result["review"])
```

## Note

Make sure to keep your OpenAI API key secure and never commit it to version control. 