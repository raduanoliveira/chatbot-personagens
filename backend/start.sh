#!/bin/sh

# Script de inicialização com retry para conexão MySQL
# Não usa set -e para permitir tratamento de erros

echo "🚀 Iniciando aplicação..."

# Função para limpar revisões antigas do Alembic
clean_alembic_version() {
    echo "🧹 Verificando tabela alembic_version..."
    
    # Tenta limpar usando Python, mas não falha se der erro
    python3 << 'EOF' || echo "⚠️  Não foi possível verificar alembic_version (banco pode não estar pronto)"
import os
import sys
sys.path.insert(0, '/app')

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🔍 Conectando ao banco...")
    with engine.connect() as conn:
        # Verifica se a tabela existe
        result = conn.execute(text("SHOW TABLES LIKE 'alembic_version'"))
        if result.fetchone():
            # Verifica a revisão atual
            result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            row = result.fetchone()
            if row:
                version = row[0]
                print(f"📌 Revisão atual: {version}")
                # Se for uma revisão antiga que não existe mais, limpa
                old_revisions = ['fa3c80dae25c', '88ab14753bca']
                if version in old_revisions:
                    print(f"⚠️  Revisão antiga encontrada: {version}. Limpando...")
                    conn.execute(text("DELETE FROM alembic_version"))
                    conn.commit()
                    print("✅ Tabela alembic_version limpa!")
                else:
                    print(f"✅ Revisão válida: {version}")
            else:
                print("ℹ️  Tabela alembic_version está vazia")
        else:
            print("ℹ️  Tabela alembic_version não existe ainda")
except Exception as e:
    import traceback
    print(f"⚠️  Erro ao verificar alembic_version: {e}")
    traceback.print_exc()
    # Não falha se houver erro, apenas continua
    sys.exit(0)
EOF
}

# Função para tentar executar migrations com retry
run_migrations_with_retry() {
    local max_attempts=10
    local attempt=1
    local delay=5
    
    # Limpa revisões antigas antes de tentar migrations (pode falhar se banco não estiver pronto)
    echo "🔧 Tentando limpar revisões antigas do Alembic..."
    clean_alembic_version || echo "⚠️  Limpeza falhou, mas continuando..."
    
    while [ $attempt -le $max_attempts ]; do
        echo "📊 Tentativa $attempt/$max_attempts: Executando migrations..."
        echo "📂 Diretório atual: $(pwd)"
        echo "📁 Conteúdo de alembic/versions:"
        ls -la alembic/versions/ || echo "Erro ao listar versions"
        
        if alembic upgrade head 2>&1; then
            echo "✅ Migrations executadas com sucesso!"
            return 0
        else
            exit_code=$?
            echo "❌ Falha na tentativa $attempt (exit code: $exit_code)"
            
            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Aguardando ${delay}s antes de tentar novamente..."
                sleep $delay
                attempt=$((attempt + 1))
            else
                echo "❌ ERRO CRÍTICO: Migrations falharam após $max_attempts tentativas!"
                return 1
            fi
        fi
    done
}

# Tenta executar migrations com retry
echo "🚦 Iniciando processo de migrations..."
if ! run_migrations_with_retry; then
    echo "❌ ERRO CRÍTICO: Migrations falharam após múltiplas tentativas!"
    echo "📋 Verifique os logs acima para mais detalhes."
    echo "💡 Dica: Verifique se o MySQL está acessível e se as variáveis de ambiente estão corretas."
    echo "🔍 Variáveis de ambiente (mascarado):"
    echo "   DB_HOST=${DB_HOST}"
    echo "   DB_PORT=${DB_PORT}"
    echo "   DB_NAME=${DB_NAME}"
    echo "   DB_USER=${DB_USER}"
    echo "   DB_PASSWORD=***"
    exit 1
fi

# Inicia o servidor
echo "✅ Migrations concluídas! Iniciando servidor..."
echo "🌐 Iniciando servidor uvicorn na porta 7000..."
echo "🔗 Servidor estará disponível em: http://0.0.0.0:7000"
exec uvicorn app.main:app --host 0.0.0.0 --port 7000

