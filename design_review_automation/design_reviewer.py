import os
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
import json
import math
from pathlib import Path
from document_parser import DocumentParser
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('design_review.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ReviewError(Exception):
    """Base exception for review-related errors."""
    pass

class DocumentProcessingError(ReviewError):
    """Exception raised when there are issues processing the document."""
    pass

class ReviewValidationError(ReviewError):
    """Exception raised when review results fail validation."""
    pass

class Verdict(str, Enum):
    APPROVE = "Approve"
    APPROVE_WITH_COMMENTS = "Approve with Comments"
    REJECT = "Reject"

class SectionScore(BaseModel):
    score: int = Field(..., ge=1, le=10)
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    reasoning: str = Field(..., description="Detailed explanation of the score and evaluation")

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
    review_metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.now().isoformat(),
            "model_version": "gpt-4-turbo-preview",
            "review_duration": None,
            "document_size": None,
            "chunks_processed": 0
        }
    )

class DesignReviewCriteria(BaseModel):
    problem_statement: str
    high_level_design: str
    proposal: str
    security: str
    operating_model: str
    resiliency: str
    org_design_criteria: Optional[List[str]] = Field(default=None, description="Organization-specific criteria for High Level Design")
    org_proposal_criteria: Optional[List[str]] = Field(default=None, description="Organization-specific criteria for Proposal")
    min_score_threshold: int = Field(default=7, ge=1, le=10, description="Minimum acceptable score for approval")
    require_security_review: bool = Field(default=True, description="Whether security review is mandatory")
    require_resiliency_review: bool = Field(default=True, description="Whether resiliency review is mandatory")

class PromptTemplate(BaseModel):
    name: str
    content: str
    variables: List[str]
    format: str = "text"

class DesignReviewAgent:
    def __init__(self, prompt_templates_dir: Optional[str] = None, max_chunk_size: int = 8000):
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if not self.client.api_key:
                raise ValueError("OpenAI API key not found in environment variables")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ReviewError(f"Failed to initialize OpenAI client: {str(e)}")

        self.prompt_templates_dir = prompt_templates_dir
        self.prompt_templates = self._load_prompt_templates()
        self.max_chunk_size = max_chunk_size
        self.document_parser = DocumentParser()
        
        # Default specialized prompts if no templates are loaded
        self.specialized_prompts = {
            "problem_statement": """You are an expert in problem analysis and requirements engineering.
Focus on evaluating the clarity, completeness, and feasibility of the problem statement.
Provide detailed reasoning for your evaluation, explaining:
1. How well the problem is defined
2. Whether all dependencies are identified
3. If risks are properly assessed
4. The clarity of the problem statement""",
            
            "high_level_design": """You are an expert software architect specializing in system design.
Focus on evaluating architectural decisions, patterns, and system organization.
Provide detailed reasoning for your evaluation, explaining:
1. The quality of architectural decisions
2. The appropriateness of design patterns
3. The clarity of component interactions
4. The scalability of the design""",
            
            "proposal": """You are an expert in solution design and implementation planning.
Focus on evaluating the proposed solution's effectiveness and implementation strategy.
Provide detailed reasoning for your evaluation, explaining:
1. The effectiveness of the solution
2. The feasibility of implementation
3. The consideration of alternatives
4. The clarity of the implementation plan""",
            
            "security": """You are an expert in software security and threat modeling.
Focus on evaluating security measures, threat vectors, and compliance requirements.
Provide detailed reasoning for your evaluation, explaining:
1. The comprehensiveness of security measures
2. The adequacy of threat modeling
3. The compliance with security standards
4. The effectiveness of security controls""",
            
            "operating_model": """You are an expert in system operations and monitoring.
Focus on evaluating operational procedures, monitoring capabilities, and maintenance plans.
Provide detailed reasoning for your evaluation, explaining:
1. The completeness of operational procedures
2. The adequacy of monitoring
3. The effectiveness of maintenance plans
4. The clarity of operational requirements""",
            
            "resiliency": """You are an expert in system reliability and fault tolerance.
Focus on evaluating system resilience, recovery procedures, and disaster planning.
Provide detailed reasoning for your evaluation, explaining:
1. The robustness of the system
2. The effectiveness of recovery procedures
3. The adequacy of disaster planning
4. The resilience of critical components"""
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
- Critical but constructive in your feedback

For each evaluation, provide detailed reasoning explaining:
1. The basis for your score
2. Key strengths identified
3. Areas needing improvement
4. Specific recommendations
5. Impact of findings on the overall design"""

    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text."""
        try:
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
        except Exception as e:
            logger.error(f"Error estimating tokens: {str(e)}")
            raise DocumentProcessingError(f"Failed to estimate tokens: {str(e)}")

    def _chunk_document(self, text: str) -> List[str]:
        """Split document into chunks that fit within token limits."""
        try:
            chunks = []
            current_chunk = []
            current_size = 0
            
            # Split by paragraphs
            paragraphs = text.split('\n\n')
            
            for para in paragraphs:
                para_tokens = self._estimate_tokens(para)
                
                if current_size + para_tokens > self.max_chunk_size:
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_size = para_tokens
                else:
                    current_chunk.append(para)
                    current_size += para_tokens
            
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                
            return chunks
        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            raise DocumentProcessingError(f"Failed to chunk document: {str(e)}")

    def _summarize_chunk(self, chunk: str) -> str:
        """Summarize a chunk of text to reduce token count while preserving key information."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing technical documents while preserving key information and structure. Focus on maintaining technical accuracy and important details."},
                    {"role": "user", "content": f"Please summarize the following text while preserving all key technical information, requirements, and design decisions. Maintain the original structure and technical accuracy:\n\n{chunk}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            logger.error(f"OpenAI API error during summarization: {str(e)}")
            raise ReviewError(f"Failed to summarize chunk: {str(e)}")
        except Exception as e:
            logger.error(f"Error summarizing chunk: {str(e)}")
            raise DocumentProcessingError(f"Failed to summarize chunk: {str(e)}")

    def _process_large_document(self, design_doc: str) -> str:
        """Process a large document by chunking and summarizing if necessary."""
        try:
            total_tokens = self._estimate_tokens(design_doc)
            
            if total_tokens <= self.max_chunk_size:
                return design_doc
                
            logger.info(f"Document is large ({total_tokens} estimated tokens). Processing in chunks...")
            
            chunks = self._chunk_document(design_doc)
            processed_chunks = []
            
            for i, chunk in enumerate(chunks, 1):
                logger.info(f"Processing chunk {i}/{len(chunks)}...")
                processed_chunk = self._summarize_chunk(chunk)
                processed_chunks.append(processed_chunk)
                
            return "\n\n".join(processed_chunks)
        except Exception as e:
            logger.error(f"Error processing large document: {str(e)}")
            raise DocumentProcessingError(f"Failed to process large document: {str(e)}")

    def _validate_review_result(self, result: Dict[str, Any], criteria: DesignReviewCriteria) -> None:
        """Validate the review result against criteria requirements."""
        try:
            # Check minimum score threshold
            for section in ["problem_statement", "high_level_design", "proposal", "security", "operating_model", "resiliency"]:
                if result[section]["score"] < criteria.min_score_threshold:
                    logger.warning(f"Section {section} scored below minimum threshold: {result[section]['score']}")

            # Check mandatory reviews
            if criteria.require_security_review and not result["security"]["recommendations"]:
                raise ReviewValidationError("Security review is mandatory but no recommendations were provided")
            
            if criteria.require_resiliency_review and not result["resiliency"]["recommendations"]:
                raise ReviewValidationError("Resiliency review is mandatory but no recommendations were provided")

            # Validate critical findings
            if not result["critical_findings"]:
                logger.warning("No critical findings were identified")

        except Exception as e:
            logger.error(f"Error validating review result: {str(e)}")
            raise ReviewValidationError(f"Failed to validate review result: {str(e)}")

    def _create_section_prompt(self, section: str, content: str, criteria: List[str]) -> str:
        # Try to use template if available
        template_name = f"{section}_prompt"
        if template_name in self.prompt_templates:
            return self._apply_template(
                template_name,
                section=section,
                content=content,
                criteria="\n".join([f"   - {criterion}" for criterion in criteria])
            )
            
        # Fallback to default prompt
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
        # Try to use template if available
        if "review_prompt" in self.prompt_templates:
            return self._apply_template(
                "review_prompt",
                design_doc=design_doc,
                criteria=criteria
            )
            
        # Fallback to default prompt
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

    def review_design(self, design_doc: Union[str, Path], criteria: DesignReviewCriteria) -> Dict:
        """Review a design document from a file or string."""
        start_time = datetime.now()
        try:
            # If design_doc is a file path, parse it
            if isinstance(design_doc, (str, Path)) and os.path.exists(design_doc):
                logger.info(f"Parsing document: {design_doc}")
                design_doc = self.document_parser.parse_document(design_doc)
            
            # Process large documents
            processed_doc = self._process_large_document(design_doc)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self._create_review_prompt(processed_doc, criteria)}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response into our structured format
            review_result = DesignReviewResult.parse_raw(response.choices[0].message.content)
            
            # Validate the review result
            self._validate_review_result(review_result.dict(), criteria)
            
            # Update review metadata
            review_result.review_metadata.update({
                "review_duration": (datetime.now() - start_time).total_seconds(),
                "document_size": len(design_doc),
                "chunks_processed": len(processed_doc.split('\n\n')) if processed_doc != design_doc else 0
            })
            
            return {
                "status": "success",
                "review": review_result
            }
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "status": "error",
                "message": f"OpenAI API error: {str(e)}"
            }
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "status": "error",
                "message": f"Validation error: {str(e)}"
            }
        except DocumentProcessingError as e:
            logger.error(f"Document processing error: {str(e)}")
            return {
                "status": "error",
                "message": f"Document processing error: {str(e)}"
            }
        except ReviewValidationError as e:
            logger.error(f"Review validation error: {str(e)}")
            return {
                "status": "error",
                "message": f"Review validation error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }

    def format_review_output(self, review_result: DesignReviewResult) -> str:
        """Format the review output with detailed reasoning."""
        try:
            # Try to use template if available
            if "output_format" in self.prompt_templates:
                return self._apply_template(
                    "output_format",
                    review_result=review_result
                )
                
            # Fallback to default format
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
                
                output.append("\nReasoning:")
                output.append(section.reasoning)
                
                output.append("\nStrengths:")
                for strength in section.strengths:
                    output.append(f"- {strength}")
                
                output.append("\nAreas for Improvement:")
                for area in section.areas_for_improvement:
                    output.append(f"- {area}")
                
                output.append("\nRecommendations:")
                for rec in section.recommendations:
                    output.append(f"- {rec}")
            
            # Review Metadata
            output.append("\nReview Metadata")
            output.append("-" * 20)
            for key, value in review_result.review_metadata.items():
                output.append(f"{key}: {value}")
            
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error formatting review output: {str(e)}")
            raise ReviewError(f"Failed to format review output: {str(e)}")

    def _load_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Load prompt templates from the specified directory."""
        templates = {}
        if not self.prompt_templates_dir:
            return templates
            
        try:
            for filename in os.listdir(self.prompt_templates_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.prompt_templates_dir, filename), 'r') as f:
                        template_data = json.load(f)
                        templates[template_data['name']] = PromptTemplate(**template_data)
        except Exception as e:
            print(f"Warning: Could not load prompt templates: {str(e)}")
            
        return templates

    def _apply_template(self, template_name: str, **kwargs) -> str:
        """Apply a template with the given variables."""
        if template_name not in self.prompt_templates:
            return ""
            
        template = self.prompt_templates[template_name]
        content = template.content
        
        # Replace variables in the template
        for var in template.variables:
            if var in kwargs:
                content = content.replace(f"{{{var}}}", str(kwargs[var]))
                
        return content

def main():
    # Example usage
    agent = DesignReviewAgent(prompt_templates_dir="prompt_templates")
    
    # Example with different document formats
    # 1. From a file
    result = agent.review_design("path/to/design.docx", criteria)
    
    # 2. From a string
    design_doc = """
    [Your design document content here]
    """
    result = agent.review_design(design_doc, criteria)
    
    if result["status"] == "success":
        formatted_output = agent.format_review_output(result["review"])
        print(formatted_output)
    else:
        print(f"Error during review: {result['message']}")

if __name__ == "__main__":
    main() 