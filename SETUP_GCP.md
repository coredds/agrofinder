# 🔐 Setup Google Cloud Platform - AgroFinder

Este guia explica como configurar o AgroFinder para usar seu bucket GCS existente de forma segura.

## ✅ Segurança Garantida

- ✅ **Nenhuma credencial** é salva no repositório
- ✅ Usa **Application Default Credentials (ADC)** do gcloud CLI
- ✅ Arquivo `.env` está no `.gitignore`
- ✅ Arquivos `.json` de credenciais bloqueados no `.gitignore`

## 📋 Pré-requisitos

1. **gcloud CLI instalado e configurado**
   ```bash
   gcloud --version
   ```

2. **Autenticado no GCP**
   ```bash
   gcloud auth list
   ```

3. **Bucket gs://agrofinder acessível** com as pastas:
   - `anuncios/`
   - `organico/`

## 🚀 Setup Rápido (Windows)

### Passo 1: Execute o script de setup

```powershell
.\scripts\setup_gcp.ps1
```

Este script irá:
- ✅ Verificar se gcloud CLI está instalado
- ✅ Verificar autenticação
- ✅ Configurar Application Default Credentials (ADC)
- ✅ Listar arquivos no bucket gs://agrofinder
- ✅ Criar arquivo .env (se não existir)

### Passo 2: Configure sua OpenAI API Key

Edite o arquivo `.env` que foi criado:

```bash
# Abra o arquivo .env e adicione sua chave
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

### Passo 3: Verifique os arquivos no bucket

```powershell
# Listar com Python
python scripts/list_gcs_files.py

# Ou diretamente com gsutil
gsutil ls gs://agrofinder/anuncios/
gsutil ls gs://agrofinder/organico/
```

## 🔧 Como Funciona

### Application Default Credentials (ADC)

O sistema usa ADC do gcloud CLI automaticamente:

1. Você faz login uma vez:
   ```bash
   gcloud auth application-default login
   ```

2. O Python usa essas credenciais automaticamente via `google-cloud-storage`

3. **Nenhuma credencial é salva no código** ✅

### Estrutura de Configuração

```python
# backend/services/gcs_client.py
class GCSClient:
    def __init__(self):
        # Usa ADC automaticamente - sem credenciais explícitas!
        self.client = storage.Client()
        self.bucket = self.client.bucket("agrofinder")
```

## 📁 Estrutura do Bucket

```
gs://agrofinder/
├── anuncios/        # PDFs de anúncios
│   ├── anuncio1.pdf
│   ├── anuncio2.pdf
│   └── ...
└── organico/        # PDFs de conteúdo orgânico
    ├── organico1.pdf
    ├── organico2.pdf
    └── ...
```

## 🧪 Testando a Integração

### 1. Listar arquivos no bucket

```bash
python scripts/list_gcs_files.py
```

Saída esperada:
```
🌾 AgroFinder - Arquivos no GCS
==================================================
📦 Bucket: gs://agrofinder

📁 anuncios/
--------------------------------------------------
   📄 documento1.pdf
      Tamanho: 2.5 MB
      Caminho: anuncios/documento1.pdf
...
```

### 2. Ingerir um arquivo específico

```bash
# Sintaxe: python scripts/test_ingest_gcs.py <caminho> <categoria>
python scripts/test_ingest_gcs.py anuncios/documento1.pdf anuncio
python scripts/test_ingest_gcs.py organico/relatorio1.pdf organico
```

### 3. Ingerir múltiplos arquivos

Edite `scripts/test_ingest_gcs.py` e configure a lista `test_files`:

```python
test_files = [
    {
        "gcs_path": "anuncios/doc1.pdf",
        "category": DocumentCategory.ANUNCIO
    },
    {
        "gcs_path": "organico/rel1.pdf",
        "category": DocumentCategory.ORGANICO
    },
]
```

Depois execute:
```bash
python scripts/test_ingest_gcs.py
```

## 🔍 Testando Busca

Após ingerir alguns documentos:

```bash
python scripts/test_search.py
```

Ou use a interface web:
```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Acesse: http://localhost:3000
```

## 🛠️ Troubleshooting

### Erro: "Could not automatically determine credentials"

**Solução:**
```bash
gcloud auth application-default login
```

### Erro: "403 Forbidden" ao acessar bucket

**Verificar:**
1. Você tem permissão no bucket?
   ```bash
   gsutil ls gs://agrofinder/
   ```

2. Sua conta está ativa?
   ```bash
   gcloud auth list
   ```

### Erro: "Bucket does not exist"

**Verificar:**
1. Nome do bucket no `.env`:
   ```bash
   GCS_BUCKET_NAME=agrofinder
   ```

2. Bucket existe?
   ```bash
   gsutil ls gs://agrofinder/
   ```

### Erro: "Module 'google.cloud.storage' not found"

**Solução:**
```bash
pip install google-cloud-storage
# Ou
pip install -r requirements.txt
```

## 📊 Categorias Disponíveis

O sistema agora suporta 3 categorias:

- **anuncio**: PDFs de anúncios publicitários
- **organico**: PDFs de conteúdo orgânico/social
- **relatorio**: PDFs de relatórios (futuro)

## 🔒 Segurança - Checklist

- ✅ `.env` está no `.gitignore`
- ✅ `*.json` está no `.gitignore` (exceto package.json)
- ✅ Usando ADC (sem credenciais hardcoded)
- ✅ Nenhum secret commitado
- ✅ Token OpenAI em variável de ambiente

## 📝 Resumo dos Comandos

```bash
# Setup inicial
.\scripts\setup_gcp.ps1

# Listar arquivos
python scripts/list_gcs_files.py

# Ingerir arquivo específico
python scripts/test_ingest_gcs.py anuncios/doc.pdf anuncio

# Testar busca
python scripts/test_search.py

# Iniciar aplicação
uvicorn backend.main:app --reload
```

## 🎯 Próximos Passos

1. ✅ Setup GCP concluído
2. ✅ Listar arquivos no bucket
3. ✅ Ingerir alguns PDFs de teste
4. ✅ Testar busca semântica
5. 🚀 Usar a aplicação!

---

**Nota de Segurança**: Suas credenciais GCP permanecem apenas no seu sistema local e não são compartilhadas ou commitadas no Git. O sistema usa Application Default Credentials (ADC) que é a prática recomendada pelo Google Cloud.

