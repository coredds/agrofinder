"""
Script para testar ingestão de PDFs do bucket gs://agrofinder
"""
import asyncio
import sys
import os

# Adicionar parent directory ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.ingestion import ingestion_service
from backend.models.schemas import DocumentCategory


async def list_and_ingest():
    """Lista e ingere PDFs das pastas anuncios e organico"""
    
    print("=" * 70)
    print("🌾 AgroFinder - Ingestão de PDFs do GCS")
    print("=" * 70)
    print()
    
    # Exemplos de arquivos para ingerir
    # Você pode listar com: gsutil ls gs://agrofinder/anuncios/
    # Você pode listar com: gsutil ls gs://agrofinder/organico/
    
    test_files = [
        # Exemplos - ajuste conforme seus arquivos reais
        {
            "gcs_path": "anuncios/exemplo1.pdf",  # Ajuste para seu arquivo real
            "category": DocumentCategory.ANUNCIO
        },
        {
            "gcs_path": "organico/exemplo1.pdf",  # Ajuste para seu arquivo real
            "category": DocumentCategory.ORGANICO
        },
    ]
    
    print("📋 INSTRUÇÕES:")
    print("1. Liste os arquivos no seu bucket:")
    print("   gsutil ls gs://agrofinder/anuncios/")
    print("   gsutil ls gs://agrofinder/organico/")
    print()
    print("2. Edite este arquivo e atualize test_files com os caminhos reais")
    print()
    print("3. Execute novamente: python scripts/test_ingest_gcs.py")
    print()
    print("-" * 70)
    print()
    
    # Perguntar ao usuário se deseja continuar
    response = input("Você já configurou os arquivos corretos? (s/N): ")
    if response.lower() != 's':
        print()
        print("⚠️  Configure os arquivos primeiro!")
        print()
        print("Exemplo de como editar test_files:")
        print('test_files = [')
        print('    {')
        print('        "gcs_path": "anuncios/seu_arquivo.pdf",')
        print('        "category": DocumentCategory.ANUNCIO')
        print('    },')
        print(']')
        return
    
    print()
    print("🚀 Iniciando ingestão...")
    print()
    
    successful = 0
    failed = 0
    
    for i, file_info in enumerate(test_files, 1):
        gcs_path = file_info["gcs_path"]
        category = file_info["category"]
        
        print(f"\n[{i}/{len(test_files)}] Processando: {gcs_path}")
        print(f"    Categoria: {category.value}")
        
        try:
            document_id, num_chunks = await ingestion_service.ingest_pdf(
                gcs_path=gcs_path,
                category=category,
                metadata={
                    "source": "test_ingest_gcs",
                    "original_path": gcs_path
                }
            )
            
            print(f"    ✅ Sucesso!")
            print(f"    📄 Document ID: {document_id}")
            print(f"    📊 Chunks: {num_chunks}")
            successful += 1
            
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            failed += 1
    
    # Resumo
    print()
    print("=" * 70)
    print("📈 RESUMO DA INGESTÃO")
    print("=" * 70)
    print(f"✅ Sucesso: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📊 Total: {len(test_files)}")
    
    # Estatísticas da collection
    stats = ingestion_service.get_collection_stats()
    print()
    print("📚 Estatísticas da Collection ChromaDB:")
    print(f"   Total de chunks indexados: {stats['total_chunks']}")
    print(f"   Collection: {stats['collection_name']}")
    print()
    print("=" * 70)
    print()
    print("🎉 Pronto! Agora você pode testar a busca:")
    print("   python scripts/test_search.py")
    print("   Ou acesse: http://localhost:3000")
    print()


async def ingest_specific_file(gcs_path: str, category_str: str):
    """Ingere um arquivo específico"""
    category = DocumentCategory(category_str)
    
    print(f"\n🚀 Ingerindo arquivo: {gcs_path}")
    print(f"📁 Categoria: {category.value}")
    print()
    
    try:
        document_id, num_chunks = await ingestion_service.ingest_pdf(
            gcs_path=gcs_path,
            category=category,
            metadata={"source": "cli"}
        )
        
        print(f"✅ Ingestão concluída!")
        print(f"📄 Document ID: {document_id}")
        print(f"📊 Chunks: {num_chunks}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    
    # Modo interativo
    if len(sys.argv) > 1:
        # Uso: python test_ingest_gcs.py anuncios/arquivo.pdf anuncio
        if len(sys.argv) != 3:
            print("Uso: python test_ingest_gcs.py <gcs_path> <category>")
            print("Exemplo: python test_ingest_gcs.py anuncios/doc.pdf anuncio")
            print("Categorias: anuncio, organico, relatorio")
            sys.exit(1)
        
        gcs_path = sys.argv[1]
        category_str = sys.argv[2]
        asyncio.run(ingest_specific_file(gcs_path, category_str))
    else:
        # Modo batch
        asyncio.run(list_and_ingest())

