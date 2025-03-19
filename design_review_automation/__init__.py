"""
Design Review Automation - A tool for automated technical design document review using OpenAI's GPT models.
"""

__version__ = "0.1.0"
__author__ = "Design Review Automation Team"
__license__ = "MIT"

from .design_reviewer import (
    DesignReviewAgent,
    DesignReviewCriteria,
    DesignReviewResult,
    SectionScore,
    Verdict,
    ReviewError,
    DocumentProcessingError,
    ReviewValidationError
)
from .document_parser import DocumentParser

__all__ = [
    'DesignReviewAgent',
    'DesignReviewCriteria',
    'DesignReviewResult',
    'SectionScore',
    'Verdict',
    'ReviewError',
    'DocumentProcessingError',
    'ReviewValidationError',
    'DocumentParser'
] 