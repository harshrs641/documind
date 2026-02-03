from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "DocuMind API"
    chroma_persist_directory: str = "./chroma_db"
    upload_directory: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()