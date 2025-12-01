# 🌾 AgroFinder

Sistema de busca semântica inteligente para documentos agro usando OpenAI e Pinecone.

## 📋 Visão Geral

O AgroFinder é um protótipo para catalogar e buscar automaticamente PDFs de anúncios do agro e conteúdo orgânico de análises de redes sociais. Utiliza busca semântica avançada via prompts naturais, com frontend React e backend FastAPI integrados em um único container, deployado no Google Cloud Run.

### Características Principais

- 🔍 **Busca Semântica**: Encontre documentos usando linguagem natural
- 🤖 **Powered by OpenAI**: Embeddings de alta qualidade com text-embedding-3-small (1536 dimensões)
- 🚀 **Pinecone Vector DB**: Database vetorial gerenciado para produção
- ☁️ **Cloud Native**: Deploy no Google Cloud Run (serverless, auto-scaling)
- 💾 **Cloud Storage**: PDFs armazenados no Google Cloud Storage
- ⚡ **Performance**: Respostas em menos de 2 segundos
- 📦 **Container Único**: Deploy simplificado com Docker
- 🎨 **UI Moderna**: Interface React responsiva com Tailwind CSS (mobile-ready)
- 🔐 **Login Simples**: Autenticação básica para demo

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│         Container (Cloud Run)                   │
│         [Serverless - Auto Scaling]             │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Frontend (React + Vite + Tailwind)      │  │
│  │  - Login Screen                          │  │
│  │  - Search Interface                      │  │
│  │  - Upload Section                        │  │
│  │  Servido por FastAPI StaticFiles         │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Backend FastAPI                         │  │
│  │  - API Endpoints                         │  │
│  │  - Busca Semântica                       │  │
│  │  - Ingestão de PDFs                      │  │
│  │  - PDF Processing (pdfplumber)           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
            ↓                    ↓
   ┌────────────────┐   ┌────────────────────┐
   │   Pinecone     │   │ Google Cloud       │
   │   Vector DB    │   │ Storage (GCS)      │
   │                │   │                    │
   │ • 3.5k vectors │   │ • anuncios/        │
   │ • 1536-dim     │   │ • organico/        │
   │ • Cosine       │   │ • 125 PDFs         │
   │ • us-east-1    │   └────────────────────┘
   └────────────────┘            ↓
            ↓                    ↓
   ┌──────────────────────────────────────┐
   │     OpenAI Embeddings API            │
   │  text-embedding-3-small (1536-dim)   │
   └──────────────────────────────────────┘
```

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Conta OpenAI com API key
- Google Cloud Platform account (para GCS)

### Instalação Local

1. **Clone o repositório**

```bash
git clone <repo-url>
cd agrofinder
```

2. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o

# Google Cloud Storage
GCS_BUCKET_NAME=agrofinder
GCS_PROJECT_ID=your-project-id  # Opcional com ADC

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=agrofinder
PINECONE_ENVIRONMENT=us-east-1

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# Search Configuration
TOP_K_RESULTS=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

3. **Opção A: Usar Docker Compose (Recomendado)**

```bash
docker-compose up --build
```

4. **Opção B: Desenvolvimento Local**

**Backend:**
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

5. **Acesse a aplicação**

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## 📡 API Endpoints

### POST /api/search
Busca semântica de documentos

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tendências etanol agro 2025",
    "category": "anuncio",
    "top_k": 10
  }'
```

**Response:**
```json
{
  "query": "tendências etanol agro 2025",
  "results": [
    {
      "document_id": "abc123...",
      "filename": "relatorio_etanol.pdf",
      "category": "anuncio",
      "similarity_score": 0.89,
      "page_number": 5,
      "chunk_text": "O mercado de etanol...",
      "url": "/api/document/pdfs/anuncio/relatorio_etanol.pdf",
      "metadata": {...}
    }
  ],
  "total_results": 10,
  "processing_time_ms": 847
}
```

### POST /api/upload
Upload de novo PDF (indexa automaticamente no Pinecone)

```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "category=anuncio" \
  http://localhost:8000/api/upload
```

### POST /api/ingest
Ingestão manual de PDF do GCS

```json
{
  "gcs_path": "anuncios/documento.pdf",
  "category": "anuncio"
}
```

### GET /api/document/{path:path}
Serve PDF do GCS (com autenticação)

```bash
curl http://localhost:8000/api/document/pdfs/anuncio/file.pdf
```

### GET /api/health
Health check do sistema

**Response:**
```json
{
  "status": "healthy",
  "vector_db": "pinecone",
  "total_vectors": 3448,
  "environment": "production"
}
```

### GET /api/stats
Estatísticas do sistema

```json
{
  "total_vectors": 3448,
  "vector_db": "pinecone",
  "index_name": "agrofinder"
}
```

## 🏗️ Estrutura do Projeto

```
agrofinder/
├── backend/
│   ├── main.py                       # FastAPI app
│   ├── config.py                     # Configurações (Pydantic Settings)
│   ├── services/
│   │   ├── search_pinecone.py        # Busca semântica (Pinecone)
│   │   ├── ingestion_pinecone.py     # Ingestão de PDFs (Pinecone)
│   │   ├── pinecone_client.py        # Cliente Pinecone
│   │   ├── openai_client.py          # Cliente OpenAI
│   │   └── gcs_client.py             # Cliente GCS
│   └── models/
│       └── schemas.py                # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── App.tsx                   # Main app component
│   │   ├── components/
│   │   │   ├── Login.tsx             # Login screen
│   │   │   ├── SearchBar.tsx         # Search interface
│   │   │   ├── ResultCard.tsx        # Result display
│   │   │   └── UploadSection.tsx     # Upload UI
│   │   ├── services/
│   │   │   └── api.ts                # API client (axios)
│   │   └── types.ts                  # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   ├── index_all_pdfs_pinecone.py    # Bulk indexing script
│   ├── test_pinecone.py              # Test Pinecone connection
│   └── setup_gcp.ps1                 # GCP setup script
├── Dockerfile                         # Multi-stage build
├── cloudbuild.yaml                    # Cloud Build config
├── deploy_cloudrun.ps1                # Deploy script (Windows)
├── deploy_cloudrun.sh                 # Deploy script (Linux/Mac)
├── requirements.txt                   # Python dependencies
├── ARCHITECTURE.md                    # Technical documentation
├── DEPLOY_CLOUDRUN_PINECONE.md       # Deployment guide
└── README.md                          # This file
```

## 🐳 Deploy

### Google Cloud Run (Recomendado)

**Pré-requisitos:**
- Conta Pinecone (free tier suporta 100k vetores)
- Google Cloud Project configurado
- Secrets criados no Secret Manager:
  - `agrofinder-openai-key`
  - `agrofinder-pinecone-key`

**Opção 1: Script PowerShell (Windows)**

```powershell
.\deploy_cloudrun.ps1
```

**Opção 2: Script Bash (Linux/Mac)**

```bash
chmod +x deploy_cloudrun.sh
./deploy_cloudrun.sh
```

**Opção 3: Cloud Build (CI/CD)**

```bash
# Commit e push para GitHub
git push origin main

# Trigger manual do Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

**O que é deployado:**
- ✅ Container com Frontend + Backend
- ✅ Conectado ao Pinecone (stateless, sem perda de dados)
- ✅ Integrado com Google Cloud Storage
- ✅ Auto-scaling (0 a 10 instâncias)
- ✅ Secrets gerenciados pelo Secret Manager
- ✅ HTTPS automático

**Custos estimados (Google Cloud):**
- Cloud Run: ~$5-20/mês (pay-per-use)
- Cloud Storage: ~$0.02/GB/mês
- Pinecone: Grátis (free tier: 1 índice, 100k vetores)

📖 **Documentação completa:** Veja `DEPLOY_CLOUDRUN_PINECONE.md`

## 🧪 Testing

### Testar conexão Pinecone

```bash
python scripts/test_pinecone.py
```

### Testar ingestão de PDF

```python
# test_ingest.py
import asyncio
from backend.services.ingestion_pinecone import ingestion_service_pinecone
from backend.models.schemas import DocumentCategory

async def test():
    doc_id, chunks = await ingestion_service_pinecone.ingest_pdf(
        gcs_path="anuncios/test.pdf",
        category=DocumentCategory.ANUNCIO
    )
    print(f"✅ Document {doc_id} indexed with {chunks} chunks")

asyncio.run(test())
```

### Testar busca

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "tendências etanol", "top_k": 5}'
```

### Indexação em massa

```bash
# Indexar todos os PDFs do GCS para Pinecone
python scripts/index_all_pdfs_pinecone.py
```

### Testar via interface web

```bash
# 1. Iniciar backend
python -m uvicorn backend.main:app --reload --port 8000

# 2. Iniciar frontend (outro terminal)
cd frontend
npm run dev

# 3. Acessar http://localhost:3000
# Login com credenciais configuradas em frontend/src/components/Login.tsx
```

## 📊 Stack Tecnológica

- **Backend**: FastAPI 0.115+, Python 3.12
- **Frontend**: React 19, Vite 5, TailwindCSS 3
- **Vector DB**: Pinecone 3.0+ (managed, serverless)
- **LLM**: OpenAI (text-embedding-3-small, GPT-4o)
- **Storage**: Google Cloud Storage
- **PDF Processing**: pdfplumber
- **Deploy**: Google Cloud Run, Docker
- **CI/CD**: Google Cloud Build

## 🔧 Desenvolvimento

### Adicionar novos endpoints

1. Adicione schema em `backend/models/schemas.py`
2. Implemente lógica em `backend/services/`
3. Adicione endpoint em `backend/main.py`

### Adicionar novos componentes

1. Crie componente em `frontend/src/components/`
2. Adicione tipos em `frontend/src/types.ts`
3. Use no `App.tsx`

## 📝 Próximos Passos

- [x] ~~Implementar Pinecone para vector storage~~
- [x] ~~Deploy no Google Cloud Run~~
- [x] ~~Upload de PDFs pela interface~~
- [x] ~~Login básico para demo~~
- [x] ~~UI responsiva (mobile-ready)~~
- [ ] Implementar cache de embeddings
- [ ] Adicionar autenticação OAuth (Google, GitHub)
- [ ] Melhorar reranking com GPT-4o
- [ ] Dashboard de analytics (estatísticas de uso)
- [ ] Suporte para mais formatos (DOCX, TXT, PPTX)
- [ ] Histórico de buscas por usuário
- [ ] Export de resultados (CSV, PDF)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🙋 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub ou entre em contato.

---

**AgroFinder v1.0** - Powered by OpenAI & Pinecone 🚀

