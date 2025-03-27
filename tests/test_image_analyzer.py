"""Tests for the image analyzer module."""

import os
import json
import pytest
from unittest.mock import Mock, patch, mock_open

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
        
        # Test preprocessing with default options
        output_path = image_analyzer._preprocess_image(str(test_image))
        assert output_path == str(test_image) + "_preprocessed.png"
        
        # Test preprocessing with custom options
        custom_options = {
            "grayscale": False,
            "threshold": False,
            "denoise": False,
            "resize": True,
            "max_size": 2048
        }
        output_path = image_analyzer._preprocess_image(str(test_image), custom_options)
        assert output_path == str(test_image) + "_preprocessed.png"
        
        # Verify cv2 calls
        mock_cv2.imread.assert_called()
        mock_cv2.cvtColor.assert_called()
        mock_cv2.adaptiveThreshold.assert_called()
        mock_cv2.fastNlMeansDenoising.assert_called()
        mock_cv2.imwrite.assert_called()

def test_analyze_image(image_analyzer, tmp_path):
    """Test image analysis."""
    # Create a test image
    test_image = tmp_path / "test.png"
    test_image.write_bytes(b"fake image data")
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content=json.dumps({
            "description": "Test analysis",
            "technical_details": "Test details",
            "suggestions": ["Test suggestion"],
            "quality_score": 0.8,
            "issues": ["Test issue"]
        })))
    ]
    image_analyzer.client.chat.completions.create.return_value = mock_response
    
    # Test analysis with default options
    result = image_analyzer.analyze_image(str(test_image))
    
    # Verify result
    assert isinstance(result, ImageAnalysisResult)
    assert result.description == "Test analysis"
    assert result.technical_details == "Test details"
    assert result.suggestions == ["Test suggestion"]
    assert result.quality_score == 0.8
    assert result.issues == ["Test issue"]
    
    # Test analysis with custom options
    custom_options = {
        "preprocessing": {
            "grayscale": False,
            "threshold": False,
            "denoise": False,
            "resize": True,
            "max_size": 2048
        },
        "analysis_type": "security",
        "focus_areas": ["security", "compliance"],
        "quality_threshold": 0.9
    }
    result = image_analyzer.analyze_image(str(test_image), custom_options)
    
    # Verify OpenAI API call
    image_analyzer.client.chat.completions.create.assert_called()

def test_extract_images_from_pdf(image_analyzer, tmp_path):
    """Test PDF image extraction."""
    # Create a test PDF file
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"fake pdf data")
    
    # Mock pdf2image functions
    with patch('design_review_automation.image_analyzer.convert_from_path') as mock_convert:
        mock_convert.return_value = [Mock()]
        
        # Test extraction
        image_paths = image_analyzer._extract_images_from_pdf(str(test_pdf))
        
        # Verify results
        assert len(image_paths) == 1
        assert image_paths[0].startswith(image_analyzer.temp_dir)
        assert image_paths[0].endswith(".png")
        
        # Verify pdf2image call
        mock_convert.assert_called_once_with(str(test_pdf))

def test_extract_images_from_docx(image_analyzer, tmp_path):
    """Test DOCX image extraction."""
    # Create a test DOCX file
    test_docx = tmp_path / "test.docx"
    test_docx.write_bytes(b"fake docx data")
    
    # Mock docx2txt and docx functions
    with patch('design_review_automation.image_analyzer.process') as mock_process, \
         patch('design_review_automation.image_analyzer.docx.Document') as mock_docx:
        
        # Test extraction with docx2txt
        mock_process.return_value = None
        mock_docx.return_value.part.rels.values.return_value = [
            Mock(reltype="image/jpeg", target_part=Mock(blob=b"fake image data"))
        ]
        
        image_paths = image_analyzer._extract_images_from_docx(str(test_docx))
        
        # Verify results
        assert len(image_paths) == 1
        assert image_paths[0].startswith(image_analyzer.temp_dir)
        assert image_paths[0].endswith(".png")
        
        # Verify function calls
        mock_process.assert_called_once()
        mock_docx.assert_called_once()

def test_analyze_document_images(image_analyzer, tmp_path):
    """Test document image analysis."""
    # Create a test PDF file
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"fake pdf data")
    
    # Mock image extraction and analysis
    with patch.object(image_analyzer, '_extract_images_from_pdf') as mock_extract, \
         patch.object(image_analyzer, 'analyze_image') as mock_analyze:
        
        mock_extract.return_value = [str(tmp_path / "image1.png")]
        mock_analyze.return_value = ImageAnalysisResult(
            description="Test analysis",
            technical_details="Test details",
            suggestions=["Test suggestion"],
            quality_score=0.8,
            issues=["Test issue"]
        )
        
        # Test document analysis with default options
        results = image_analyzer.analyze_document_images(str(test_pdf))
        
        # Verify results
        assert len(results) == 1
        assert isinstance(results[0], ImageAnalysisResult)
        assert results[0].description == "Test analysis"
        assert results[0].quality_score == 0.8
        
        # Test document analysis with custom options
        custom_options = {
            "preprocessing": {
                "grayscale": False,
                "threshold": False,
                "denoise": False,
                "resize": True,
                "max_size": 2048
            },
            "analysis_type": "security",
            "focus_areas": ["security", "compliance"],
            "quality_threshold": 0.9
        }
        results = image_analyzer.analyze_document_images(str(test_pdf), custom_options)
        
        # Verify function calls
        mock_extract.assert_called()
        mock_analyze.assert_called()

def test_analyze_document_images_unsupported_format(image_analyzer, tmp_path):
    """Test document analysis with unsupported format."""
    # Create a test file with unsupported format
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    # Test analysis
    with pytest.raises(ValueError, match="Unsupported document type"):
        image_analyzer.analyze_document_images(str(test_file))

def test_cleanup_temp_files(image_analyzer, tmp_path):
    """Test cleanup of temporary files."""
    # Create some temporary files
    temp_file = os.path.join(image_analyzer.temp_dir, "test.txt")
    with open(temp_file, "w") as f:
        f.write("test content")
    
    # Call cleanup
    image_analyzer.__del__()
    
    # Verify files are cleaned up
    assert not os.path.exists(image_analyzer.temp_dir) 