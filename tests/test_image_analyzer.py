"""Tests for the image analyzer module."""

import os
import pytest
from unittest.mock import Mock, patch

from design_review_automation.image_analyzer import ImageAnalyzer, ImageAnalysisResult

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    with patch('design_review_automation.image_analyzer.OpenAI') as mock:
        client = Mock()
        mock.return_value = client
        yield client

@pytest.fixture
def image_analyzer(mock_openai_client):
    """Create an ImageAnalyzer instance with mocked client."""
    return ImageAnalyzer(client=mock_openai_client)

def test_encode_image(image_analyzer, tmp_path):
    """Test image encoding."""
    # Create a test image
    test_image = tmp_path / "test.png"
    test_image.write_bytes(b"fake image data")
    
    # Test encoding
    encoded = image_analyzer._encode_image(str(test_image))
    assert encoded == "ZmFrZSBpbWFnZSBkYXRh"  # base64 of "fake image data"

def test_preprocess_image(image_analyzer, tmp_path):
    """Test image preprocessing."""
    # Create a test image
    test_image = tmp_path / "test.png"
    test_image.write_bytes(b"fake image data")
    
    # Mock cv2 functions
    with patch('design_review_automation.image_analyzer.cv2') as mock_cv2:
        mock_cv2.imread.return_value = Mock()
        mock_cv2.cvtColor.return_value = Mock()
        mock_cv2.adaptiveThreshold.return_value = Mock()
        mock_cv2.fastNlMeansDenoising.return_value = Mock()
        
        # Test preprocessing
        output_path = image_analyzer._preprocess_image(str(test_image))
        assert output_path == str(test_image) + "_preprocessed.png"
        
        # Verify cv2 calls
        mock_cv2.imread.assert_called_once()
        mock_cv2.cvtColor.assert_called_once()
        mock_cv2.adaptiveThreshold.assert_called_once()
        mock_cv2.fastNlMeansDenoising.assert_called_once()
        mock_cv2.imwrite.assert_called_once()

def test_analyze_image(image_analyzer, tmp_path):
    """Test image analysis."""
    # Create a test image
    test_image = tmp_path / "test.png"
    test_image.write_bytes(b"fake image data")
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="Test analysis"))
    ]
    image_analyzer.client.chat.completions.create.return_value = mock_response
    
    # Test analysis
    result = image_analyzer.analyze_image(str(test_image))
    
    # Verify result
    assert isinstance(result, ImageAnalysisResult)
    assert result.description == "Test analysis"
    assert result.technical_details == "Technical details extracted from analysis"
    assert len(result.suggestions) == 2
    assert 0 <= result.quality_score <= 1
    
    # Verify OpenAI API call
    image_analyzer.client.chat.completions.create.assert_called_once()

def test_analyze_document_images(image_analyzer, tmp_path):
    """Test document image analysis."""
    # Create a test PDF file
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"fake pdf data")
    
    # Mock image extraction
    with patch.object(image_analyzer, '_extract_images_from_pdf') as mock_extract:
        mock_extract.return_value = [str(tmp_path / "image1.png")]
        
        # Mock image analysis
        with patch.object(image_analyzer, 'analyze_image') as mock_analyze:
            mock_analyze.return_value = ImageAnalysisResult(
                description="Test analysis",
                technical_details="Test details",
                suggestions=["Test suggestion"],
                quality_score=0.8,
                issues=["Test issue"]
            )
            
            # Test document analysis
            results = image_analyzer.analyze_document_images(str(test_pdf))
            
            # Verify results
            assert len(results) == 1
            assert isinstance(results[0], ImageAnalysisResult)
            assert results[0].description == "Test analysis"
            assert results[0].quality_score == 0.8

def test_analyze_document_images_unsupported_format(image_analyzer, tmp_path):
    """Test document analysis with unsupported format."""
    # Create a test file with unsupported format
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    # Test analysis
    with pytest.raises(ValueError, match="Unsupported document type"):
        image_analyzer.analyze_document_images(str(test_file)) 