import os
import uuid
from typing import List
from datetime import datetime
from app.services.file_processor import FileProcessor
from app.services.chunking import DocumentChunker
from app.services.embedding import EmbeddingService
from app.services.vectorstore import VectorStoreService
from app.models.schemas import DocumentUploadResponse, DocumentType
from app.config import get_settings

class DocumentIngestionService:
    """Orchestrates the document ingestion pipeline"""
    
    def __init__(self):
        settings = get_settings()
        self.file_processor = FileProcessor()
        self.chunker = DocumentChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.embedding_service = EmbeddingService(settings.embedding_model)
        self.vectorstore = VectorStoreService(settings.chroma_persist_directory)
    
    async def ingest_document(
        self,
        file_path: str,
        filename: str,
        file_size: int
    ) -> DocumentUploadResponse:
        """Complete document ingestion pipeline"""
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Step 1: Detect file type
        file_type = self.file_processor.detect_file_type(filename)
        
        # Step 2: Extract text content
        print(f"Processing file: {filename}")
        text_content = await self.file_processor.process_file(file_path, file_type)
        
        if not text_content or len(text_content.strip()) == 0:
            raise ValueError("No text content could be extracted from the file")
        
        # Step 3: Chunk the document
        print(f"Chunking document into {self.chunker.chunk_size} character chunks...")
        chunks = self.chunker.chunk_document(text_content, file_type)
        
        if not chunks:
            raise ValueError("Failed to create chunks from document")
        
        print(f"Created {len(chunks)} chunks")
        
        # Step 4: Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedding_service.generate_embeddings(chunks)
        
        # Step 5: Store in vector database
        print("Storing in vector database...")
        chunks_stored = self.vectorstore.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=filename,
            doc_type=file_type.value
        )
        
        print(f"Successfully ingested document: {filename}")
        
        return DocumentUploadResponse(
            id=document_id,
            filename=filename,
            file_type=file_type,
            size=file_size,
            chunks_created=chunks_stored,
            upload_time=datetime.now(),
            message=f"Document successfully processed into {chunks_stored} searchable chunks"
        )

