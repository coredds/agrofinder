# Script para verificar se suas credenciais estão seguras

Write-Host ""
Write-Host "🔒 Verificação de Segurança - AgroFinder" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

$issues = 0

# 1. Verificar se .env existe e tem credenciais
Write-Host "1. Verificando arquivo .env..." -ForegroundColor Cyan

if (Test-Path .env) {
    Write-Host "   ✅ .env encontrado" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    
    if ($envContent -match "sk-proj-your-openai-api-key-here") {
        Write-Host "   ⚠️  API Key ainda é o placeholder!" -ForegroundColor Yellow
        Write-Host "      Configure sua chave real da OpenAI" -ForegroundColor Gray
        $issues++
    } elseif ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "   ✅ API Key configurada" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  API Key não encontrada ou inválida" -ForegroundColor Yellow
        $issues++
    }
} else {
    Write-Host "   ❌ .env não encontrado!" -ForegroundColor Red
    Write-Host "      Execute: .\scripts\create_env.ps1" -ForegroundColor Yellow
    $issues++
}

# 2. Verificar .gitignore
Write-Host ""
Write-Host "2. Verificando .gitignore..." -ForegroundColor Cyan

if (Test-Path .gitignore) {
    $gitignoreContent = Get-Content .gitignore -Raw
    
    if ($gitignoreContent -match "\.env") {
        Write-Host "   ✅ .env está protegido no .gitignore" -ForegroundColor Green
    } else {
        Write-Host "   ❌ .env NÃO está no .gitignore!" -ForegroundColor Red
        Write-Host "      PERIGO: Suas credenciais podem ser commitadas!" -ForegroundColor Red
        $issues++
    }
    
    if ($gitignoreContent -match "\*\.json") {
        Write-Host "   ✅ Arquivos .json estão protegidos" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Arquivos .json não estão protegidos" -ForegroundColor Yellow
    }
    
    if ($gitignoreContent -match "chroma_db") {
        Write-Host "   ✅ chroma_db/ está protegido" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  .gitignore não encontrado!" -ForegroundColor Yellow
    $issues++
}

# 3. Verificar se é repositório git
Write-Host ""
Write-Host "3. Verificando repositório Git..." -ForegroundColor Cyan

try {
    git status 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Repositório Git inicializado" -ForegroundColor Green
        
        # Verificar se .env está sendo rastreado
        $trackedFiles = git ls-files 2>&1
        
        if ($trackedFiles -match "\.env$") {
            Write-Host "   ❌ PERIGO: .env está sendo rastreado pelo Git!" -ForegroundColor Red
            Write-Host "      Execute: git rm --cached .env" -ForegroundColor Yellow
            $issues++
        } else {
            Write-Host "   ✅ .env não está sendo rastreado" -ForegroundColor Green
        }
    } else {
        Write-Host "   ⚠️  Não é um repositório Git" -ForegroundColor Yellow
        Write-Host "      Execute 'git init' se quiser usar Git" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Git não encontrado ou não é um repositório" -ForegroundColor Yellow
}

# 4. Verificar arquivos sensíveis no diretório
Write-Host ""
Write-Host "4. Procurando arquivos sensíveis..." -ForegroundColor Cyan

$sensitiveFiles = @(
    "*.json",
    "credentials.json",
    "service-account.json",
    "*.pem",
    "*.key"
)

$found = @()
foreach ($pattern in $sensitiveFiles) {
    $files = Get-ChildItem -Filter $pattern -Recurse -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -notmatch "node_modules|package" }
    
    if ($files) {
        $found += $files
    }
}

if ($found.Count -gt 0) {
    Write-Host "   ⚠️  Arquivos sensíveis encontrados:" -ForegroundColor Yellow
    foreach ($file in $found) {
        Write-Host "      - $($file.Name)" -ForegroundColor Gray
    }
    Write-Host "      Certifique-se de que estão no .gitignore!" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Nenhum arquivo sensível encontrado" -ForegroundColor Green
}

# 5. Verificar ADC do Google Cloud
Write-Host ""
Write-Host "5. Verificando autenticação GCP..." -ForegroundColor Cyan

try {
    $gcloudAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $gcloudAccount) {
        Write-Host "   ✅ Autenticado como: $gcloudAccount" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Não autenticado no GCP" -ForegroundColor Yellow
        Write-Host "      Execute: gcloud auth application-default login" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  gcloud CLI não encontrado" -ForegroundColor Yellow
}

# Resumo
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "📊 RESUMO DA VERIFICAÇÃO" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

if ($issues -eq 0) {
    Write-Host "🎉 TUDO OK! Suas credenciais estão seguras!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Você pode commitar com segurança:" -ForegroundColor White
    Write-Host "   git add ." -ForegroundColor Cyan
    Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  $issues problema(s) encontrado(s)!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Corrija os problemas acima antes de commitar!" -ForegroundColor Red
}

Write-Host ""
Write-Host "📚 Documentação de Segurança: SECURITY.md" -ForegroundColor Cyan
Write-Host ""

