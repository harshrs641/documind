from fastapi import APIRouter, HTTPException, Depends
from app.services.search_service import SearchService
from app.services.vectorstore import VectorStoreService
from app.services.embedding import EmbeddingService
from app.services.ollama_service import OllamaService
from app.models.schemas import SearchRequest, SearchResponse, QuestionRequest, QuestionResponse
from app.config import get_settings, Settings

router = APIRouter(prefix="/search", tags=["search"])

def get_search_service():
    settings = get_settings()
    vectorstore = VectorStoreService(settings.chroma_persist_directory)
    embedding_service = EmbeddingService(settings.embedding_model)
    ollama_service = OllamaService()
    return SearchService(vectorstore, embedding_service, ollama_service)

@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Perform semantic search across indexed documents
    Returns relevant chunks without LLM processing
    """
    try:
        results = await search_service.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        formatted_results = [
            {
                "text": r["text"],
                "filename": r["filename"],
                "chunk_index": r["chunk_index"],
                "doc_type": r["doc_type"],
                "relevance_score": 1 - r["distance"],
                "text_preview": r["text"][:200] + "..."
            }
            for r in results
        ]
        
        return SearchResponse(
            results=formatted_results,
            query=request.query,
            total_results=len(formatted_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Ask a question and get an AI-powered answer with citations
    Uses Ollama for response generation
    """
    try:
        # Check if Ollama is available
        ollama_available = await search_service.ollama_service.check_health()
        if not ollama_available:
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available. Make sure Ollama is running with 'ollama serve' and the model is pulled."
            )
        
        result = await search_service.ask_question(
            query=request.query,
            top_k=request.top_k,
            conversation_history=request.conversation_history
        )
        
        return QuestionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/health")
async def check_search_health(search_service: SearchService = Depends(get_search_service)):
    """Check if search services are healthy"""
    ollama_status = await search_service.ollama_service.check_health()
    collection_stats = search_service.vectorstore.get_collection_stats()
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama_available": ollama_status,
        "indexed_chunks": collection_stats["total_chunks"],
        "embedding_model": "all-MiniLM-L6-v2"
    }
