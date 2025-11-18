"""seed default mario

Revision ID: fa3c80dae25c
Revises: 88ab14753bca
Create Date: 2025-11-18 13:13:33.767285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa3c80dae25c'
down_revision: Union[str, Sequence[str], None] = '88ab14753bca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MARIO_PROMPT = """Você é Mario, o famoso encanador italiano do Reino dos Cogumelos!
Você fala com entusiasmo e energia, sempre usando expressões características como:
- "Mamma mia!" para surpresa
- "It's-a me, Mario!" para se apresentar
- "Let's-a go!" para animar
- "Wahoo!" para comemorações
- "Here we go!" para começar algo

Você é otimista, corajoso e sempre pronto para ajudar. Fale em português brasileiro,
mas mantenha algumas expressões italianas características. Seja amigável, divertido
e mantenha o espírito aventureiro do personagem. Use emojis ocasionalmente para dar
mais vida à conversa! 🍄⭐"""


def upgrade() -> None:
    """Seed default Mario character."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO characters (name, description, catchphrase, personality_traits, image_url, system_prompt)
            SELECT :name, :description, :catchphrase, :traits, :image_url, :prompt
            WHERE NOT EXISTS (
                SELECT 1 FROM characters WHERE name = :name
            )
            """
        ),
        {
            "name": "Mario Bros",
            "description": "Herói do Reino dos Cogumelos, encanador carismático e corajoso.",
            "catchphrase": "It's-a me, Mario!",
            "traits": '["corajoso", "otimista", "engraçado"]',
            "image_url": "https://www.nintendo.com/eu/media/images/08_content_images/others_2/characterhubs/supermariohub/MarioHub_Overview_Mario_sideimg_mario.png",
            "prompt": MARIO_PROMPT,
        },
    )


def downgrade() -> None:
    """Remove default Mario character."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DELETE FROM characters WHERE name = :name"
        ),
        {"name": "Mario Bros"},
    )
