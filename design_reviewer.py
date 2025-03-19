import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum

# Load environment variables
load_dotenv()

class Verdict(str, Enum):
    APPROVE = "Approve"
    APPROVE_WITH_COMMENTS = "Approve with Comments"
    REJECT = "Reject"

class SectionScore(BaseModel):
    score: int = Field(..., ge=1, le=10)
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]

class DesignReviewResult(BaseModel):
    problem_statement: SectionScore
    high_level_design: SectionScore
    proposal: SectionScore
    security: SectionScore
    operating_model: SectionScore
    resiliency: SectionScore
    overall_verdict: Verdict
    summary: str
    critical_findings: List[str]

class DesignReviewCriteria(BaseModel):
    problem_statement: str
    high_level_design: str
    proposal: str
    security: str
    operating_model: str
    resiliency: str
    org_design_criteria: Optional[List[str]] = Field(default=None, description="Organization-specific criteria for High Level Design")
    org_proposal_criteria: Optional[List[str]] = Field(default=None, description="Organization-specific criteria for Proposal")

class DesignReviewAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.specialized_prompts = {
            "problem_statement": """You are an expert in problem analysis and requirements engineering.
Focus on evaluating the clarity, completeness, and feasibility of the problem statement.""",
            
            "high_level_design": """You are an expert software architect specializing in system design.
Focus on evaluating architectural decisions, patterns, and system organization.""",
            
            "proposal": """You are an expert in solution design and implementation planning.
Focus on evaluating the proposed solution's effectiveness and implementation strategy.""",
            
            "security": """You are an expert in software security and threat modeling.
Focus on evaluating security measures, threat vectors, and compliance requirements.""",
            
            "operating_model": """You are an expert in system operations and monitoring.
Focus on evaluating operational procedures, monitoring capabilities, and maintenance plans.""",
            
            "resiliency": """You are an expert in system reliability and fault tolerance.
Focus on evaluating system resilience, recovery procedures, and disaster planning."""
        }
        
        self.system_prompt = """You are an expert technical design review agent specializing in software architecture and system design.
Your role is to thoroughly analyze design documents and provide structured, actionable feedback based on specific criteria.

Key responsibilities:
1. Analyze each section of the design document systematically
2. Evaluate against specific criteria for each section
3. Provide specific, actionable recommendations
4. Score each section objectively
5. Make a final verdict based on comprehensive analysis

You should be:
- Thorough and systematic in your analysis
- Objective and evidence-based in your scoring
- Specific and actionable in your recommendations
- Clear and concise in your communication
- Critical but constructive in your feedback"""

    def _create_section_prompt(self, section: str, content: str, criteria: List[str]) -> str:
        specialized_prompt = self.specialized_prompts.get(section, "")
        criteria_list = "\n".join([f"   - {criterion}" for criterion in criteria])
        return f"""{specialized_prompt}

Review the following {section.replace('_', ' ').title()} section:

{content}

Evaluation Criteria:
{criteria_list}

Provide your evaluation in the following JSON format:
{{
    "score": <1-10>,
    "strengths": ["<strength1>", "<strength2>", ...],
    "areas_for_improvement": ["<area1>", "<area2>", ...],
    "recommendations": ["<recommendation1>", "<recommendation2>", ...]
}}"""

    def _create_review_prompt(self, design_doc: str, criteria: DesignReviewCriteria) -> str:
        # Build organization-specific criteria sections
        design_criteria = criteria.org_design_criteria if criteria.org_design_criteria else [
            "L1 design depth",
            "Explanation quality",
            "System architecture",
            "Component interactions",
            "Design patterns"
        ]
        
        proposal_criteria = criteria.org_proposal_criteria if criteria.org_proposal_criteria else [
            "Problem-solving effectiveness",
            "L2 level design explanation",
            "Implementation strategy",
            "Alternatives considered"
        ]

        return f"""Please perform a comprehensive review of the following design document based on the specified criteria.

Design Document:
{design_doc}

Review Criteria and Requirements:

1. Problem Statement:
   - Clarity of Problem definition
   - Dependencies
   - Risks
   - Literal clarity
   Required: Clear articulation of the problem, its scope, and impact

2. High Level Design:
{chr(10).join(f"   - {criterion}" for criterion in design_criteria)}
   Required: System architecture, component interactions, and design patterns

3. Proposal:
{chr(10).join(f"   - {criterion}" for criterion in proposal_criteria)}
   Required: Detailed solution approach, implementation strategy, and alternatives considered

4. Security:
   - Threat Modeling
   - ASRA/ACRA
   - CARA
   - Penn Testing
   Required: Comprehensive security analysis, threat vectors, and mitigation strategies

5. Operating Model:
   - Healthchecks
   - Monitoring
   Required: Operational procedures, monitoring strategy, and maintenance plans

6. Resiliency:
   Required: System reliability, fault tolerance, and disaster recovery plans

Please provide your review in the following JSON format:
{{
    "problem_statement": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "high_level_design": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "proposal": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "security": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "operating_model": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "resiliency": {{
        "score": <1-10>,
        "strengths": ["<strength1>", "<strength2>", ...],
        "areas_for_improvement": ["<area1>", "<area2>", ...],
        "recommendations": ["<recommendation1>", "<recommendation2>", ...]
    }},
    "overall_verdict": "<Approve|Approve with Comments|Reject>",
    "summary": "<brief summary of the review>",
    "critical_findings": ["<critical finding1>", "<critical finding2>", ...]
}}

For each section, consider:
1. Completeness of required elements
2. Quality of implementation
3. Alignment with best practices
4. Potential risks and mitigations
5. Scalability and maintainability"""

    def review_design(self, design_doc: str, criteria: DesignReviewCriteria) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self._create_review_prompt(design_doc, criteria)}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response into our structured format
            review_result = DesignReviewResult.parse_raw(response.choices[0].message.content)
            
            return {
                "status": "success",
                "review": review_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def format_review_output(self, review_result: DesignReviewResult) -> str:
        output = []
        output.append("Design Review Results")
        output.append("=" * 50)
        
        # Overall Summary
        output.append("\nOverall Summary")
        output.append("-" * 20)
        output.append(review_result.summary)
        output.append(f"\nFinal Verdict: {review_result.overall_verdict}")
        
        # Critical Findings
        if review_result.critical_findings:
            output.append("\nCritical Findings")
            output.append("-" * 20)
            for finding in review_result.critical_findings:
                output.append(f"- {finding}")
        
        # Section-by-Section Review
        sections = [
            ("Problem Statement", review_result.problem_statement),
            ("High Level Design", review_result.high_level_design),
            ("Proposal", review_result.proposal),
            ("Security", review_result.security),
            ("Operating Model", review_result.operating_model),
            ("Resiliency", review_result.resiliency)
        ]
        
        for section_name, section in sections:
            output.append(f"\n{section_name}")
            output.append("-" * 20)
            output.append(f"Score: {section.score}/10")
            
            output.append("\nStrengths:")
            for strength in section.strengths:
                output.append(f"- {strength}")
            
            output.append("\nAreas for Improvement:")
            for area in section.areas_for_improvement:
                output.append(f"- {area}")
            
            output.append("\nRecommendations:")
            for rec in section.recommendations:
                output.append(f"- {rec}")
        
        return "\n".join(output)

def main():
    # Example usage
    agent = DesignReviewAgent()
    
    # Example design document (replace with actual document)
    design_doc = """
    [Your design document content here]
    """
    
    # Example organization-specific criteria
    org_design_criteria = [
        "Architecture alignment with company standards",
        "Component reusability",
        "Scalability considerations",
        "Integration patterns"
    ]
    
    org_proposal_criteria = [
        "Cost efficiency",
        "Implementation timeline",
        "Resource requirements",
        "Risk mitigation strategy"
    ]
    
    # Example criteria with organization-specific criteria
    criteria = DesignReviewCriteria(
        problem_statement="",
        high_level_design="",
        proposal="",
        security="",
        operating_model="",
        resiliency="",
        org_design_criteria=org_design_criteria,
        org_proposal_criteria=org_proposal_criteria
    )
    
    result = agent.review_design(design_doc, criteria)
    
    if result["status"] == "success":
        formatted_output = agent.format_review_output(result["review"])
        print(formatted_output)
    else:
        print(f"Error during review: {result['message']}")

if __name__ == "__main__":
    main() 