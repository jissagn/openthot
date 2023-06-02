"""Move transcript field to raw

Revision ID: 514ed3b64736
Revises:
Create Date: 2023-06-01 12:25:07.966329

"""
from alembic import op

# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "514ed3b64736"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("interviews", "transcript", new_column_name="transcript_raw")


def downgrade() -> None:
    op.alter_column("interviews", "transcript_raw", new_column_name="transcript")
