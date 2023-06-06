"""Add speakers

Revision ID: 9939aff3cbd4
Revises: 8225580d5e4d
Create Date: 2023-06-06 14:45:23.565437

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9939aff3cbd4"
down_revision = "8225580d5e4d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("speakers", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("interviews", "speakers")
