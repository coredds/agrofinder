"""
Serviço de busca semântica usando Pinecone
"""
import logging
from typing import List, Optional
from datetime import datetime

from backend.config import settings
from backend.services.openai_client import openai_client
from backend.services.pinecone_client import pinecone_client
from backend.models.schemas import SearchResult, DocumentCategory

logger = logging.getLogger(__name__)


class SearchServicePinecone:
    """Serviço para busca semântica usando Pinecone"""
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[DocumentCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[SearchResult]:
        """
        Realiza busca semântica usando Pinecone
        
        Args:
            query: Query de busca em linguagem natural
            top_k: Número de resultados a retornar
            category: Filtro opcional por categoria
            date_from: Filtro opcional de data inicial
            date_to: Filtro opcional de data final
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        try:
            import time
            start_time = time.time()
            
            # 1. Gerar embedding da query
            logger.info(f"🔍 Gerando embedding para query: '{query[:50]}...'")
            embed_start = time.time()
            query_embedding = await openai_client.create_embedding(query)
            embed_time = time.time() - embed_start
            logger.info(f"⏱️  Embedding gerado em {embed_time:.2f}s")
            
            # 2. Preparar filtros Pinecone
            pinecone_filter = self._build_pinecone_filter(category, date_from, date_to)
            if pinecone_filter:
                logger.info(f"🔎 Filtros aplicados: {pinecone_filter}")
            
            # 3. Buscar no Pinecone
            logger.info(f"📊 Buscando no Pinecone (top_k={top_k})...")
            pinecone_start = time.time()
            
            results = pinecone_client.query(
                query_vector=query_embedding,
                top_k=top_k,
                filter=pinecone_filter,
                include_metadata=True
            )
            
            pinecone_time = time.time() - pinecone_start
            logger.info(f"⏱️  Busca no Pinecone em {pinecone_time:.2f}s")
            
            # 4. Processar resultados
            process_start = time.time()
            search_results = self._process_results(results)
            process_time = time.time() - process_start
            
            total_time = time.time() - start_time
            logger.info(f"✅ {len(search_results)} resultados em {total_time:.2f}s total")
            logger.info(f"   └─ Embedding: {embed_time:.2f}s | Pinecone: {pinecone_time:.2f}s | Processamento: {process_time:.2f}s")
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Erro durante busca: {e}")
            raise
    
    def _build_pinecone_filter(
        self,
        category: Optional[DocumentCategory],
        date_from: Optional[datetime],
        date_to: Optional[datetime]
    ) -> Optional[dict]:
        """
        Constrói filtros para Pinecone
        
        Pinecone usa formato:
        {
            "category": {"$eq": "anuncio"},
            "upload_date": {"$gte": "2024-01-01"}
        }
        
        Args:
            category: Filtro de categoria
            date_from: Data inicial
            date_to: Data final
            
        Returns:
            Dicionário de filtros ou None
        """
        filters = {}
        
        if category:
            filters["category"] = {"$eq": category.value}
        
        # Filtros de data (se implementado no metadata)
        if date_from:
            filters["upload_date"] = filters.get("upload_date", {})
            filters["upload_date"]["$gte"] = date_from.isoformat()
        
        if date_to:
            filters["upload_date"] = filters.get("upload_date", {})
            filters["upload_date"]["$lte"] = date_to.isoformat()
        
        return filters if filters else None
    
    def _process_results(self, pinecone_results: dict) -> List[SearchResult]:
        """
        Processa resultados do Pinecone para formato da API
        
        Args:
            pinecone_results: Resultados brutos do Pinecone
            
        Returns:
            Lista de SearchResult
        """
        search_results = []
        
        matches = pinecone_results.get("matches", [])
        
        for match in matches:
            metadata = match.get("metadata", {})
            score = match.get("score", 0.0)
            
            # Converter GCS path para URL da API
            gcs_path = metadata.get("gcs_path", "")
            api_url = f"/api/document/{gcs_path}" if gcs_path else ""
            
            result = SearchResult(
                document_id=metadata.get("document_id", ""),
                filename=metadata.get("filename", ""),
                category=DocumentCategory(metadata.get("category", "anuncio")),
                chunk_text=metadata.get("text", ""),
                similarity_score=round(score, 4),
                upload_date=datetime.fromisoformat(metadata.get("upload_date", datetime.now().isoformat())),
                page_number=metadata.get("page_number"),
                gcs_url=api_url
            )
            search_results.append(result)
        
        return search_results
    
    def get_document_count(self) -> int:
        """
        Retorna número total de vetores indexados
        
        Returns:
            Número de vetores
        """
        try:
            stats = pinecone_client.get_index_stats()
            return stats.get("total_vectors", 0)
        except Exception as e:
            logger.error(f"Erro ao contar documentos: {e}")
            return 0


# Singleton instance
search_service_pinecone = SearchServicePinecone()

