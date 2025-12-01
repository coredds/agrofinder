# Script para configurar e testar integração com GCP
# Este script usa as credenciais do gcloud CLI já configuradas

Write-Host "🌾 AgroFinder - Setup Google Cloud Platform" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Verificar se gcloud está instalado
Write-Host "🔍 Verificando gcloud CLI..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud version 2>&1 | Select-String "Google Cloud SDK"
    Write-Host "✅ gcloud CLI encontrado: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud CLI não encontrado!" -ForegroundColor Red
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Host ""
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1

if ($LASTEXITCODE -eq 0 -and $currentAccount) {
    Write-Host "✅ Autenticado como: $currentAccount" -ForegroundColor Green
} else {
    Write-Host "❌ Não autenticado!" -ForegroundColor Red
    Write-Host "   Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

# Configurar Application Default Credentials
Write-Host ""
Write-Host "🔑 Configurando Application Default Credentials..." -ForegroundColor Yellow
Write-Host "   Isso permite que a aplicação use suas credenciais do gcloud" -ForegroundColor Cyan

try {
    gcloud auth application-default login --no-launch-browser
    Write-Host "✅ ADC configurado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erro ao configurar ADC. Tentando continuar..." -ForegroundColor Yellow
}

# Listar arquivos no bucket agrofinder
Write-Host ""
Write-Host "📦 Verificando bucket gs://agrofinder..." -ForegroundColor Yellow

# Listar pastas
Write-Host ""
Write-Host "📁 Pasta: anuncios/" -ForegroundColor Cyan
$anuncios = gsutil ls gs://agrofinder/anuncios/ 2>&1
if ($LASTEXITCODE -eq 0) {
    $anuncios | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor White
    }
    $totalAnuncios = ($anuncios | Measure-Object).Count
    Write-Host "   Total: $totalAnuncios arquivo(s)" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Erro ao acessar pasta anuncios/" -ForegroundColor Red
}

Write-Host ""
Write-Host "📁 Pasta: organico/" -ForegroundColor Cyan
$organico = gsutil ls gs://agrofinder/organico/ 2>&1
if ($LASTEXITCODE -eq 0) {
    $organico | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor White
    }
    $totalOrganico = ($organico | Measure-Object).Count
    Write-Host "   Total: $totalOrganico arquivo(s)" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Erro ao acessar pasta organico/" -ForegroundColor Red
}

# Verificar/Criar arquivo .env
Write-Host ""
Write-Host "📝 Configurando arquivo .env..." -ForegroundColor Yellow

$envContent = @"
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Google Cloud Storage Configuration
# Usando Application Default Credentials (ADC) do gcloud CLI
GCS_BUCKET_NAME=agrofinder

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
"@

if (-Not (Test-Path .env)) {
    $envContent | Out-File -FilePath .env -Encoding UTF8
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANTE: Configure sua OPENAI_API_KEY no arquivo .env" -ForegroundColor Yellow
} else {
    Write-Host "✅ Arquivo .env já existe" -ForegroundColor Green
}

# Resumo
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "✅ Setup GCP concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure sua OPENAI_API_KEY no arquivo .env" -ForegroundColor White
Write-Host "2. Execute: .\scripts\init_env.ps1 (se ainda não executou)" -ForegroundColor White
Write-Host "3. Inicie o backend: uvicorn backend.main:app --reload" -ForegroundColor White
Write-Host "4. Teste a ingestão: python scripts\test_ingest_gcs.py" -ForegroundColor White
Write-Host ""
Write-Host "🔒 Segurança:" -ForegroundColor Cyan
Write-Host "   - Suas credenciais GCP não são salvas no repositório" -ForegroundColor Gray
Write-Host "   - O sistema usa Application Default Credentials (ADC)" -ForegroundColor Gray
Write-Host "   - O arquivo .env está no .gitignore" -ForegroundColor Gray
Write-Host ""

