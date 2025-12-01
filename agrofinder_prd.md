# AgroFinder Product Requirements Document (PRD)

## 1. Visão do Produto

O **AgroFinder** é um protótipo para catalogar automaticamente PDFs de anúncios do agro e relatórios de análises de redes sociais armazenados no Google Cloud Storage (GCS). Realiza buscas semânticas inteligentes via prompts naturais usando modelos OpenAI, com frontend React e backend FastAPI integrados em um único container. ChromaDB roda embutido para indexação vetorial local.

**Escopo**: Até 520 documentos (2 categorias × 26 quinzenais/ano × 5 anos). Deploy em Cloud Run como container único. Foco em implementação rápida para validação.

## 2. Público-Alvo e User Stories

### Usuários
- Analistas agro
- Pesquisadores de mercado agrícola

### User Stories
- Como analista, quero buscar "tendências etanol agro 2025" e receber PDFs relevantes rankeados
- Como usuário, quero filtrar por categoria (anúncios/relatórios) e data
- Como administrador, quero fazer upload de novos PDFs e vê-los indexados automaticamente

## 3. Funcionalidades Principais

### 3.1 Ingestão de Documentos
- Monitoramento de GCS para novos PDFs
- Extração de texto com pdfplumber
- Chunking inteligente (500 tokens)
- Geração de embeddings com OpenAI
- Armazenamento no ChromaDB

### 3.2 Busca Semântica
- Input via prompt natural
- Embedding da query com OpenAI
- Busca por similaridade no ChromaDB (top-K=10)
- Reranking dos resultados
- Preview e download de PDFs

### 3.3 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/search` | POST | Busca semântica por prompt + filtros |
| `/api/ingest` | POST | Indexação manual de PDF |
| `/api/upload` | POST | Upload de novo PDF para GCS |
| `/api/health` | GET | Status do sistema |
| `/` | GET | Serve frontend React |

### 3.4 Frontend
- Interface React moderna e responsiva
- Busca em tempo real
- Tabela de resultados com preview
- Download direto de PDFs
- Filtros por categoria e data

## 4. Requisitos Não-Funcionais

### 4.1 Performance
- Resposta de busca: < 2 segundos
- ChromaDB local para acesso rápido
- Caching de embeddings recorrentes

### 4.2 Escalabilidade
- Cloud Run auto-scale: 1-10 instâncias
- Suporte para até 520 documentos
- Preparado para crescimento futuro

### 4.3 Persistência
- ChromaDB em volume persistente (`./chroma_db/`)
- PDFs armazenados no GCS
- Metadados em ChromaDB SQLite backend

### 4.4 Segurança
- Autenticação IAM para GCS
- API keys OpenAI via variáveis de ambiente
- CORS configurado para domínio específico

### 4.5 Custo
- Orçamento alvo: < $10/mês para protótipo
- Cloud Run pay-per-use
- OpenAI API otimizada (embeddings text-embedding-3-small)

## 5. Arquitetura Técnica

### 5.1 Visão Geral - Container Único

```
┌─────────────────────────────────────────────────┐
│         Container (Cloud Run)                   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Frontend (React - Build Estático)       │  │
│  │  Servido por FastAPI StaticFiles         │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  Backend FastAPI                         │  │
│  │  - Endpoints API (/api/*)                │  │
│  │  - Serviço de Busca                      │  │
│  │  - Serviço de Ingestão                   │  │
│  │  - Cliente GCS                           │  │
│  │  - Cliente OpenAI                        │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  ChromaDB (Embedded)                     │  │
│  │  - PersistentClient                      │  │
│  │  - Volume: ./chroma_db/                  │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────┐
        │  Google Cloud Storage   │
        │  (Bucket com PDFs)      │
        └─────────────────────────┘
```

### 5.2 Fluxo de Ingestão

```
1. Upload PDF → GCS Bucket
2. Webhook/Polling → FastAPI /api/ingest
3. Download PDF do GCS
4. Extração texto (pdfplumber)
5. Chunking (500 tokens)
6. Embeddings OpenAI (text-embedding-3-small)
7. Upsert ChromaDB com metadados
```

### 5.3 Fluxo de Busca

```
1. User Query (Frontend)
2. POST /api/search
3. Embedding query OpenAI
4. Busca similaridade ChromaDB (top-K=10)
5. Retorna resultados com metadados
6. Exibição no Frontend
```

### 5.4 ChromaDB Configuração

```python
import chromadb
from chromadb.config import Settings

# Client persistente embutido
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Collection para documentos agro
collection = client.get_or_create_collection(
    name="agro_docs",
    metadata={"hnsw:space": "cosine"}
)
```

## 6. Plano de Implementação (2 Semanas)

| Sprint | Atividades | Entregável | Tempo |
|--------|------------|------------|-------|
| **Dia 1-3** | Setup FastAPI + ChromaDB + OpenAI, ingestão manual de PDFs | Backend local funcionando com `/api/search` e `/api/ingest` | 3 dias |
| **Dia 4-6** | Pipeline automático GCS, cliente OpenAI, testes de ingestão | Ingestão automática funcionando com webhooks | 3 dias |
| **Dia 7-9** | Frontend React (Vite + Tailwind), integração com API | Interface completa de busca e resultados | 3 dias |
| **Dia 10-12** | Build container único, deploy Cloud Run, testes end-to-end | Protótipo online e funcional | 3 dias |

## 7. Stack Tecnológica

### Backend
- **Framework**: FastAPI 0.115+
- **Vector DB**: ChromaDB 0.5+
- **PDF Processing**: pdfplumber
- **HTTP Client**: httpx (async)
- **GCS Client**: google-cloud-storage

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **UI Components**: shadcn/ui (opcional)

### LLM & Embeddings
- **Provider**: OpenAI exclusivamente
- **Embeddings**: text-embedding-3-small
- **Models**: GPT-4o (para reranking/summarização se necessário)

### Infraestrutura
- **Container**: Docker multi-stage build
- **Deploy**: Google Cloud Run
- **Storage**: Google Cloud Storage
- **Persistência**: ChromaDB local (SQLite backend)

### DevOps
- **CI/CD**: Cloud Build
- **Secrets**: Google Secret Manager
- **Monitoring**: Cloud Logging

## 8. Estrutura do Projeto

```
agrofinder/
├── backend/
│   ├── main.py                 # FastAPI app principal
│   ├── services/
│   │   ├── ingestion.py        # Serviço de ingestão
│   │   ├── search.py           # Serviço de busca
│   │   ├── openai_client.py    # Cliente OpenAI
│   │   └── gcs_client.py       # Cliente GCS
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── config.py               # Configurações
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── services/
│   ├── package.json
│   └── vite.config.ts
├── chroma_db/                  # Volume ChromaDB (gitignore)
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Desenvolvimento local
├── requirements.txt
├── .env.example
└── README.md
```

## 9. Dockerfile - Container Único

```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend + Frontend Servido
FROM python:3.12-slim
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código backend
COPY backend/ ./backend/

# Copiar frontend build do stage anterior
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Criar diretório para ChromaDB
RUN mkdir -p /app/chroma_db

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV CHROMA_DB_PATH=/app/chroma_db

# Comando de inicialização
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 10. Configuração e Deploy

### 10.1 Variáveis de Ambiente

```bash
# .env
OPENAI_API_KEY=sk-...
GCS_BUCKET_NAME=agrofinder-pdfs
GCS_PROJECT_ID=your-project-id
CHROMA_DB_PATH=./chroma_db
ENVIRONMENT=production
```

### 10.2 requirements.txt

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
chromadb==0.5.0
pydantic==2.8.0
pydantic-settings==2.4.0
openai==1.40.0
google-cloud-storage==2.18.0
pdfplumber==0.11.0
python-multipart==0.0.9
httpx==0.27.0
```

### 10.3 Deploy Commands

```bash
# Build e Push da Imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/agrofinder

# Deploy no Cloud Run
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

### 10.4 Desenvolvimento Local

```bash
# Com Docker Compose
docker-compose up --build

# Ou direto
cd backend && uvicorn main:app --reload --port 8000
cd frontend && npm run dev
```

## 11. Próximos Passos Imediatos

### Fase 1: Setup Inicial (Dia 1)
1. Criar estrutura de pastas do projeto
2. Configurar ambiente virtual Python
3. Instalar dependências: `pip install -r requirements.txt`
4. Configurar variáveis de ambiente (.env)
5. Inicializar ChromaDB local

### Fase 2: Backend Core (Dias 2-3)
1. Implementar FastAPI main.py com endpoints base
2. Criar serviço de ingestão com pdfplumber
3. Integrar OpenAI client para embeddings
4. Testar ingestão manual: `python -m backend.test_ingest`
5. Implementar endpoint de busca semântica

### Fase 3: Frontend (Dias 4-6)
1. Setup Vite + React + Tailwind
2. Criar componente de busca
3. Criar tabela de resultados
4. Integrar com API backend
5. Build de produção

### Fase 4: Deploy (Dias 7-8)
1. Criar Dockerfile multi-stage
2. Testar build local do container
3. Deploy Cloud Run
4. Configurar secrets e env vars
5. Testes end-to-end

## 12. Métricas de Sucesso

- ✅ Ingestão de 520 documentos em < 1 hora
- ✅ Resposta de busca em < 2 segundos
- ✅ Precisão de busca > 80% (avaliação manual)
- ✅ Uptime > 99%
- ✅ Custo mensal < $10

## 13. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Custo OpenAI excede orçamento | Média | Alto | Cache de embeddings, usar text-embedding-3-small |
| ChromaDB não persiste entre restarts | Baixa | Alto | Volume persistente Cloud Run |
| Performance degrada com 520 docs | Baixa | Médio | Otimização chunking, índices ChromaDB |
| Timeout em PDFs grandes | Média | Médio | Processamento assíncrono, timeout 60s |

---

**Documento preparado para**: Protótipo AgroFinder v1.0  
**Última atualização**: Dezembro 2025  
**Status**: Pronto para implementação