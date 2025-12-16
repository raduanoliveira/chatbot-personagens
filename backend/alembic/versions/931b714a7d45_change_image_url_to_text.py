"""change_image_url_to_text

Revision ID: 931b714a7d45
Revises: 001_refactor_characters
Create Date: 2025-12-16 17:11:09.706775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '931b714a7d45'
down_revision: Union[str, Sequence[str], None] = '001_refactor_characters'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
