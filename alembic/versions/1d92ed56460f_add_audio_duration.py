"""Add audio_duration

Revision ID: 1d92ed56460f
Revises: 9939aff3cbd4
Create Date: 2023-06-23 09:19:12.676409

"""
import librosa
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1d92ed56460f"
down_revision = "9939aff3cbd4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    try:
        op.drop_column("interviews", "audio_duration")
    except Exception:
        pass
    select_statement = sa.sql.text("SELECT id, audio_location FROM interviews")
    interviews = bind.execute(select_statement)
    updated = []
    for itw in interviews:
        itw_id, audio_location = itw
        audio_duration = librosa.get_duration(path=audio_location)
        updated.append({"id": itw_id, "audio_duration": audio_duration})

    op.add_column(
        "interviews",
        sa.Column(
            "audio_duration", sa.Float, nullable=False, server_default=sa.text("0.0")
        ),
    )
    upd_statement = sa.sql.text(
        "UPDATE interviews SET audio_duration = :audio_duration WHERE id=:id"
    )
    bind.execute(upd_statement, updated)


def downgrade() -> None:
    op.drop_column("interviews", "audio_duration")
