import os
import mimetypes
from pathlib import Path
from typing import Tuple
import aiofiles
from pypdf import PdfReader
from app.models.schemas import DocumentType

class FileProcessor:
    """Handles file reading and type detection"""
    
    SUPPORTED_EXTENSIONS = {
        '.md': DocumentType.MARKDOWN,
        '.txt': DocumentType.TXT,
        '.pdf': DocumentType.PDF,
        '.py': DocumentType.PYTHON,
        '.js': DocumentType.JAVASCRIPT,
        '.ts': DocumentType.TYPESCRIPT,
        '.tsx': DocumentType.TYPESCRIPT,
        '.jsx': DocumentType.JAVASCRIPT,
        '.java': DocumentType.JAVA,
        '.go': DocumentType.OTHER,
        '.rs': DocumentType.OTHER,
        '.cpp': DocumentType.OTHER,
        '.c': DocumentType.OTHER,
        '.h': DocumentType.OTHER,
        '.yaml': DocumentType.OTHER,
        '.json': DocumentType.OTHER,
    }
    
    @staticmethod
    def detect_file_type(filename: str) -> DocumentType:
        """Detect document type from filename"""
        ext = Path(filename).suffix.lower()
        return FileProcessor.SUPPORTED_EXTENSIONS.get(ext, DocumentType.OTHER)
    
    @staticmethod
    async def read_text_file(file_path: str) -> str:
        """Read text-based files"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return await f.read()
    
    @staticmethod
    def read_pdf_file(file_path: str) -> str:
        """Read PDF files"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text
    
    @staticmethod
    async def process_file(file_path: str, file_type: DocumentType) -> str:
        """Process file based on type and return text content"""
        if file_type == DocumentType.PDF:
            return FileProcessor.read_pdf_file(file_path)
        else:
            return await FileProcessor.read_text_file(file_path)

