"""
Cliente Google Cloud Storage
"""
from google.cloud import storage
from typing import Optional, BinaryIO
import logging
from backend.config import settings

logger = logging.getLogger(__name__)


class GCSClient:
    """Cliente para interação com Google Cloud Storage"""
    
    def __init__(self):
        # Usar Application Default Credentials (ADC) do gcloud CLI
        # Não requer credenciais explícitas - usa gcloud auth application-default login
        try:
            self.client = storage.Client(project=settings.gcs_project_id)
        except Exception:
            # Se project_id não estiver configurado, tenta sem especificar
            logger.warning("Inicializando GCS client sem project_id explícito")
            self.client = storage.Client()
        
        self.bucket_name = settings.gcs_bucket_name
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_file(self, file_data: BinaryIO, destination_path: str) -> str:
        """
        Upload de arquivo para GCS
        
        Args:
            file_data: Dados binários do arquivo
            destination_path: Caminho de destino no bucket
            
        Returns:
            URL pública do arquivo
        """
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_file(file_data, rewind=True)
            
            gcs_url = f"gs://{self.bucket_name}/{destination_path}"
            logger.info(f"Arquivo enviado com sucesso: {gcs_url}")
            return gcs_url
        except Exception as e:
            logger.error(f"Erro ao fazer upload para GCS: {e}")
            raise
    
    async def download_file(self, source_path: str) -> bytes:
        """
        Download de arquivo do GCS
        
        Args:
            source_path: Caminho do arquivo no bucket
            
        Returns:
            Conteúdo binário do arquivo
        """
        try:
            blob = self.bucket.blob(source_path)
            content = blob.download_as_bytes()
            logger.info(f"Arquivo baixado com sucesso: {source_path}")
            return content
        except Exception as e:
            logger.error(f"Erro ao fazer download do GCS: {e}")
            raise
    
    async def file_exists(self, path: str) -> bool:
        """
        Verifica se um arquivo existe no GCS
        
        Args:
            path: Caminho do arquivo no bucket
            
        Returns:
            True se existe, False caso contrário
        """
        try:
            blob = self.bucket.blob(path)
            return blob.exists()
        except Exception as e:
            logger.error(f"Erro ao verificar existência do arquivo: {e}")
            return False
    
    def get_public_url(self, path: str) -> str:
        """
        Retorna URL pública do arquivo
        
        Args:
            path: Caminho do arquivo no bucket
            
        Returns:
            URL pública
        """
        return f"gs://{self.bucket_name}/{path}"
    
    async def list_files(self, prefix: Optional[str] = None) -> list:
        """
        Lista arquivos no bucket
        
        Args:
            prefix: Prefixo opcional para filtrar arquivos
            
        Returns:
            Lista de nomes de arquivos
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            raise


# Singleton instance
gcs_client = GCSClient()

