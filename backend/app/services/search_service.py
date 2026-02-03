from typing import List, Dict, Optional
from app.services.vectorstore import VectorStoreService
from app.services.embedding import EmbeddingService
from app.services.ollama_service import OllamaService

class SearchService:
    """Handles semantic search and query processing"""
    
    def __init__(
        self,
        vectorstore: VectorStoreService,
        embedding_service: EmbeddingService,
        ollama_service: OllamaService
    ):
        self.vectorstore = vectorstore
        self.embedding_service = embedding_service
        self.ollama_service = ollama_service
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Perform semantic search"""
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Search in vector store
        results = self.vectorstore.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and len(results["documents"]) > 0:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "chunk_id": results["ids"][0][i],
                    "filename": results["metadatas"][0][i].get("filename", "Unknown"),
                    "chunk_index": results["metadatas"][0][i].get("chunk_index", 0),
                    "doc_type": results["metadatas"][0][i].get("doc_type", "unknown")
                })
        
        return formatted_results
    
    async def ask_question(
        self,
        query: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Ask a question and get LLM-powered answer with citations"""
        
        # Search for relevant chunks
        search_results = await self.search(query, top_k)
        
        if not search_results:
            return {
                "answer": "I couldn't find any relevant information in the documentation to answer your question.",
                "sources": [],
                "query": query
            }
        
        # Generate answer using Ollama
        answer = await self.ollama_service.generate_response(
            query=query,
            context_chunks=search_results,
            conversation_history=conversation_history
        )
        
        # Format sources
        sources = [
            {
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "text_preview": result["text"][:200] + "...",
                "relevance_score": 1 - result["distance"]  # Convert distance to similarity
            }
            for result in search_results
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "query": query,
            "num_sources": len(sources)
        }
