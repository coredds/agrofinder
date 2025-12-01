# Script para criar arquivo .env de forma segura
# Este script copia o template e verifica a segurança

Write-Host ""
Write-Host "🔒 AgroFinder - Configuração Segura de Credenciais" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Verificar se .env já existe
if (Test-Path .env) {
    Write-Host "⚠️  Arquivo .env já existe!" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Deseja sobrescrever? (s/N)"
    
    if ($response -ne "s") {
        Write-Host ""
        Write-Host "✅ Mantendo arquivo .env existente." -ForegroundColor Green
        Write-Host ""
        exit 0
    }
}

# Copiar template
Write-Host "📄 Criando arquivo .env a partir do template..." -ForegroundColor Cyan

if (Test-Path .env.template) {
    Copy-Item .env.template .env
    Write-Host "✅ Arquivo .env criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo .env.template não encontrado!" -ForegroundColor Red
    Write-Host "   Criando .env com configuração padrão..." -ForegroundColor Yellow
    
    $defaultEnv = @"
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Google Cloud Storage Configuration
GCS_BUCKET_NAME=agrofinder
GCS_PROJECT_ID=

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
"@
    
    $defaultEnv | Out-File -FilePath .env -Encoding UTF8
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
}

# Verificar .gitignore
Write-Host ""
Write-Host "🔍 Verificando proteção do .gitignore..." -ForegroundColor Cyan

if (Test-Path .gitignore) {
    $gitignoreContent = Get-Content .gitignore
    
    if ($gitignoreContent -match "\.env") {
        Write-Host "✅ .env está protegido no .gitignore" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env NÃO está no .gitignore!" -ForegroundColor Red
        Write-Host "   Adicionando agora..." -ForegroundColor Yellow
        Add-Content .gitignore "`n# Environment variables`n.env`n.env.local"
        Write-Host "✅ Adicionado ao .gitignore" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Arquivo .gitignore não encontrado!" -ForegroundColor Yellow
    Write-Host "   Criando .gitignore..." -ForegroundColor Cyan
    
    @"
# Environment variables
.env
.env.local

# Python
__pycache__/
*.pyc

# ChromaDB
chroma_db/

# Node
node_modules/
"@ | Out-File -FilePath .gitignore -Encoding UTF8
    
    Write-Host "✅ .gitignore criado!" -ForegroundColor Green
}

# Instruções
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "📋 PRÓXIMOS PASSOS" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Abra o arquivo .env em um editor:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Substitua 'sk-proj-your-openai-api-key-here' pela sua chave real" -ForegroundColor White
Write-Host "   Obtenha em: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host ""
Write-Host "3. ⚠️  IMPORTANTE - Segurança:" -ForegroundColor Red
Write-Host "   - O arquivo .env contém CREDENCIAIS SENSÍVEIS" -ForegroundColor Yellow
Write-Host "   - NUNCA compartilhe este arquivo" -ForegroundColor Yellow
Write-Host "   - NUNCA faça commit dele no Git" -ForegroundColor Yellow
Write-Host "   - Já está protegido no .gitignore ✅" -ForegroundColor Green
Write-Host ""
Write-Host "4. Verifique se está protegido:" -ForegroundColor White
Write-Host "   git status | Select-String .env" -ForegroundColor Cyan
Write-Host "   (não deve retornar nada)" -ForegroundColor Gray
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Abrir arquivo para edição
$openFile = Read-Host "Deseja abrir o arquivo .env para edição agora? (s/N)"
if ($openFile -eq "s") {
    notepad .env
}

Write-Host ""
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host ""

