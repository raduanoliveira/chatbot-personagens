"""refactor characters with phrases

Revision ID: 001_refactor_characters
Revises: 
Create Date: 2025-12-15 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '001_refactor_characters'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Finalidades disponíveis
PURPOSES = [
    "para se apresentar",
    "para surpresa",
    "para animar",
    "para comemorações",
    "para começar algo"
]


def upgrade() -> None:
    """Upgrade schema - refatora estrutura de characters e adiciona phrases."""
    
    # Remove tabelas antigas se existirem
    # Verifica se as tabelas existem antes de dropar
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    existing_tables = inspector.get_table_names()
    
    # Desabilita foreign key checks para MySQL
    try:
        op.execute("SET FOREIGN_KEY_CHECKS = 0")
    except Exception:
        pass  # Não é MySQL ou já está desabilitado
    
    if "phrases" in existing_tables:
        op.drop_table("phrases")
    
    if "characters" in existing_tables:
        op.drop_table("characters")
    
    # Reabilita foreign key checks
    try:
        op.execute("SET FOREIGN_KEY_CHECKS = 1")
    except Exception:
        pass  # Não é MySQL
    
    # Cria tabela characters com nova estrutura
    op.create_table(
        "characters",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("catchphrase", sa.String(length=255), nullable=True),
        sa.Column("personality_traits", sa.JSON(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("who_is_character", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    
    # Cria tabela phrases
    op.create_table(
        "phrases",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("character_id", sa.Integer(), nullable=False),
        sa.Column("phrase", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("character_id", "purpose", name="uq_character_purpose"),
    )
    
    # Cria índices para performance
    op.create_index("ix_phrases_character_id", "phrases", ["character_id"])
    op.create_index("ix_phrases_purpose", "phrases", ["purpose"])
    
    # Seed: Insere Mario com suas falas
    conn = op.get_bind()
    
    # Insere o personagem Mario
    conn.execute(
        sa.text(
            """
            INSERT INTO characters (name, description, catchphrase, personality_traits, image_url, who_is_character)
            VALUES (:name, :description, :catchphrase, :traits, :image_url, :who_is)
            """
        ),
        {
            "name": "Mario Bros",
            "description": "Herói do Reino dos Cogumelos, encanador carismático e corajoso.",
            "catchphrase": "It's-a me, Mario!",
            "traits": '["corajoso", "otimista", "engraçado"]',
            "image_url": "https://www.nintendo.com/eu/media/images/08_content_images/others_2/characterhubs/supermariohub/MarioHub_Overview_Mario_sideimg_mario.png",
            "who_is": "o famoso encanador italiano do Reino dos Cogumelos",
        },
    )
    
    # Pega o ID do Mario inserido
    result = conn.execute(
        sa.text("SELECT id FROM characters WHERE name = :name"),
        {"name": "Mario Bros"}
    )
    mario_id = result.scalar()
    
    # Insere as falas do Mario
    mario_phrases = [
        ("Mamma mia!", "para surpresa"),
        ("It's-a me, Mario!", "para se apresentar"),
        ("Let's-a go!", "para animar"),
        ("Wahoo!", "para comemorações"),
        ("Here we go!", "para começar algo"),
    ]
    
    for phrase, purpose in mario_phrases:
        conn.execute(
            sa.text(
                """
                INSERT INTO phrases (character_id, phrase, purpose)
                VALUES (:character_id, :phrase, :purpose)
                """
            ),
            {
                "character_id": mario_id,
                "phrase": phrase,
                "purpose": purpose,
            },
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("phrases")
    op.drop_table("characters")

