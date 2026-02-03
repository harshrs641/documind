from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
    MarkdownTextSplitter
)
from typing import List
from app.models.schemas import DocumentType

class DocumentChunker:
    """Handles intelligent document chunking based on type"""
    
    # Language mapping for code files
    LANGUAGE_MAP = {
        DocumentType.PYTHON: Language.PYTHON,
        DocumentType.JAVASCRIPT: Language.JS,
        DocumentType.TYPESCRIPT: Language.TS,
        DocumentType.JAVA: Language.JAVA,
    }
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, text: str, doc_type: DocumentType) -> List[str]:
        """Chunk document based on type"""
        
        # Markdown files
        if doc_type == DocumentType.MARKDOWN:
            splitter = MarkdownTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            return splitter.split_text(text)
        
        # Code files with language-specific splitting
        if doc_type in self.LANGUAGE_MAP:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=self.LANGUAGE_MAP[doc_type],
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            return splitter.split_text(text)
        
        # Default text splitting
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)

