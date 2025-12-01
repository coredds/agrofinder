"""
Script de teste para busca semântica
"""
import asyncio
import sys
import os

# Adicionar parent directory ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.search import search_service
from backend.models.schemas import DocumentCategory


async def test_search():
    """Testa busca semântica"""
    
    # Exemplo de queries
    queries = [
        "tendências de mercado para etanol em 2025",
        "análise de preços agrícolas",
        "relatórios de redes sociais do agronegócio"
    ]
    
    print("=" * 60)
    print("🔍 Testando Busca Semântica")
    print("=" * 60)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 60)
        
        try:
            results = await search_service.search(
                query=query,
                top_k=3
            )
            
            if results:
                print(f"✅ Encontrados {len(results)} resultados:")
                for i, result in enumerate(results, 1):
                    print(f"\n   {i}. {result.filename}")
                    print(f"      Relevância: {result.similarity_score * 100:.1f}%")
                    print(f"      Categoria: {result.category.value}")
                    print(f"      Preview: {result.chunk_text[:100]}...")
            else:
                print("❌ Nenhum resultado encontrado")
                
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            import traceback
            traceback.print_exc()


async def check_collection():
    """Verifica estado da collection"""
    print("\n" + "=" * 60)
    print("📊 Estado da Collection")
    print("=" * 60)
    
    try:
        count = search_service.get_document_count()
        print(f"Total de chunks indexados: {count}")
        
        if count == 0:
            print("\n⚠️  ATENÇÃO: Nenhum documento indexado!")
            print("   Execute 'python scripts/test_ingest.py' primeiro.")
    except Exception as e:
        print(f"❌ Erro ao verificar collection: {e}")


if __name__ == "__main__":
    asyncio.run(check_collection())
    asyncio.run(test_search())

