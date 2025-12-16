#!/usr/bin/env python3
"""
Script para limpar revisões antigas do Alembic.
Executa antes das migrations para evitar erros de revisões não encontradas.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    from app.database import engine
    from sqlalchemy import text
    
    print("🧹 Verificando tabela alembic_version...")
    
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
                    sys.exit(0)
                else:
                    print(f"ℹ️  Revisão atual: {version} (não precisa limpar)")
            else:
                print("ℹ️  Tabela alembic_version está vazia")
        else:
            print("ℹ️  Tabela alembic_version não existe ainda")
except Exception as e:
    print(f"⚠️  Erro ao verificar alembic_version: {e}")
    # Não falha se houver erro, apenas continua
    sys.exit(0)

