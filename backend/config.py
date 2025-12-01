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
    
    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "agro_docs"
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    
    # Search
    top_k_results: int = 10
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()

