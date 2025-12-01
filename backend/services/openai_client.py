"""
Cliente OpenAI para embeddings e chat
"""
from openai import OpenAI
from typing import List
import logging
from backend.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Cliente para interação com OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.openai_embedding_model
        self.chat_model = settings.openai_chat_model
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Cria embedding para um texto usando OpenAI
        
        Args:
            text: Texto para criar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        try:
            logger.info(f"🤖 Chamando OpenAI API para embedding ({len(text)} caracteres)...")
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                timeout=60  # Timeout de 60s para OpenAI
            )
            logger.info(f"✅ Embedding recebido da OpenAI")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Erro ao criar embedding: {e}")
            raise
    
    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Cria embeddings para múltiplos textos em batch
        
        Args:
            texts: Lista de textos para criar embeddings
            
        Returns:
            Lista de embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Erro ao criar embeddings em batch: {e}")
            raise
    
    async def rerank_results(self, query: str, results: List[str]) -> List[int]:
        """
        Rerank resultados usando GPT-4o (opcional, para melhorar relevância)
        
        Args:
            query: Query original do usuário
            results: Lista de textos dos resultados
            
        Returns:
            Lista de índices ordenados por relevância
        """
        # Implementação simplificada - pode ser expandida futuramente
        # Por enquanto, retorna a ordem original
        return list(range(len(results)))


# Singleton instance
openai_client = OpenAIClient()

