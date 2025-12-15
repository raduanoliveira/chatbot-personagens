#!/bin/sh

# Script de inicialização com retry para conexão MySQL
set -e

echo "🚀 Iniciando aplicação..."

# Função para tentar executar migrations com retry
run_migrations_with_retry() {
    local max_attempts=10
    local attempt=1
    local delay=5
    
    while [ $attempt -le $max_attempts ]; do
        echo "📊 Tentativa $attempt/$max_attempts: Executando migrations..."
        
        if alembic upgrade head; then
            echo "✅ Migrations executadas com sucesso!"
            return 0
        else
            echo "⚠️  Falha na tentativa $attempt. Aguardando ${delay}s antes de tentar novamente..."
            if [ $attempt -lt $max_attempts ]; then
                sleep $delay
                attempt=$((attempt + 1))
            else
                echo "❌ Falhou após $max_attempts tentativas. Continuando mesmo assim..."
                return 1
            fi
        fi
    done
}

# Tenta executar migrations com retry
run_migrations_with_retry || echo "⚠️  Migrations falharam, mas continuando..."

# Inicia o servidor
echo "🌐 Iniciando servidor uvicorn na porta 7000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 7000

