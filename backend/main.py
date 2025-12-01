"""
FastAPI Application - AgroFinder
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import time
from datetime import datetime
from pathlib import Path

from backend.config import settings
from backend.models.schemas import (
    SearchRequest, SearchResponse, SearchResult,
    IngestRequest, IngestResponse,
    UploadResponse, HealthResponse
)
from backend.services.search_pinecone import search_service_pinecone
from backend.services.ingestion_pinecone import ingestion_service_pinecone
from backend.services.gcs_client import gcs_client

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="AgroFinder API",
    description="API para busca semântica de documentos agro",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização"""
    logger.info("🚀 Iniciando AgroFinder API...")
    logger.info(f"📊 Pinecone Index: {settings.pinecone_index_name}")
    logger.info(f"🌍 Environment: {settings.environment}")
    # Pinecone será inicializado lazy no primeiro uso

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no shutdown"""
    logger.info("👋 Encerrando AgroFinder API...")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - versão rápida"""
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        chromadb_status="pinecone",  # Agora usando Pinecone
        total_documents=0,  # Não consultar Pinecone aqui (pode ser lento)
        timestamp=datetime.now()
    )

@app.get("/api/debug")
async def debug_connections():
    """Endpoint de diagnóstico para verificar conectividade"""
    import os
    import socket
    
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "environment": settings.environment,
        "checks": {}
    }
    
    # Check OpenAI API key
    api_key = settings.openai_api_key
    diagnostics["checks"]["openai_key_length"] = len(api_key) if api_key else 0
    diagnostics["checks"]["openai_key_starts_with"] = api_key[:10] if api_key else "NONE"
    
    # Check Pinecone
    diagnostics["checks"]["pinecone_key_length"] = len(settings.pinecone_api_key) if settings.pinecone_api_key else 0
    diagnostics["checks"]["pinecone_environment"] = settings.pinecone_environment
    
    # Test DNS resolution
    try:
        socket.gethostbyname("api.openai.com")
        diagnostics["checks"]["dns_openai"] = "OK"
    except Exception as e:
        diagnostics["checks"]["dns_openai"] = f"FAIL: {str(e)}"
    
    # Test OpenAI connection
    try:
        from backend.services.openai_client import openai_client
        test_embedding = await openai_client.create_embedding("test")
        diagnostics["checks"]["openai_connection"] = "OK"
        diagnostics["checks"]["embedding_dimension"] = len(test_embedding)
    except Exception as e:
        diagnostics["checks"]["openai_connection"] = f"FAIL: {str(e)}"
    
    return diagnostics

@app.get("/api/stats")
async def get_stats():
    """Retorna estatísticas detalhadas do sistema"""
    try:
        # Consultamos o Pinecone
        stats = ingestion_service_pinecone.get_index_stats()
        return {
            "success": True,
            "total_vectors": stats.get("total_vectors", 0),
            "vector_db": "pinecone",
            "index_name": settings.pinecone_index_name,
            "environment": settings.environment,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Endpoint de busca semântica
    
    Realiza busca semântica nos documentos indexados usando OpenAI embeddings
    e ChromaDB para recuperação de documentos relevantes.
    """
    start_time = time.time()
    
    try:
        # Realizar busca usando Pinecone
        results = await search_service_pinecone.search(
            query=request.query,
            top_k=request.top_k or 10,
            category=request.category,
            date_from=request.date_from,
            date_to=request.date_to
        )
        
        # Calcular tempo de processamento
        processing_time = (time.time() - start_time) * 1000  # em ms
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time_ms=round(processing_time, 2)
        )
    
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao realizar busca: {str(e)}")


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_pdf(request: IngestRequest):
    """
    Endpoint para ingestão manual de PDF do GCS
    
    Processa um PDF já existente no GCS, extrai texto, gera chunks,
    cria embeddings e armazena no ChromaDB.
    """
    try:
        # Verificar se arquivo existe no GCS
        exists = await gcs_client.file_exists(request.gcs_path)
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Arquivo não encontrado no GCS: {request.gcs_path}"
            )
        
        # Processar e indexar PDF no Pinecone
        document_id, num_chunks = await ingestion_service_pinecone.ingest_pdf(
            gcs_path=request.gcs_path,
            category=request.category,
            metadata=request.metadata
        )
        
        filename = request.gcs_path.split('/')[-1]
        
        return IngestResponse(
            success=True,
            document_id=document_id,
            filename=filename,
            num_chunks=num_chunks,
            message=f"PDF indexado com sucesso: {num_chunks} chunks criados"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    category: str = "anuncio"
):
    """
    Endpoint para upload de novo PDF
    
    Faz upload do PDF para o GCS e indexa automaticamente no ChromaDB.
    """
    try:
        # Validar tipo de arquivo
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
        
        # Validar categoria
        from backend.models.schemas import DocumentCategory
        if category == "anuncio":
            doc_category = DocumentCategory.ANUNCIO
        elif category == "organico":
            doc_category = DocumentCategory.ORGANICO
        else:
            raise HTTPException(status_code=400, detail=f"Categoria inválida: {category}")
        
        # Gerar caminho no GCS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gcs_path = f"pdfs/{category}/{timestamp}_{file.filename}"
        
        # Upload para GCS
        content = await file.read()
        file_size = len(content)
        
        from io import BytesIO
        file_data = BytesIO(content)
        gcs_url = await gcs_client.upload_file(file_data, gcs_path)
        
        logger.info(f"✅ Arquivo enviado para GCS: {gcs_path}")
        
        # Indexar automaticamente no Pinecone
        logger.info(f"🔄 Iniciando indexação automática no Pinecone...")
        document_id, num_chunks = await ingestion_service_pinecone.ingest_pdf(
            gcs_path=gcs_path,
            category=doc_category,
            metadata={"indexed_by": "web_upload", "upload_timestamp": timestamp}
        )
        
        logger.info(f"✅ Documento indexado: {num_chunks} chunks criados")
        
        return UploadResponse(
            success=True,
            gcs_path=gcs_path,
            filename=file.filename,
            file_size=file_size,
            message=f"Arquivo enviado e indexado com sucesso! {num_chunks} chunks criados."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload/indexação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")




@app.get("/api/document/{document_path:path}")
async def get_document(document_path: str):
    """
    Serve PDF from GCS
    
    Example: /api/document/anuncios/file.pdf
    """
    try:
        # Download PDF from GCS
        pdf_bytes = await gcs_client.download_file(document_path)
        
        # Return as PDF response
        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={document_path.split('/')[-1]}"
            }
        )
    except Exception as e:
        logger.error(f"Erro ao buscar documento: {e}")
        raise HTTPException(status_code=404, detail=f"Documento não encontrado: {str(e)}")


# Servir frontend (será adicionado após build do React)
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve frontend React"""
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "AgroFinder API - Frontend não encontrado"}
else:
    @app.get("/")
    async def root():
        """Root endpoint quando frontend não está disponível"""
        return {
            "message": "AgroFinder API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

