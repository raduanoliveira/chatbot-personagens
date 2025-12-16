#!/bin/sh

# Script de inicialização com retry para conexão MySQL
set -e

echo "🚀 Iniciando aplicação..."

# Função para limpar revisões antigas do Alembic
clean_alembic_version() {
    echo "🧹 Verificando tabela alembic_version..."
    python3 << 'EOF'
import os
import sys
sys.path.insert(0, '/app')

try:
    from app.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Verifica se a tabela existe
        result = conn.execute(text("SHOW TABLES LIKE 'alembic_version'"))
        if result.fetchone():
            # Verifica a revisão atual
            result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            row = result.fetchone()
            if row:
                version = row[0]
                # Se for uma revisão antiga que não existe mais, limpa
                old_revisions = ['fa3c80dae25c', '88ab14753bca']
                if version in old_revisions:
                    print(f"⚠️  Revisão antiga encontrada: {version}. Limpando...")
                    conn.execute(text("DELETE FROM alembic_version"))
                    conn.commit()
                    print("✅ Tabela alembic_version limpa!")
                else:
                    print(f"ℹ️  Revisão atual: {version}")
        else:
            print("ℹ️  Tabela alembic_version não existe ainda")
except Exception as e:
    print(f"⚠️  Erro ao verificar alembic_version: {e}")
    # Não falha se houver erro, apenas continua
EOF
}

# Função para tentar executar migrations com retry
run_migrations_with_retry() {
    local max_attempts=10
    local attempt=1
    local delay=5
    
    # Limpa revisões antigas antes de tentar migrations
    clean_alembic_version
    
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

