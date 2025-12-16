from logging.config import fileConfig
from pathlib import Path
import sys

import pymysql
from sqlalchemy import engine_from_config, pool, text

from alembic import context

BASE_DIR = Path(__file__).resolve().parents[1]
# Garante que o diretório de trabalho está no PYTHONPATH (prioridade máxima)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Verifica se o módulo app existe antes de importar
import os
# Debug: lista o que existe no BASE_DIR
if not os.path.exists(os.path.join(BASE_DIR, "app")):
    print(f"❌ ERRO: Diretório 'app' não encontrado em {BASE_DIR}")
    print(f"📁 Conteúdo de {BASE_DIR}:")
    try:
        for item in os.listdir(BASE_DIR):
            print(f"  - {item}")
    except Exception as e:
        print(f"  Erro ao listar: {e}")
    raise RuntimeError(f"Diretório 'app' não encontrado em {BASE_DIR}")

if not os.path.exists(os.path.join(BASE_DIR, "app", "core")):
    print(f"❌ ERRO: Diretório 'app/core' não encontrado em {BASE_DIR}")
    print(f"📁 Conteúdo de {os.path.join(BASE_DIR, 'app')}:")
    try:
        for item in os.listdir(os.path.join(BASE_DIR, "app")):
            print(f"  - {item}")
    except Exception as e:
        print(f"  Erro ao listar: {e}")
    raise RuntimeError(f"Diretório 'app/core' não encontrado em {BASE_DIR}")

if not os.path.exists(os.path.join(BASE_DIR, "app", "core", "__init__.py")):
    print(f"❌ ERRO: Arquivo 'app/core/__init__.py' não encontrado em {BASE_DIR}")
    print(f"📁 Conteúdo de {os.path.join(BASE_DIR, 'app', 'core')}:")
    try:
        for item in os.listdir(os.path.join(BASE_DIR, "app", "core")):
            print(f"  - {item}")
    except Exception as e:
        print(f"  Erro ao listar: {e}")
    raise RuntimeError(f"Arquivo 'app/core/__init__.py' não encontrado em {BASE_DIR}")

if not os.path.exists(os.path.join(BASE_DIR, "app", "core", "config.py")):
    print(f"❌ ERRO: Arquivo 'app/core/config.py' não encontrado em {BASE_DIR}")
    print(f"📁 Conteúdo de {os.path.join(BASE_DIR, 'app', 'core')}:")
    try:
        for item in os.listdir(os.path.join(BASE_DIR, "app", "core")):
            print(f"  - {item}")
    except Exception as e:
        print(f"  Erro ao listar: {e}")
    raise RuntimeError(f"Arquivo 'app/core/config.py' não encontrado em {BASE_DIR}")

from app.core.config import settings  # noqa: E402
from app.models.base import Base  # noqa: E402
from app import models  # noqa: F401, E402


def ensure_database_exists():
    """
    Verifica se o banco de dados existe e cria se não existir.
    Não falha se o MySQL não estiver disponível - apenas loga o erro.
    """
    try:
        # Conecta ao MySQL sem especificar o banco de dados
        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            charset='utf8mb4',
            connect_timeout=5  # Timeout de 5 segundos
        )
        
        with connection.cursor() as cursor:
            # Verifica se o banco existe
            cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
                (settings.db_name,)
            )
            result = cursor.fetchone()
            
            if not result:
                # Cria o banco de dados se não existir
                cursor.execute(f"CREATE DATABASE `{settings.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                connection.commit()
                print(f"✅ Banco de dados '{settings.db_name}' criado com sucesso!")
            else:
                print(f"✅ Banco de dados '{settings.db_name}' já existe.")
        
        connection.close()
    except Exception as e:
        # Não faz raise - apenas loga o erro
        # O Alembic tentará conectar novamente quando executar as migrations
        print(f"⚠️  Aviso: Não foi possível verificar/criar banco de dados agora: {e}")
        print(f"   Isso é normal se o MySQL ainda não estiver disponível.")
        print(f"   Tentando conectar em: {settings.db_host}:{settings.db_port}")
        print(f"   As migrations serão executadas quando o banco estiver disponível.")


# Tenta garantir que o banco existe antes de rodar migrations
# Mas não falha se não conseguir - o Alembic tentará novamente
ensure_database_exists()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Limpa revisões antigas que não existem mais
        try:
            result = connection.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            row = result.fetchone()
            if row:
                version = row[0]
                old_revisions = ['fa3c80dae25c', '88ab14753bca']
                if version in old_revisions:
                    print(f"⚠️  Revisão antiga encontrada: {version}. Limpando...")
                    connection.execute(text("DELETE FROM alembic_version"))
                    connection.commit()
                    print("✅ Tabela alembic_version limpa!")
        except Exception as e:
            # Se a tabela não existir ou houver erro, continua normalmente
            print(f"ℹ️  Não foi possível verificar alembic_version: {e}")
        
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
