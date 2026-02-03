from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingService:
    """Handles text embedding generation"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

