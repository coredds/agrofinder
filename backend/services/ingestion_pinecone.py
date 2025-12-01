"""
Serviço de ingestão de documentos PDF usando Pinecone
"""
import pdfplumber
import logging
from typing import List, Dict, Tuple
from io import BytesIO
from datetime import datetime
import hashlib

from backend.config import settings
from backend.services.openai_client import openai_client
from backend.services.gcs_client import gcs_client
from backend.services.pinecone_client import pinecone_client
from backend.models.schemas import DocumentCategory

logger = logging.getLogger(__name__)


class IngestionServicePinecone:
    """Serviço para processamento e ingestão de PDFs no Pinecone"""
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> List[Tuple[int, str]]:
        """
        Extrai texto de PDF usando pdfplumber
        
        Args:
            pdf_bytes: Conteúdo binário do PDF
            
        Returns:
            Lista de tuplas (número_página, texto)
        """
        pages_text = []
        
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_text.append((i, text.strip()))
            
            logger.info(f"Texto extraído de {len(pages_text)} páginas")
            return pages_text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Divide texto em chunks para melhor indexação
        
        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho aproximado de cada chunk (em caracteres)
            overlap: Sobreposição entre chunks
            
        Returns:
            Lista de chunks de texto
        """
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap
        
        # Dividir por palavras para não quebrar no meio das palavras
        words = text.split()
        chunks = []
        
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 para o espaço
            
            if current_size >= chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                
                # Manter overlap de palavras
                overlap_words = int(len(current_chunk) * (overlap / chunk_size))
                current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                current_size = sum(len(w) + 1 for w in current_chunk)
        
        # Adicionar último chunk se houver
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def generate_document_id(self, filename: str, category: str) -> str:
        """
        Gera ID único para documento
        
        Args:
            filename: Nome do arquivo
            category: Categoria do documento
            
        Returns:
            ID único
        """
        timestamp = datetime.now().isoformat()
        hash_input = f"{filename}_{category}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def ingest_pdf(
        self, 
        gcs_path: str, 
        category: DocumentCategory,
        metadata: Dict = None
    ) -> Tuple[str, int]:
        """
        Processa e indexa um PDF do GCS no Pinecone
        
        Args:
            gcs_path: Caminho do PDF no GCS
            category: Categoria do documento
            metadata: Metadados adicionais
            
        Returns:
            Tupla (document_id, número_de_chunks)
        """
        try:
            # 1. Download do PDF do GCS
            logger.info(f"Baixando PDF de: {gcs_path}")
            pdf_bytes = await gcs_client.download_file(gcs_path)
            
            # 2. Extrair texto
            logger.info("Extraindo texto do PDF...")
            pages_text = self.extract_text_from_pdf(pdf_bytes)
            
            if not pages_text:
                raise ValueError("Nenhum texto foi extraído do PDF")
            
            # 3. Gerar ID do documento
            filename = gcs_path.split('/')[-1]
            document_id = self.generate_document_id(filename, category.value)
            
            # 4. Processar cada página
            all_chunks = []
            chunk_metadatas = []
            chunk_ids = []
            
            for page_num, page_text in pages_text:
                # Dividir página em chunks
                chunks = self.chunk_text(page_text)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_page{page_num}_chunk{i}"
                    chunk_ids.append(chunk_id)
                    all_chunks.append(chunk)
                    
                    chunk_metadata = {
                        "document_id": document_id,
                        "filename": filename,
                        "category": category.value,
                        "page_number": page_num,
                        "chunk_index": i,
                        "gcs_path": gcs_path,
                        "upload_date": datetime.now().isoformat(),
                        "text": chunk,  # Pinecone: texto vai no metadata
                        **(metadata or {})
                    }
                    chunk_metadatas.append(chunk_metadata)
            
            # 5. Gerar embeddings em batch
            logger.info(f"Gerando embeddings para {len(all_chunks)} chunks...")
            embeddings = await openai_client.create_embeddings_batch(all_chunks)
            
            # 6. Preparar vetores para Pinecone
            # Formato: [(id, embedding, metadata), ...]
            vectors = []
            for chunk_id, embedding, chunk_metadata in zip(chunk_ids, embeddings, chunk_metadatas):
                vectors.append((chunk_id, embedding, chunk_metadata))
            
            # 7. Upsert no Pinecone
            logger.info(f"Armazenando no Pinecone...")
            pinecone_client.upsert_vectors(vectors)
            
            logger.info(f"Documento {filename} indexado com sucesso: {len(all_chunks)} chunks")
            return document_id, len(all_chunks)
            
        except Exception as e:
            logger.error(f"Erro durante ingestão: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """
        Retorna estatísticas do Pinecone
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            return pinecone_client.get_index_stats()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"total_vectors": 0, "error": str(e)}


# Singleton instance
ingestion_service_pinecone = IngestionServicePinecone()

