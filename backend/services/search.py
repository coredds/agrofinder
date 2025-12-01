"""
Serviço de busca semântica
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings
from backend.services.openai_client import openai_client
from backend.models.schemas import SearchResult, DocumentCategory

logger = logging.getLogger(__name__)


class SearchService:
    """Serviço para busca semântica usando ChromaDB"""
    
    def __init__(self):
        self._chroma_client = None
        self._collection = None
    
    @property
    def chroma_client(self):
        """Lazy loading do cliente ChromaDB"""
        if self._chroma_client is None:
            logger.info("Inicializando ChromaDB client...")
            self._chroma_client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=False,
                    # Otimizações de performance
                    chroma_api_impl="chromadb.api.segment.SegmentAPI",
                    chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
                    persist_directory=settings.chroma_db_path,
                )
            )
            logger.info("ChromaDB client inicializado")
        return self._chroma_client
    
    @property
    def collection(self):
        """Lazy loading da collection"""
        if self._collection is None:
            logger.info("Carregando collection...")
            try:
                self._collection = self.chroma_client.get_collection(
                    name=settings.chroma_collection_name
                )
                count = self._collection.count()
                logger.info(f"Collection carregada com {count} documentos")
            except Exception:
                logger.warning("Collection não existe, criando nova...")
                self._collection = self.chroma_client.create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
        return self._collection
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[DocumentCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[SearchResult]:
        """
        Realiza busca semântica
        
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
            
            # 2. Preparar filtros
            where_filter = self._build_filters(category, date_from, date_to)
            if where_filter:
                logger.info(f"🔎 Filtros aplicados: {where_filter}")
            
            # 3. Buscar no ChromaDB
            logger.info(f"📊 Buscando no ChromaDB (top_k={top_k})...")
            chroma_start = time.time()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            chroma_time = time.time() - chroma_start
            logger.info(f"⏱️  Busca no ChromaDB em {chroma_time:.2f}s")
            
            # 4. Processar resultados
            process_start = time.time()
            search_results = self._process_results(results)
            process_time = time.time() - process_start
            
            total_time = time.time() - start_time
            logger.info(f"✅ {len(search_results)} resultados em {total_time:.2f}s total")
            logger.info(f"   └─ Embedding: {embed_time:.2f}s | ChromaDB: {chroma_time:.2f}s | Processamento: {process_time:.2f}s")
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Erro durante busca: {e}")
            raise
    
    def _build_filters(
        self,
        category: Optional[DocumentCategory],
        date_from: Optional[datetime],
        date_to: Optional[datetime]
    ) -> Optional[Dict]:
        """
        Constrói filtros para ChromaDB
        
        Args:
            category: Filtro de categoria
            date_from: Data inicial
            date_to: Data final
            
        Returns:
            Dicionário de filtros ou None
        """
        filters = {}
        
        if category:
            filters["category"] = category.value
        
        # ChromaDB tem suporte limitado para filtros de data complexos
        # Para simplificar, vamos apenas filtrar por categoria por enquanto
        # Filtros de data podem ser aplicados após a busca
        
        return filters if filters else None
    
    def _process_results(self, chroma_results: Dict) -> List[SearchResult]:
        """
        Processa resultados do ChromaDB para formato da API
        
        Args:
            chroma_results: Resultados brutos do ChromaDB
            
        Returns:
            Lista de SearchResult
        """
        search_results = []
        
        # ChromaDB retorna resultados em listas aninhadas
        documents = chroma_results.get("documents", [[]])[0]
        metadatas = chroma_results.get("metadatas", [[]])[0]
        distances = chroma_results.get("distances", [[]])[0]
        
        for doc, metadata, distance in zip(documents, metadatas, distances):
            # Converter distância para similaridade (0-1)
            # ChromaDB usa distância cosine, então 1 - distance = similaridade
            similarity = 1 - distance if distance is not None else 0
            
            # Converter GCS path para URL da API
            gcs_path = metadata.get("gcs_path", "")
            api_url = f"/api/document/{gcs_path}" if gcs_path else ""
            
            result = SearchResult(
                document_id=metadata.get("document_id", ""),
                filename=metadata.get("filename", ""),
                category=DocumentCategory(metadata.get("category", "anuncio")),
                chunk_text=doc,
                similarity_score=round(similarity, 4),
                upload_date=datetime.fromisoformat(metadata.get("upload_date", datetime.now().isoformat())),
                page_number=metadata.get("page_number"),
                gcs_url=api_url
            )
            search_results.append(result)
        
        return search_results
    
    def get_document_count(self) -> int:
        """
        Retorna número total de chunks indexados
        
        Returns:
            Número de chunks
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Erro ao contar documentos: {e}")
            return 0


# Singleton instance
search_service = SearchService()

