import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class VectorStoreService:
    """Handles ChromaDB operations"""
    
    def __init__(self, persist_directory: str):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        document_id: str,
        filename: str,
        doc_type: str
    ) -> int:
        """Add document chunks to vector store"""
        
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        metadatas = [
            {
                "document_id": document_id,
                "filename": filename,
                "doc_type": doc_type,
                "chunk_index": i,
                "upload_time": datetime.now().isoformat(),
                "text_preview": chunk[:100]
            }
            for i, chunk in enumerate(chunks)
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """Retrieve all chunks for a document"""
        results = self.collection.get(
            where={"document_id": document_id}
        )
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            self.collection.delete(
                where={"document_id": document_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            "total_chunks": self.collection.count(),
            "collection_name": self.collection.name
        }
