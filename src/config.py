from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Qdrant config
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # Collection names
    collection_name: str = "biotech_documents"
    
    # Chunking settings
    chunk_size_meeting_minutes: int = 300
    chunk_size_progress_report: int = 500
    chunk_size_research_paper: int = 1000
    
    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    
    # FastAPI settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Search settings
    top_k: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
