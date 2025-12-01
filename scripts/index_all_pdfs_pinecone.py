"""
Script para indexar todos os PDFs do bucket GCS no Pinecone
"""
import asyncio
import sys
import os
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import storage
from backend.services.ingestion_pinecone import ingestion_service_pinecone
from backend.services.pinecone_client import pinecone_client
from backend.models.schemas import DocumentCategory
from backend.config import settings


def list_all_pdfs() -> Dict[str, List[str]]:
    """Lista todos os PDFs do bucket organizados por categoria"""
    print("📦 Conectando ao bucket gs://agrofinder...")
    
    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket_name)
    
    pdfs = {
        "anuncios": [],
        "organico": [],
        "outros": []
    }
    
    blobs = bucket.list_blobs()
    
    for blob in blobs:
        if blob.name.endswith('.pdf'):
            if blob.name.startswith('anuncios/'):
                pdfs["anuncios"].append(blob.name)
            elif blob.name.startswith('organico/'):
                pdfs["organico"].append(blob.name)
            elif blob.name.startswith('pdfs/anuncio/'):
                pdfs["anuncios"].append(blob.name)
            elif blob.name.startswith('pdfs/organico/'):
                pdfs["organico"].append(blob.name)
            else:
                pdfs["outros"].append(blob.name)
    
    return pdfs


async def index_all():
    """Indexa todos os PDFs do bucket no Pinecone"""
    
    print("=" * 80)
    print("🌾 AgroFinder - Indexação em Massa para Pinecone")
    print("=" * 80)
    print()
    
    # Verificar conexão Pinecone
    print("🔍 Verificando conexão com Pinecone...")
    try:
        stats = pinecone_client.get_index_stats()
        print(f"✅ Conectado ao Pinecone")
        print(f"   Index: {settings.pinecone_index_name}")
        print(f"   Vetores atuais: {stats.get('total_vectors', 0):,}")
    except Exception as e:
        print(f"❌ Erro ao conectar no Pinecone: {e}")
        print(f"   Verifique se PINECONE_API_KEY está configurada no .env")
        return
    
    # Listar PDFs
    pdfs = list_all_pdfs()
    
    total_pdfs = sum(len(files) for files in pdfs.values())
    
    print()
    print("📊 PDFs encontrados:")
    print(f"   📢 Anúncios: {len(pdfs['anuncios'])} arquivo(s)")
    print(f"   🌱 Orgânico: {len(pdfs['organico'])} arquivo(s)")
    if pdfs['outros']:
        print(f"   ❓ Outros: {len(pdfs['outros'])} arquivo(s)")
    print(f"   📦 Total: {total_pdfs} arquivo(s)")
    print()
    
    if total_pdfs == 0:
        print("⚠️  Nenhum PDF encontrado no bucket!")
        return
    
    # Confirmar
    print("🚀 Iniciando indexação no Pinecone...")
    print("   (Isso pode levar alguns minutos dependendo da quantidade de PDFs)")
    print()
    
    success_count = 0
    error_count = 0
    total_chunks = 0
    
    # Indexar anúncios
    if pdfs['anuncios']:
        print(f"\n{'='*80}")
        print(f"📢 Indexando Anúncios ({len(pdfs['anuncios'])} arquivos)")
        print(f"{'='*80}\n")
        
        for i, pdf_path in enumerate(pdfs['anuncios'], 1):
            filename = pdf_path.split('/')[-1]
            print(f"[{i}/{len(pdfs['anuncios'])}] 📄 {filename}")
            
            try:
                document_id, num_chunks = await ingestion_service_pinecone.ingest_pdf(
                    gcs_path=pdf_path,
                    category=DocumentCategory.ANUNCIO,
                    metadata={"indexed_by": "batch_script_pinecone", "source": "reindex"}
                )
                
                print(f"   ✅ Sucesso! {num_chunks} chunks criados")
                success_count += 1
                total_chunks += num_chunks
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)[:100]}")
                error_count += 1
            
            print()
    
    # Indexar orgânicos
    if pdfs['organico']:
        print(f"\n{'='*80}")
        print(f"🌱 Indexando Orgânico ({len(pdfs['organico'])} arquivos)")
        print(f"{'='*80}\n")
        
        for i, pdf_path in enumerate(pdfs['organico'], 1):
            filename = pdf_path.split('/')[-1]
            print(f"[{i}/{len(pdfs['organico'])}] 📄 {filename}")
            
            try:
                document_id, num_chunks = await ingestion_service_pinecone.ingest_pdf(
                    gcs_path=pdf_path,
                    category=DocumentCategory.ORGANICO,
                    metadata={"indexed_by": "batch_script_pinecone", "source": "reindex"}
                )
                
                print(f"   ✅ Sucesso! {num_chunks} chunks criados")
                success_count += 1
                total_chunks += num_chunks
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)[:100]}")
                error_count += 1
            
            print()
    
    # Resumo final
    print()
    print("=" * 80)
    print("📈 RESUMO DA INDEXAÇÃO")
    print("=" * 80)
    print(f"✅ Sucessos: {success_count}/{total_pdfs}")
    print(f"❌ Erros: {error_count}/{total_pdfs}")
    print(f"📊 Total de chunks criados: {total_chunks:,}")
    print()
    
    # Estatísticas finais do Pinecone
    try:
        final_stats = pinecone_client.get_index_stats()
        print("📚 Estatísticas do Pinecone:")
        print(f"   Total de vetores no index: {final_stats.get('total_vectors', 0):,}")
        print(f"   Index: {settings.pinecone_index_name}")
        print(f"   Dashboard: https://app.pinecone.io/")
    except Exception as e:
        print(f"⚠️  Não foi possível obter estatísticas finais: {e}")
    
    print()
    print("=" * 80)
    print()
    
    if success_count == total_pdfs:
        print("🎉 Todos os documentos foram indexados com sucesso no Pinecone!")
    elif success_count > 0:
        print(f"⚠️  {success_count} documentos indexados, {error_count} com erro")
    else:
        print("❌ Falha ao indexar documentos")
    
    print()
    print("🚀 Sistema pronto para uso!")
    print("   Frontend local: http://localhost:3000")
    print("   Backend local: http://localhost:8000")
    print("   Ou faça deploy: .\\deploy_cloudrun.ps1")
    print()


if __name__ == "__main__":
    asyncio.run(index_all())

