"""Add synthesis_usage table for free-tier limits.

Revision ID: 005_synthesis_usage
Revises: 004_merge_heads
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '005_synthesis_usage'
down_revision: str | None = '004_merge_heads'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('voice_profiles',
                  sa.Column('consent_at', sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        'synthesis_usage',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('characters', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_synthesis_usage_user_id', 'synthesis_usage', ['user_id'])
    op.create_index('ix_synthesis_usage_created_at', 'synthesis_usage', ['created_at'])


def downgrade() -> None:
    op.drop_column('voice_profiles', 'consent_at')
    op.drop_table('synthesis_usage')
