#!/usr/bin/env pwsh
# Script para deploy do AgroFinder no Google Cloud Run

Write-Host "`n🚀 AgroFinder - Deploy para Google Cloud Run`n" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Verificar se gcloud está instalado
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ gcloud CLI não encontrado!" -ForegroundColor Red
    Write-Host "   Instale: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null

if (-not $account) {
    Write-Host "❌ Não autenticado no gcloud!" -ForegroundColor Red
    Write-Host "   Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Autenticado como: $account" -ForegroundColor Green

# Obter PROJECT_ID
$PROJECT_ID = gcloud config get-value project 2>$null

if (-not $PROJECT_ID) {
    Write-Host "`n📋 Projetos disponíveis:" -ForegroundColor Yellow
    gcloud projects list
    
    $PROJECT_ID = Read-Host "`nDigite o PROJECT_ID"
    gcloud config set project $PROJECT_ID
}

Write-Host "`n📦 Projeto: $PROJECT_ID" -ForegroundColor Green

# Verificar se a API está habilitada
Write-Host "`n🔧 Habilitando APIs necessárias..." -ForegroundColor Yellow

$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "storage-api.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Habilitando $api..." -ForegroundColor Gray
    gcloud services enable $api --project=$PROJECT_ID 2>$null
}

Write-Host "✅ APIs habilitadas" -ForegroundColor Green

# Criar secrets
Write-Host "`n🔑 Configurando secrets..." -ForegroundColor Yellow

# OpenAI API Key
$OPENAI_KEY = $env:OPENAI_API_KEY
if (-not $OPENAI_KEY) {
    Write-Host "⚠️  OPENAI_API_KEY não encontrada no ambiente" -ForegroundColor Yellow
    $secureOpenAI = Read-Host "Digite sua OpenAI API Key" -AsSecureString
    $OPENAI_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureOpenAI)
    )
}

$secretExists = gcloud secrets describe agrofinder-openai-key --project=$PROJECT_ID 2>$null

if ($secretExists) {
    Write-Host "   Secret 'agrofinder-openai-key' já existe, atualizando..." -ForegroundColor Gray
    echo $OPENAI_KEY | gcloud secrets versions add agrofinder-openai-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   Criando secret 'agrofinder-openai-key'..." -ForegroundColor Gray
    echo $OPENAI_KEY | gcloud secrets create agrofinder-openai-key --data-file=- --project=$PROJECT_ID
}

# Pinecone API Key
$PINECONE_KEY = $env:PINECONE_API_KEY
if (-not $PINECONE_KEY) {
    Write-Host "⚠️  PINECONE_API_KEY não encontrada no ambiente" -ForegroundColor Yellow
    Write-Host "   Crie uma conta gratuita em: https://www.pinecone.io/" -ForegroundColor Cyan
    $securePinecone = Read-Host "Digite sua Pinecone API Key" -AsSecureString
    $PINECONE_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePinecone)
    )
}

$pineconeSecretExists = gcloud secrets describe agrofinder-pinecone-key --project=$PROJECT_ID 2>$null

if ($pineconeSecretExists) {
    Write-Host "   Secret 'agrofinder-pinecone-key' já existe, atualizando..." -ForegroundColor Gray
    echo $PINECONE_KEY | gcloud secrets versions add agrofinder-pinecone-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   Criando secret 'agrofinder-pinecone-key'..." -ForegroundColor Gray
    echo $PINECONE_KEY | gcloud secrets create agrofinder-pinecone-key --data-file=- --project=$PROJECT_ID
}

Write-Host "✅ Secrets configurados" -ForegroundColor Green

# Confirmar deploy
Write-Host "`n══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 Resumo do Deploy:" -ForegroundColor Yellow
Write-Host "   Projeto: $PROJECT_ID" -ForegroundColor White
Write-Host "   Região: us-central1" -ForegroundColor White
Write-Host "   Service: agrofinder" -ForegroundColor White
Write-Host "   Memória: 2Gi" -ForegroundColor White
Write-Host "   CPU: 2" -ForegroundColor White
Write-Host "   Timeout: 300s" -ForegroundColor White
Write-Host "══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$confirm = Read-Host "Deseja continuar com o deploy? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "`n❌ Deploy cancelado" -ForegroundColor Red
    exit 0
}

# Build e Deploy usando Cloud Build
Write-Host "`n🏗️  Iniciando build e deploy..." -ForegroundColor Yellow
Write-Host "   Isso pode levar 5-10 minutos...`n" -ForegroundColor Gray

gcloud builds submit --config cloudbuild.yaml --project=$PROJECT_ID

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "══════════════════════════════════════════════════════════════`n" -ForegroundColor Green
    
    # Obter URL do serviço
    $SERVICE_URL = gcloud run services describe agrofinder --region=us-central1 --format="value(status.url)" --project=$PROJECT_ID
    
    Write-Host "🌍 URL da Aplicação:" -ForegroundColor Yellow
    Write-Host "   $SERVICE_URL`n" -ForegroundColor Cyan
    
    Write-Host "📊 Monitoramento:" -ForegroundColor Yellow
    Write-Host "   Logs: gcloud run logs tail agrofinder --region=us-central1" -ForegroundColor White
    Write-Host "   Métricas: https://console.cloud.google.com/run/detail/us-central1/agrofinder`n" -ForegroundColor White
    
    Write-Host "✅ Usando Pinecone (Managed Vector DB)" -ForegroundColor Green
    Write-Host "   ✓ Dados persistentes automaticamente" -ForegroundColor White
    Write-Host "   ✓ Escala automática" -ForegroundColor White
    Write-Host "   ✓ Alta disponibilidade" -ForegroundColor White
    Write-Host "`n   Dashboard: https://app.pinecone.io/`n" -ForegroundColor Cyan
    
} else {
    Write-Host "`n❌ Erro no deploy!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para mais detalhes" -ForegroundColor Yellow
    exit 1
}

