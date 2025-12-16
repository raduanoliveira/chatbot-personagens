import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base  # noqa: F401  (ensures metadata import)


def ensure_database_exists():
    """
    Verifica se o banco de dados existe e cria se não existir.
    Deve ser chamado antes de criar o engine com o database_url.
    """
    try:
        # Conecta ao MySQL sem especificar o banco de dados
        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            charset='utf8mb4'
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
        print(f"⚠️  Erro ao verificar/criar banco de dados: {e}")
        raise


# Garante que o banco existe antes de criar o engine
# Não falha se o MySQL não estiver disponível - apenas loga o erro
try:
    ensure_database_exists()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  Não foi possível verificar/criar banco de dados: {e}")
    logger.warning("   Isso é normal se o MySQL ainda não estiver disponível.")
    logger.warning("   O Alembic tentará criar o banco durante as migrations.")

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

