import pytest
from pathlib import Path
from document_parser import DocumentParser

@pytest.fixture
def parser():
    return DocumentParser()

def test_detect_file_type(parser, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    mime_type = parser.detect_file_type(test_file)
    assert mime_type.startswith("text/")

def test_parse_text(parser, tmp_path):
    # Create a test text file
    test_file = tmp_path / "test.txt"
    content = "Line 1\nLine 2\nLine 3"
    test_file.write_text(content)
    
    parsed_content = parser.parse_text(test_file)
    assert parsed_content == content

def test_parse_markdown(parser, tmp_path):
    # Create a test markdown file
    test_file = tmp_path / "test.md"
    content = "# Title\n\n## Subtitle\n\nSome text"
    test_file.write_text(content)
    
    parsed_content = parser.parse_markdown(test_file)
    assert "Title" in parsed_content
    assert "Subtitle" in parsed_content
    assert "Some text" in parsed_content

def test_file_not_found(parser):
    with pytest.raises(FileNotFoundError):
        parser.parse_document("nonexistent_file.txt")

def test_unsupported_file_type(parser, tmp_path):
    # Create a test file with an unsupported extension
    test_file = tmp_path / "test.xyz"
    test_file.write_text("Test content")
    
    with pytest.raises(ValueError):
        parser.parse_document(test_file) 