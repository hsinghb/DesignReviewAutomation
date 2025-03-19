import os
from typing import Union
from pathlib import Path
import magic
from docx import Document
from PyPDF2 import PdfReader
import markdown
from bs4 import BeautifulSoup

class DocumentParser:
    """A class to parse different document formats into plain text."""
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
    
    def detect_file_type(self, file_path: Union[str, Path]) -> str:
        """Detect the MIME type of a file."""
        return self.mime.from_file(str(file_path))
    
    def parse_docx(self, file_path: Union[str, Path]) -> str:
        """Parse a DOCX file into plain text."""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def parse_pdf(self, file_path: Union[str, Path]) -> str:
        """Parse a PDF file into plain text."""
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)
    
    def parse_markdown(self, file_path: Union[str, Path]) -> str:
        """Parse a Markdown file into plain text."""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def parse_text(self, file_path: Union[str, Path]) -> str:
        """Parse a plain text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_document(self, file_path: Union[str, Path]) -> str:
        """Parse a document based on its file type."""
        file_path = str(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        mime_type = self.detect_file_type(file_path)
        
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self.parse_docx(file_path)
        elif mime_type == 'application/pdf':
            return self.parse_pdf(file_path)
        elif mime_type == 'text/markdown':
            return self.parse_markdown(file_path)
        elif mime_type.startswith('text/'):
            return self.parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}") 