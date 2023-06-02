"""Add audio_filename

Revision ID: 8225580d5e4d
Revises: 853c13259cfd
Create Date: 2023-06-02 10:51:16.503296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8225580d5e4d"
down_revision = "853c13259cfd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("audio_filename", sa.String(), nullable=True))
    op.execute("UPDATE interviews SET audio_filename = SUBSTR(audio_location, -32);")


def downgrade() -> None:
    op.drop_column("interviews", "audio_filename")
