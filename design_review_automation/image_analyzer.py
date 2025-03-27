"""Module for analyzing images and diagrams in design documents."""

import base64
import io
import os
import tempfile
from typing import List, Optional, Tuple

import cv2
import numpy as np
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel, Field
from pdf2image import convert_from_path
from docx2txt import process
import docx
from docx.shared import Inches

class ImageAnalysisResult(BaseModel):
    """Result of image analysis."""
    description: str = Field(..., description="Detailed description of the image/diagram")
    technical_details: str = Field(..., description="Technical details and components identified")
    suggestions: List[str] = Field(..., description="Suggestions for improvement")
    quality_score: float = Field(..., description="Quality score from 0 to 1")
    issues: List[str] = Field(default_factory=list, description="Issues identified in the image")

class ImageAnalyzer:
    """Analyzes images and diagrams in design documents using OpenAI's GPT-4 Vision model."""
    
    def __init__(self, client: Optional[OpenAI] = None):
        """Initialize the image analyzer.
        
        Args:
            client: Optional OpenAI client. If not provided, will create one.
        """
        self.client = client or OpenAI()
        self.temp_dir = tempfile.mkdtemp()
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _extract_images_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract images from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            List of paths to extracted images.
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            image_paths = []
            
            # Save each page as an image
            for i, image in enumerate(images):
                image_path = os.path.join(self.temp_dir, f"page_{i+1}.png")
                image.save(image_path, "PNG")
                image_paths.append(image_path)
            
            return image_paths
        except Exception as e:
            raise ValueError(f"Failed to extract images from PDF: {str(e)}")
    
    def _extract_images_from_docx(self, docx_path: str) -> List[str]:
        """Extract images from a DOCX file.
        
        Args:
            docx_path: Path to the DOCX file.
            
        Returns:
            List of paths to extracted images.
        """
        try:
            # Extract text and images using docx2txt
            process(docx_path, self.temp_dir)
            
            # Get list of extracted images
            image_paths = []
            for filename in os.listdir(self.temp_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_paths.append(os.path.join(self.temp_dir, filename))
            
            # If no images found, try alternative method using python-docx
            if not image_paths:
                doc = docx.Document(docx_path)
                for i, rel in enumerate(doc.part.rels.values()):
                    if "image" in rel.reltype:
                        image_data = rel.target_part.blob
                        image_path = os.path.join(self.temp_dir, f"image_{i+1}.png")
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                        image_paths.append(image_path)
            
            return image_paths
        except Exception as e:
            raise ValueError(f"Failed to extract images from DOCX: {str(e)}")
    
    def _preprocess_image(self, image_path: str, preprocessing_options: Optional[Dict] = None) -> str:
        """Preprocess image for better analysis.
        
        Args:
            image_path: Path to the image file.
            preprocessing_options: Dictionary of preprocessing options.
            
        Returns:
            Path to the preprocessed image.
        """
        # Default preprocessing options
        options = preprocessing_options or {
            "grayscale": True,
            "threshold": True,
            "denoise": True,
            "resize": True,
            "max_size": 1024
        }
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale if requested
        if options.get("grayscale", True):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize if requested
        if options.get("resize", True):
            height, width = img.shape[:2]
            if max(height, width) > options["max_size"]:
                scale = options["max_size"] / max(height, width)
                img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        
        # Apply thresholding if requested
        if options.get("threshold", True):
            img = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        
        # Denoise if requested
        if options.get("denoise", True):
            img = cv2.fastNlMeansDenoising(img)
        
        # Save preprocessed image
        output_path = f"{image_path}_preprocessed.png"
        cv2.imwrite(output_path, img)
        
        return output_path
    
    def analyze_image(self, image_path: str, analysis_options: Optional[Dict] = None) -> ImageAnalysisResult:
        """Analyze an image using GPT-4 Vision.
        
        Args:
            image_path: Path to the image file.
            analysis_options: Dictionary of analysis options.
            
        Returns:
            ImageAnalysisResult containing the analysis.
        """
        # Default analysis options
        options = analysis_options or {
            "preprocessing": {
                "grayscale": True,
                "threshold": True,
                "denoise": True,
                "resize": True,
                "max_size": 1024
            },
            "analysis_type": "technical",  # technical, architectural, security, etc.
            "focus_areas": ["components", "relationships", "patterns"],
            "quality_threshold": 0.7
        }
        
        # Preprocess image
        preprocessed_path = self._preprocess_image(image_path, options["preprocessing"])
        
        # Encode image
        base64_image = self._encode_image(preprocessed_path)
        
        # Create prompt for analysis
        prompt = f"""Analyze this technical diagram or image and provide a detailed analysis focusing on:
1. Overall description and purpose
2. Technical components and their relationships
3. Design patterns and architectural decisions
4. Quality assessment and potential issues
5. Recommendations for improvement

Focus areas: {', '.join(options['focus_areas'])}
Analysis type: {options['analysis_type']}

Please provide your analysis in the following JSON format:
{{
    "description": "Detailed description",
    "technical_details": "Technical components and relationships",
    "suggestions": ["List of suggestions"],
    "quality_score": float between 0 and 1,
    "issues": ["List of issues"]
}}"""

        # Get analysis from GPT-4 Vision
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        analysis_data = json.loads(response.choices[0].message.content)
        
        return ImageAnalysisResult(**analysis_data)
    
    def analyze_document_images(self, document_path: str, analysis_options: Optional[Dict] = None) -> List[ImageAnalysisResult]:
        """Analyze all images in a document.
        
        Args:
            document_path: Path to the document file.
            analysis_options: Dictionary of analysis options.
            
        Returns:
            List of ImageAnalysisResult for each image found.
        """
        # Determine document type and extract images
        if document_path.lower().endswith('.pdf'):
            image_paths = self._extract_images_from_pdf(document_path)
        elif document_path.lower().endswith('.docx'):
            image_paths = self._extract_images_from_docx(document_path)
        else:
            raise ValueError(f"Unsupported document type: {document_path}")
        
        # Analyze each image
        results = []
        for image_path in image_paths:
            try:
                result = self.analyze_image(image_path, analysis_options)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing image {image_path}: {str(e)}")
                continue
        
        return results
    
    def __del__(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass 