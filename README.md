# 🌾 AgroFinder

Sistema de busca semântica inteligente para documentos agro usando OpenAI e ChromaDB.

## 📋 Visão Geral

O AgroFinder é um protótipo para catalogar e buscar automaticamente PDFs de anúncios do agro e relatórios de análises de redes sociais. Utiliza busca semântica avançada via prompts naturais, com frontend React e backend FastAPI integrados em um único container.

### Características Principais

- 🔍 **Busca Semântica**: Encontre documentos usando linguagem natural
- 🤖 **Powered by OpenAI**: Embeddings de alta qualidade com text-embedding-3-small
- ⚡ **Performance**: Respostas em menos de 2 segundos
- 📦 **Container Único**: Deploy simplificado com Docker
- 🎨 **UI Moderna**: Interface React responsiva com Tailwind CSS

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│         Container (Cloud Run)                   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Frontend (React + Vite + Tailwind)      │  │
│  │  Servido por FastAPI StaticFiles         │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Backend FastAPI                         │  │
│  │  - API Endpoints                         │  │
│  │  - Busca Semântica                       │  │
│  │  - Ingestão de PDFs                      │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  ChromaDB (Embedded)                     │  │
│  │  - Indexação Vetorial                    │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────┐
        │  Google Cloud Storage   │
        └─────────────────────────┘
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

# Google Cloud Storage
GCS_BUCKET_NAME=agrofinder-pdfs
GCS_PROJECT_ID=your-project-id

# ChromaDB
CHROMA_DB_PATH=./chroma_db

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
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

```json
{
  "query": "tendências etanol agro 2025",
  "category": "anuncio",
  "top_k": 10
}
```

### POST /api/ingest
Ingestão manual de PDF do GCS

```json
{
  "gcs_path": "pdfs/documento.pdf",
  "category": "relatorio"
}
```

### POST /api/upload
Upload de novo PDF

```bash
curl -X POST -F "file=@document.pdf" -F "category=anuncio" \
  http://localhost:8000/api/upload
```

### GET /api/health
Health check do sistema

## 🏗️ Estrutura do Projeto

```
agrofinder/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── config.py              # Configurações
│   ├── services/
│   │   ├── search.py          # Busca semântica
│   │   ├── ingestion.py       # Ingestão de PDFs
│   │   ├── openai_client.py   # Cliente OpenAI
│   │   └── gcs_client.py      # Cliente GCS
│   └── models/
│       └── schemas.py         # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── services/
│   │   └── types.ts
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🐳 Deploy

### Google Cloud Run

1. **Build e Push da imagem**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/agrofinder
```

2. **Deploy**

```bash
gcloud run deploy agrofinder \
  --image gcr.io/PROJECT_ID/agrofinder \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars OPENAI_API_KEY=${OPENAI_API_KEY} \
  --set-env-vars GCS_BUCKET_NAME=agrofinder-pdfs \
  --set-env-vars GCS_PROJECT_ID=PROJECT_ID \
  --max-instances 10 \
  --min-instances 1
```

## 🧪 Testing

### Testar ingestão de PDF

```python
# test_ingest.py
import asyncio
from backend.services.ingestion import ingestion_service
from backend.models.schemas import DocumentCategory

async def test():
    doc_id, chunks = await ingestion_service.ingest_pdf(
        gcs_path="pdfs/test.pdf",
        category=DocumentCategory.ANUNCIO
    )
    print(f"Document {doc_id} indexed with {chunks} chunks")

asyncio.run(test())
```

### Testar busca

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "tendências etanol", "top_k": 5}'
```

## 📊 Stack Tecnológica

- **Backend**: FastAPI 0.115+, Python 3.12
- **Frontend**: React 19, Vite, TailwindCSS
- **Vector DB**: ChromaDB 0.5+
- **LLM**: OpenAI (text-embedding-3-small, GPT-4o)
- **Storage**: Google Cloud Storage
- **Deploy**: Google Cloud Run, Docker

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

- [ ] Implementar cache de embeddings
- [ ] Adicionar autenticação de usuários
- [ ] Melhorar reranking com GPT-4o
- [ ] Dashboard de analytics
- [ ] Suporte para mais formatos (DOCX, TXT)

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

**AgroFinder v1.0** - Powered by OpenAI & ChromaDB 🚀

