"""
Configurações da aplicação AgroFinder
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações gerais da aplicação"""
    
    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o"
    
    # Google Cloud Storage
    gcs_bucket_name: str
    gcs_project_id: Optional[str] = None  # Opcional se usar ADC
    
    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "agrofinder"
    pinecone_environment: str = "us-east-1"  # Free tier (AWS)
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    
    # Search
    top_k_results: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()

