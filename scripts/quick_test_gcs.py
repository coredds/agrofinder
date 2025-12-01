"""
Teste rápido de permissões GCS
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import storage
from backend.config import settings

print("🔍 Testando permissões GCS...")
print(f"📦 Bucket: gs://{settings.gcs_bucket_name}")
print()

try:
    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket_name)
    
    # Teste 1: Leitura
    print("1️⃣  Testando LEITURA...", end=" ")
    blobs = list(bucket.list_blobs(max_results=1))
    print("✅")
    
    # Teste 2: Escrita
    print("2️⃣  Testando ESCRITA...", end=" ")
    test_path = f"test/write_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    blob = bucket.blob(test_path)
    blob.upload_from_string("Test write permission")
    print("✅")
    
    # Teste 3: Exclusão
    print("3️⃣  Testando EXCLUSÃO...", end=" ")
    blob.delete()
    print("✅")
    
    print()
    print("🎉 Todas as permissões OK!")
    print("   ✅ Leitura")
    print("   ✅ Escrita")
    print("   ✅ Exclusão")
    print()
    print("🚀 A aplicação pode fazer upload normalmente!")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print()
    print("💡 Execute: gcloud auth application-default login")
    print("   Conta: david.duarte@outlook.com")
    sys.exit(1)

