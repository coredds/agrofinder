"""
Script de teste para ingestão de PDF
"""
import asyncio
import sys
import os

# Adicionar parent directory ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.ingestion import ingestion_service
from backend.models.schemas import DocumentCategory


async def test_ingest():
    """Testa ingestão de um PDF de exemplo"""
    
    # Exemplo de uso
    gcs_path = "pdfs/test_documento.pdf"  # Altere para seu PDF
    category = DocumentCategory.ANUNCIO
    
    print(f"🚀 Iniciando ingestão de: {gcs_path}")
    print(f"📁 Categoria: {category.value}")
    
    try:
        document_id, num_chunks = await ingestion_service.ingest_pdf(
            gcs_path=gcs_path,
            category=category,
            metadata={
                "source": "test_script",
                "test": True
            }
        )
        
        print(f"\n✅ Ingestão concluída com sucesso!")
        print(f"📄 Document ID: {document_id}")
        print(f"📊 Chunks criados: {num_chunks}")
        
        # Verificar stats
        stats = ingestion_service.get_collection_stats()
        print(f"\n📈 Estatísticas da collection:")
        print(f"   Total de chunks: {stats['total_chunks']}")
        print(f"   Collection: {stats['collection_name']}")
        
    except Exception as e:
        print(f"\n❌ Erro durante ingestão: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🌾 AgroFinder - Teste de Ingestão")
    print("=" * 60)
    
    asyncio.run(test_ingest())

