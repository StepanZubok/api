"""last columns

Revision ID: efbcd5a7dbbe
Revises: 5a6b0a1ccbce
Create Date: 2025-11-11 20:47:12.794949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efbcd5a7dbbe'
down_revision: Union[str, Sequence[str], None] = '5a6b0a1ccbce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "created_at")
