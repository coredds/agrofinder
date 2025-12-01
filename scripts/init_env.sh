#!/bin/bash

# Script para inicializar ambiente de desenvolvimento

echo "🌾 AgroFinder - Inicialização do Ambiente"
echo "=========================================="

# Criar ambiente virtual Python
echo "📦 Criando ambiente virtual Python..."
python -m venv venv

# Ativar ambiente virtual
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependências Python
echo "📥 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório ChromaDB
echo "📁 Criando diretório ChromaDB..."
mkdir -p chroma_db

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Crie um arquivo .env baseado em .env.example"
    echo ""
    echo "Conteúdo mínimo necessário:"
    echo "OPENAI_API_KEY=sk-your-key-here"
    echo "GCS_BUCKET_NAME=agrofinder-pdfs"
    echo "GCS_PROJECT_ID=your-project-id"
    echo "CHROMA_DB_PATH=./chroma_db"
    echo "ENVIRONMENT=development"
else
    echo "✅ Arquivo .env encontrado"
fi

# Instalar dependências do frontend
echo "📥 Instalando dependências do Frontend..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Ambiente inicializado com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Execute 'uvicorn backend.main:app --reload' para iniciar o backend"
echo "3. Execute 'cd frontend && npm run dev' para iniciar o frontend"
echo ""

