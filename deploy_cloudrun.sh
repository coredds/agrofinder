#!/bin/bash
# Script para deploy do AgroFinder no Google Cloud Run

set -e

echo ""
echo "🚀 AgroFinder - Deploy para Google Cloud Run"
echo "══════════════════════════════════════════════════════════════"
echo ""

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI não encontrado!"
    echo "   Instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticação
echo "🔐 Verificando autenticação..."
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)

if [ -z "$ACCOUNT" ]; then
    echo "❌ Não autenticado no gcloud!"
    echo "   Execute: gcloud auth login"
    exit 1
fi

echo "✅ Autenticado como: $ACCOUNT"

# Obter PROJECT_ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo ""
    echo "📋 Projetos disponíveis:"
    gcloud projects list
    
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo ""
echo "📦 Projeto: $PROJECT_ID"

# Verificar se a API está habilitada
echo ""
echo "🔧 Habilitando APIs necessárias..."

APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "containerregistry.googleapis.com"
    "storage-api.googleapis.com"
    "secretmanager.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "   Habilitando $api..."
    gcloud services enable $api --project=$PROJECT_ID 2>/dev/null || true
done

echo "✅ APIs habilitadas"

# Criar secret para OpenAI API Key
echo ""
echo "🔑 Configurando secrets..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY não encontrada no ambiente"
    read -sp "Digite sua OpenAI API Key: " OPENAI_API_KEY
    echo ""
fi

# Verificar se secret já existe
if gcloud secrets describe agrofinder-openai-key --project=$PROJECT_ID &>/dev/null; then
    echo "   Secret 'agrofinder-openai-key' já existe, atualizando..."
    echo -n "$OPENAI_API_KEY" | gcloud secrets versions add agrofinder-openai-key --data-file=- --project=$PROJECT_ID
else
    echo "   Criando secret 'agrofinder-openai-key'..."
    echo -n "$OPENAI_API_KEY" | gcloud secrets create agrofinder-openai-key --data-file=- --project=$PROJECT_ID
fi

echo "✅ Secret configurado"

# Confirmar deploy
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "📋 Resumo do Deploy:"
echo "   Projeto: $PROJECT_ID"
echo "   Região: us-central1"
echo "   Service: agrofinder"
echo "   Memória: 2Gi"
echo "   CPU: 2"
echo "   Timeout: 300s"
echo "══════════════════════════════════════════════════════════════"
echo ""

read -p "Deseja continuar com o deploy? (s/n): " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo ""
    echo "❌ Deploy cancelado"
    exit 0
fi

# Build e Deploy usando Cloud Build
echo ""
echo "🏗️  Iniciando build e deploy..."
echo "   Isso pode levar 5-10 minutos..."
echo ""

gcloud builds submit --config cloudbuild.yaml --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "══════════════════════════════════════════════════════════════"
    echo ""
    
    # Obter URL do serviço
    SERVICE_URL=$(gcloud run services describe agrofinder --region=us-central1 --format="value(status.url)" --project=$PROJECT_ID)
    
    echo "🌍 URL da Aplicação:"
    echo "   $SERVICE_URL"
    echo ""
    
    echo "📊 Monitoramento:"
    echo "   Logs: gcloud run logs tail agrofinder --region=us-central1"
    echo "   Métricas: https://console.cloud.google.com/run/detail/us-central1/agrofinder"
    echo ""
    
    echo "⚠️  IMPORTANTE: ChromaDB em Cloud Run"
    echo "   Cloud Run é stateless - o banco ChromaDB será recriado a cada deploy"
    echo "   Para produção, considere:"
    echo "   1. Cloud SQL + pgvector"
    echo "   2. Pinecone (managed vector DB)"
    echo "   3. Cloud Storage para persistência do ChromaDB"
    echo ""
    
else
    echo ""
    echo "❌ Erro no deploy!"
    echo "   Verifique os logs acima para mais detalhes"
    exit 1
fi

