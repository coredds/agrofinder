# Script PowerShell para inicializar ambiente de desenvolvimento no Windows

Write-Host "🌾 AgroFinder - Inicialização do Ambiente" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Criar ambiente virtual Python
Write-Host "📦 Criando ambiente virtual Python..." -ForegroundColor Yellow
python -m venv venv

# Ativar ambiente virtual
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Instalar dependências Python
Write-Host "📥 Instalando dependências Python..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório ChromaDB
Write-Host "📁 Criando diretório ChromaDB..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path chroma_db | Out-Null

# Verificar se .env existe
if (-Not (Test-Path .env)) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "📝 Crie um arquivo .env com o seguinte conteúdo:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPENAI_API_KEY=sk-your-key-here" -ForegroundColor Cyan
    Write-Host "GCS_BUCKET_NAME=agrofinder-pdfs" -ForegroundColor Cyan
    Write-Host "GCS_PROJECT_ID=your-project-id" -ForegroundColor Cyan
    Write-Host "CHROMA_DB_PATH=./chroma_db" -ForegroundColor Cyan
    Write-Host "ENVIRONMENT=development" -ForegroundColor Cyan
} else {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
}

# Instalar dependências do frontend
Write-Host "📥 Instalando dependências do Frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host ""
Write-Host "✅ Ambiente inicializado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure o arquivo .env com suas credenciais"
Write-Host "2. Execute 'uvicorn backend.main:app --reload' para iniciar o backend"
Write-Host "3. Execute 'cd frontend; npm run dev' para iniciar o frontend"
Write-Host ""

