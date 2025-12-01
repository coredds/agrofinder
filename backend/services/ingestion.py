"""
Serviço de ingestão de documentos PDF
"""
import pdfplumber
import logging
from typing import List, Dict, Tuple
from io import BytesIO
from datetime import datetime
import hashlib
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings
from backend.services.openai_client import openai_client
from backend.services.gcs_client import gcs_client
from backend.models.schemas import DocumentCategory

logger = logging.getLogger(__name__)


class IngestionService:
    """Serviço para processamento e ingestão de PDFs"""
    
    def __init__(self):
        self._chroma_client = None
        self._collection = None
    
    @property
    def chroma_client(self):
        """Lazy loading do cliente ChromaDB"""
        if self._chroma_client is None:
            logger.info("Inicializando ChromaDB client para ingestão...")
            self._chroma_client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=False,
                    # Otimizações
                    chroma_api_impl="chromadb.api.segment.SegmentAPI",
                    chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
                )
            )
        return self._chroma_client
    
    @property
    def collection(self):
        """Lazy loading da collection"""
        if self._collection is None:
            self._collection = self.chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
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
        Processa e indexa um PDF do GCS
        
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
                        **(metadata or {})
                    }
                    chunk_metadatas.append(chunk_metadata)
            
            # 5. Gerar embeddings
            logger.info(f"Gerando embeddings para {len(all_chunks)} chunks...")
            embeddings = await openai_client.create_embeddings_batch(all_chunks)
            
            # 6. Upsert no ChromaDB
            logger.info("Armazenando no ChromaDB...")
            self.collection.upsert(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=chunk_metadatas
            )
            
            logger.info(f"Documento {filename} indexado com sucesso: {len(all_chunks)} chunks")
            return document_id, len(all_chunks)
            
        except Exception as e:
            logger.error(f"Erro durante ingestão: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """
        Retorna estatísticas da collection ChromaDB
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.chroma_collection_name
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"total_chunks": 0, "error": str(e)}


# Singleton instance
ingestion_service = IngestionService()

