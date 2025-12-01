"""
Cliente Pinecone para vector search
"""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
import logging
from datetime import datetime
import time

from backend.config import settings

logger = logging.getLogger(__name__)


class PineconeClient:
    """Cliente para interação com Pinecone Vector Database"""
    
    def __init__(self):
        """Inicializa cliente Pinecone"""
        try:
            logger.info(f"🔌 Inicializando Pinecone client para região: {settings.pinecone_environment}")
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index_name = settings.pinecone_index_name
            self.dimension = 1536  # OpenAI text-embedding-3-small
            self._index = None
            logger.info("✅ Pinecone client inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Pinecone: {e}")
            raise
    
    @property
    def index(self):
        """Lazy loading do index"""
        if self._index is None:
            # Verificar se index existe, senão criar
            existing_indexes = self.pc.list_indexes()
            
            if self.index_name not in [idx['name'] for idx in existing_indexes]:
                logger.info(f"Criando index Pinecone: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Index {self.index_name} criado com sucesso")
            
            self._index = self.pc.Index(self.index_name)
            logger.info(f"Conectado ao index: {self.index_name}")
        
        return self._index
    
    def upsert_vectors(
        self,
        vectors: List[tuple]
    ) -> Dict:
        """
        Insere ou atualiza vetores no Pinecone
        
        Args:
            vectors: Lista de tuplas (id, embedding, metadata)
            
        Returns:
            Resposta do Pinecone
        """
        try:
            response = self.index.upsert(vectors=vectors)
            logger.info(f"Upsert de {len(vectors)} vetores realizado com sucesso")
            return response
        except Exception as e:
            logger.error(f"Erro ao fazer upsert no Pinecone: {e}")
            raise
    
    def query(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict] = None,
        include_metadata: bool = True,
        timeout: int = 30
    ) -> Dict:
        """
        Busca vetores similares no Pinecone
        
        Args:
            query_vector: Vetor de embedding da query
            top_k: Número de resultados
            filter: Filtros de metadata
            include_metadata: Se deve incluir metadata nos resultados
            timeout: Timeout em segundos
            
        Returns:
            Resultados da busca
        """
        try:
            logger.info(f"🔍 Iniciando query no Pinecone (top_k={top_k})...")
            start_time = time.time()
            
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter,
                include_metadata=include_metadata,
                include_values=False  # Não precisamos dos vetores de volta
            )
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Query retornou {len(results.get('matches', []))} resultados em {elapsed:.2f}s")
            return results
        except Exception as e:
            logger.error(f"❌ Erro ao fazer query no Pinecone: {type(e).__name__}: {str(e)}")
            raise
    
    def delete(self, ids: List[str]) -> Dict:
        """
        Deleta vetores por ID
        
        Args:
            ids: Lista de IDs para deletar
            
        Returns:
            Resposta do Pinecone
        """
        try:
            response = self.index.delete(ids=ids)
            logger.info(f"Deletados {len(ids)} vetores")
            return response
        except Exception as e:
            logger.error(f"Erro ao deletar do Pinecone: {e}")
            raise
    
    def delete_all(self, namespace: Optional[str] = None) -> Dict:
        """
        Deleta todos os vetores (use com cuidado!)
        
        Args:
            namespace: Namespace específico (opcional)
            
        Returns:
            Resposta do Pinecone
        """
        try:
            response = self.index.delete(delete_all=True, namespace=namespace or "")
            logger.warning("Todos os vetores foram deletados do index")
            return response
        except Exception as e:
            logger.error(f"Erro ao deletar todos os vetores: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """
        Retorna estatísticas do index
        
        Returns:
            Estatísticas do index
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "namespaces": stats.get("namespaces", {})
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise


# Singleton instance
pinecone_client = PineconeClient()

