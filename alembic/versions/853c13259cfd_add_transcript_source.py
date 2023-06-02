"""Add transcript source

Revision ID: 853c13259cfd
Revises: 514ed3b64736
Create Date: 2023-06-01 12:43:03.451847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "853c13259cfd"
down_revision = "514ed3b64736"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews", sa.Column("transcript_source", sa.String(), nullable=True)
    )
    op.execute("UPDATE interviews SET transcript_source = 'whisper';")


def downgrade() -> None:
    op.drop_column("interviews", "transcript_source")
