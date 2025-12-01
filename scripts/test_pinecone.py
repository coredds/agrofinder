"""
Script para testar conexão com Pinecone
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.pinecone_client import pinecone_client

print("🧪 Testando conexão com Pinecone...\n")

try:
    # Obter estatísticas do index
    print("📊 Obtendo estatísticas do index...")
    stats = pinecone_client.get_index_stats()
    
    print(f"\n✅ Conexão bem-sucedida!")
    print(f"\n📊 Estatísticas do Index '{pinecone_client.index_name}':")
    print(f"   Total de vetores: {stats.get('total_vectors', 0):,}")
    print(f"   Dimensões: {stats.get('dimension', 0)}")
    print(f"   Index fullness: {stats.get('index_fullness', 0):.2%}")
    
    namespaces = stats.get('namespaces', {})
    if namespaces:
        print(f"\n   Namespaces:")
        for ns, count in namespaces.items():
            print(f"      - {ns or '(default)'}: {count.get('vector_count', 0):,} vetores")
    
    print(f"\n🌍 Index URL: https://app.pinecone.io/")
    print(f"✅ Tudo funcionando corretamente!")
    
except Exception as e:
    print(f"\n❌ Erro ao conectar no Pinecone: {e}")
    print(f"\n💡 Verifique:")
    print(f"   1. PINECONE_API_KEY está configurada no .env")
    print(f"   2. Index '{pinecone_client.index_name}' existe")
    print(f"   3. API Key tem permissões corretas")
    sys.exit(1)

