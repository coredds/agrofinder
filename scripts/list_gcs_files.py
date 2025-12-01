"""
Script para listar arquivos no bucket GCS
"""
import sys
import os

# Adicionar parent directory ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import storage
from backend.config import settings


def list_files():
    """Lista todos os arquivos no bucket"""
    
    print("=" * 70)
    print("🌾 AgroFinder - Arquivos no GCS")
    print("=" * 70)
    print()
    print(f"📦 Bucket: gs://{settings.gcs_bucket_name}")
    print()
    
    try:
        # Inicializar cliente
        client = storage.Client()
        bucket = client.bucket(settings.gcs_bucket_name)
        
        # Organizar por pasta
        folders = {}
        
        # Listar todos os blobs
        blobs = list(bucket.list_blobs())
        
        if not blobs:
            print("⚠️  Bucket vazio!")
            return
        
        # Agrupar por pasta
        for blob in blobs:
            parts = blob.name.split('/')
            folder = parts[0] if len(parts) > 1 else 'root'
            
            if folder not in folders:
                folders[folder] = []
            
            folders[folder].append(blob)
        
        # Mostrar por pasta
        for folder, files in sorted(folders.items()):
            print(f"\n📁 {folder}/")
            print("-" * 70)
            
            for blob in files:
                # Tamanho em MB
                size_mb = blob.size / (1024 * 1024)
                
                # Nome do arquivo (sem caminho da pasta)
                filename = blob.name.split('/')[-1]
                
                if filename:  # Ignorar "pastas" vazias
                    print(f"   📄 {filename}")
                    print(f"      Tamanho: {size_mb:.2f} MB")
                    print(f"      Caminho completo: {blob.name}")
                    print(f"      URL: gs://{settings.gcs_bucket_name}/{blob.name}")
                    print()
        
        # Resumo
        total_files = sum(len([f for f in files if f.name.split('/')[-1]]) for files in folders.values())
        total_size = sum(blob.size for blob in blobs) / (1024 * 1024)
        
        print("=" * 70)
        print("📊 RESUMO")
        print("=" * 70)
        print(f"Total de arquivos: {total_files}")
        print(f"Tamanho total: {total_size:.2f} MB")
        print()
        
        # Sugestões de ingestão
        pdf_files = [blob for blob in blobs if blob.name.endswith('.pdf')]
        
        if pdf_files:
            print("💡 SUGESTÕES PARA INGESTÃO:")
            print("-" * 70)
            print()
            print("Para ingerir um arquivo específico, use:")
            print()
            
            for blob in pdf_files[:3]:  # Mostrar apenas 3 exemplos
                category = "anuncio" if "anuncio" in blob.name else "organico" if "organico" in blob.name else "relatorio"
                print(f"python scripts/test_ingest_gcs.py {blob.name} {category}")
            
            if len(pdf_files) > 3:
                print(f"\n... e mais {len(pdf_files) - 3} arquivo(s)")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        print()
        print("Verifique:")
        print("1. Você executou: gcloud auth application-default login")
        print("2. O bucket 'agrofinder' existe e você tem acesso")
        print("3. Suas credenciais estão corretas")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_files()

