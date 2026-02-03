from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import aiofiles
from pathlib import Path
import uuid

from app.services.document_service import DocumentIngestionService
from app.models.schemas import DocumentUploadResponse
from app.config import get_settings, Settings

router = APIRouter(prefix="/documents", tags=["documents"])

# Dependency to get document service
def get_document_service():
    return DocumentIngestionService()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    doc_service: DocumentIngestionService = Depends(get_document_service)
):
    """
    Upload and ingest a document
    
    Supported formats: .md, .txt, .pdf, .py, .js, .ts, .java, etc.
    """
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / 1024 / 1024}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid collisions
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Ingest document
        result = await doc_service.ingest_document(
            file_path=str(file_path),
            filename=file.filename,
            file_size=file_size
        )
        
        # Clean up uploaded file after processing
        os.remove(file_path)
        
        return result
        
    except ValueError as e:
        # Clean up file on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/stats")
async def get_stats(doc_service: DocumentIngestionService = Depends(get_document_service)):
    """Get statistics about indexed documents"""
    stats = doc_service.vectorstore.get_collection_stats()
    return stats
