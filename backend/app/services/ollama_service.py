import httpx
from typing import List, Dict, Optional
import json

class OllamaService:
    """Handles interaction with Ollama for LLM responses"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate_response(
        self,
        query: str,
        context_chunks: List[Dict],
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate response using Ollama with context"""
        
        # Build context from retrieved chunks
        context_text = "\n\n".join([
            f"[Source: {chunk['filename']}, chunk {chunk['chunk_index']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Create prompt with context
        system_prompt = """You are a helpful technical documentation assistant. 
Answer questions based ONLY on the provided context from the documentation.
Always cite your sources by mentioning the filename and providing direct quotes.
If the answer is not in the context, say so clearly.
Be concise but thorough."""
        
        user_prompt = f"""Context from documentation:
{context_text}

Question: {query}

Answer the question using ONLY the information from the context above. 
Include citations to specific files and sections."""
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_prompt})
        
        # Call Ollama API
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Error calling Ollama: {str(e)}")
    
    async def check_health(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model in model.get("name", "") for model in models)
            return False
        except:
            return False
