# 🚀 AgroFinder - Guia de Início Rápido

## Configuração Inicial (5 minutos)

### 1. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com suas credenciais:

```bash
# OpenAI Configuration (OBRIGATÓRIO)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Google Cloud Storage Configuration (OBRIGATÓRIO)
GCS_BUCKET_NAME=agrofinder-pdfs
GCS_PROJECT_ID=your-gcp-project-id

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
```

⚠️ **IMPORTANTE**: Você precisa de uma conta OpenAI com créditos disponíveis.

### 2. Instale as Dependências

**Windows PowerShell:**
```powershell
.\scripts\init_env.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/init_env.sh
./scripts/init_env.sh
```

**Ou manualmente:**
```bash
# Backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

## Opções de Execução

### Opção 1: Docker Compose (Recomendado para Produção)

```bash
docker-compose up --build
```

Acesse: http://localhost:8000

### Opção 2: Desenvolvimento Local (Recomendado para Desenvolvimento)

**Terminal 1 - Backend:**
```bash
# Ativar ambiente virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Executar FastAPI
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Acesse:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Primeiros Passos

### 1. Verificar se está funcionando

Acesse http://localhost:8000/api/health

Você deve ver:
```json
{
  "status": "healthy",
  "environment": "development",
  "chromadb_status": "healthy",
  "total_documents": 0,
  "timestamp": "2025-12-01T..."
}
```

### 2. Ingerir seu primeiro PDF

**Opção A: Via Upload (interface)**
1. Acesse http://localhost:3000
2. (Funcionalidade de upload via UI - a implementar)

**Opção B: Via API**
```bash
# Upload de arquivo local
curl -X POST http://localhost:8000/api/upload \
  -F "file=@seu_documento.pdf" \
  -F "category=anuncio"
```

**Opção C: Ingerir PDF já no GCS**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "gcs_path": "pdfs/documento.pdf",
    "category": "anuncio"
  }'
```

**Opção D: Script de teste**
```python
# Edite scripts/test_ingest.py com seu PDF
python scripts/test_ingest.py
```

### 3. Fazer sua primeira busca

**Via Interface:**
1. Acesse http://localhost:3000
2. Digite uma busca: "tendências etanol agro 2025"
3. Clique em "Buscar"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tendências de mercado para etanol",
    "top_k": 5
  }'
```

**Via Script:**
```bash
python scripts/test_search.py
```

## Estrutura do Projeto

```
agrofinder/
├── backend/               # Backend FastAPI
│   ├── main.py           # Aplicação principal
│   ├── config.py         # Configurações
│   ├── services/         # Lógica de negócio
│   │   ├── search.py     # Busca semântica
│   │   ├── ingestion.py  # Ingestão de PDFs
│   │   ├── openai_client.py
│   │   └── gcs_client.py
│   └── models/
│       └── schemas.py    # Modelos Pydantic
├── frontend/             # Frontend React
│   ├── src/
│   │   ├── App.tsx       # Componente principal
│   │   ├── components/   # Componentes React
│   │   └── services/     # Cliente API
│   └── package.json
├── scripts/              # Scripts úteis
│   ├── test_ingest.py    # Testar ingestão
│   ├── test_search.py    # Testar busca
│   └── init_env.*        # Inicializar ambiente
├── Dockerfile            # Build multi-stage
├── docker-compose.yml    # Orquestração local
└── requirements.txt      # Dependências Python
```

## Troubleshooting

### Erro: "OpenAI API key not found"
- Verifique se você criou o arquivo `.env`
- Certifique-se de que OPENAI_API_KEY está configurado corretamente

### Erro: "GCS authentication failed"
- Verifique suas credenciais GCP
- Configure `GOOGLE_APPLICATION_CREDENTIALS` se necessário

### Erro: "ChromaDB not found"
- Execute: `mkdir chroma_db`
- Verifique se CHROMA_DB_PATH está correto

### Erro: "Module not found"
- Reinstale as dependências: `pip install -r requirements.txt`
- Verifique se o ambiente virtual está ativado

### Frontend não carrega
- Verifique se as dependências foram instaladas: `cd frontend && npm install`
- Certifique-se de que o backend está rodando na porta 8000

## Comandos Úteis

```bash
# Verificar health
curl http://localhost:8000/api/health

# Verificar estatísticas
curl http://localhost:8000/api/stats

# Ver documentação interativa
# Acesse: http://localhost:8000/docs

# Build para produção
docker build -t agrofinder .

# Executar container
docker run -p 8000:8000 --env-file .env agrofinder
```

## Deploy para Produção

Ver arquivo `README.md` para instruções completas de deploy no Google Cloud Run.

## Próximos Passos

1. ✅ Ingerir alguns PDFs de teste
2. ✅ Testar diferentes tipos de busca
3. ✅ Explorar a API em `/docs`
4. 📖 Ler a documentação completa em `README.md`
5. 🚀 Fazer deploy no Cloud Run

## Suporte

- 📖 Documentação: `README.md`
- 🐛 Issues: GitHub Issues
- 💬 Dúvidas: Abra uma discussão

---

Feito com ❤️ para o agronegócio brasileiro 🇧🇷

