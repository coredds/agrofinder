"""
Modelos Pydantic para API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentCategory(str, Enum):
    """Categorias de documentos"""
    ANUNCIO = "anuncio"
    ORGANICO = "organico"


class DocumentMetadata(BaseModel):
    """Metadados do documento"""
    filename: str
    category: DocumentCategory
    upload_date: datetime
    file_size: Optional[int] = None
    num_pages: Optional[int] = None


class SearchRequest(BaseModel):
    """Request para busca semântica"""
    query: str = Field(..., min_length=1, description="Query de busca em linguagem natural")
    category: Optional[DocumentCategory] = Field(None, description="Filtro por categoria")
    top_k: Optional[int] = Field(10, ge=1, le=50, description="Número de resultados a retornar")
    date_from: Optional[datetime] = Field(None, description="Filtrar documentos a partir desta data")
    date_to: Optional[datetime] = Field(None, description="Filtrar documentos até esta data")


class SearchResult(BaseModel):
    """Resultado de busca individual"""
    document_id: str
    filename: str
    category: DocumentCategory
    chunk_text: str
    similarity_score: float
    upload_date: datetime
    page_number: Optional[int] = None
    gcs_url: str


class SearchResponse(BaseModel):
    """Response da busca semântica"""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float


class IngestRequest(BaseModel):
    """Request para ingestão manual de PDF"""
    gcs_path: str = Field(..., description="Caminho do PDF no GCS (ex: pdfs/documento.pdf)")
    category: DocumentCategory
    metadata: Optional[dict] = None


class IngestResponse(BaseModel):
    """Response da ingestão"""
    success: bool
    document_id: str
    filename: str
    num_chunks: int
    message: str


class UploadResponse(BaseModel):
    """Response do upload de PDF"""
    success: bool
    gcs_path: str
    filename: str
    file_size: int
    message: str


class HealthResponse(BaseModel):
    """Response do health check"""
    status: str
    environment: str
    chromadb_status: str
    total_documents: int
    timestamp: datetime

