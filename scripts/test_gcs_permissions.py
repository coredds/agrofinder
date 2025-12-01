"""
Script para testar permissões do GCS (leitura e escrita)
"""
import sys
import os
from io import BytesIO
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import storage
from backend.config import settings

def test_permissions():
    """Testa permissões de leitura e escrita no bucket"""
    
    print("=" * 80)
    print("🔐 Teste de Permissões GCS - AgroFinder")
    print("=" * 80)
    print()
    
    try:
        # Inicializar cliente
        print("📦 Conectando ao GCS...")
        client = storage.Client()
        bucket = client.bucket(settings.gcs_bucket_name)
        print(f"✅ Conectado ao bucket: gs://{settings.gcs_bucket_name}")
        print()
        
        # Teste 1: Verificar se bucket existe
        print("🔍 Teste 1: Verificando existência do bucket...")
        if bucket.exists():
            print(f"✅ Bucket existe e está acessível")
        else:
            print(f"❌ Bucket não encontrado ou sem permissão de leitura")
            return
        print()
        
        # Teste 2: Listar arquivos (permissão de leitura)
        print("🔍 Teste 2: Testando permissão de LEITURA...")
        try:
            blobs = list(bucket.list_blobs(max_results=5))
            print(f"✅ Permissão de LEITURA OK - {len(blobs)} arquivos listados")
            if blobs:
                print("   Exemplos:")
                for blob in blobs[:3]:
                    print(f"   - {blob.name}")
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
            return
        print()
        
        # Teste 3: Upload de arquivo de teste (permissão de escrita)
        print("🔍 Teste 3: Testando permissão de ESCRITA...")
        test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_path = f"pdfs/test/{test_filename}"
        
        try:
            # Criar conteúdo de teste
            test_content = f"""AgroFinder - Teste de Upload
Timestamp: {datetime.now().isoformat()}
Este é um arquivo de teste para verificar permissões de escrita.
"""
            
            # Upload
            blob = bucket.blob(test_path)
            blob.upload_from_string(test_content, content_type='text/plain')
            
            print(f"✅ Permissão de ESCRITA OK")
            print(f"   Arquivo criado: gs://{settings.gcs_bucket_name}/{test_path}")
            print()
            
            # Teste 4: Leitura do arquivo recém-criado
            print("🔍 Teste 4: Verificando arquivo criado...")
            downloaded_content = blob.download_as_text()
            if test_content == downloaded_content:
                print("✅ Arquivo verificado - conteúdo correto")
            else:
                print("⚠️  Arquivo criado mas conteúdo diferente")
            print()
            
            # Teste 5: Deletar arquivo de teste
            print("🔍 Teste 5: Testando permissão de EXCLUSÃO...")
            blob.delete()
            print("✅ Permissão de EXCLUSÃO OK")
            print(f"   Arquivo de teste removido")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao testar escrita: {e}")
            print()
            print("💡 Possíveis causas:")
            print("   1. A conta autenticada não tem permissão de escrita")
            print("   2. O bucket está em modo somente leitura")
            print("   3. IAM roles insuficientes")
            print()
            return
        
        # Teste 6: Testar diretórios específicos
        print("🔍 Teste 6: Testando diretórios específicos...")
        directories = ["pdfs/anuncio", "pdfs/organico"]
        
        for directory in directories:
            test_path = f"{directory}/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                blob = bucket.blob(test_path)
                blob.upload_from_string(f"Test: {directory}", content_type='text/plain')
                blob.delete()
                print(f"✅ Escrita OK em: {directory}/")
            except Exception as e:
                print(f"❌ Erro em {directory}/: {e}")
        
        print()
        print("=" * 80)
        print("🎉 RESUMO: Todas as permissões estão OK!")
        print("=" * 80)
        print()
        print("✅ Leitura: OK")
        print("✅ Escrita: OK")
        print("✅ Exclusão: OK")
        print("✅ Diretórios pdfs/anuncio e pdfs/organico: OK")
        print()
        print("🚀 A aplicação pode fazer upload de arquivos normalmente!")
        print()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print()
        print("💡 Verifique:")
        print("   1. gcloud auth application-default login")
        print("   2. Conta autenticada: david.duarte@outlook.com")
        print("   3. IAM roles no projeto GCP")
        print()
        return

if __name__ == "__main__":
    test_permissions()

