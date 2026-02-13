"""Initial schema - users, voice_profiles, recordings

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users table ──────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # ── Voice Profiles table ─────────────────────────────────────────────
    op.create_table(
        'voice_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('pending', 'recording', 'processing', 'training', 'ready', 'failed', 'archived',
                     name='profilestatus'),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('recording_token', sa.String(64), nullable=False),
        sa.Column('total_recordings', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_duration_seconds', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('model_path', sa.String(512), nullable=True),
        sa.Column('training_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('training_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('training_error', sa.Text(), nullable=True),
        sa.Column('training_progress', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('voice_similarity_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_voice_profiles_user_id', 'voice_profiles', ['user_id'])
    op.create_index('ix_voice_profiles_recording_token', 'voice_profiles', ['recording_token'], unique=True)

    # ── Recordings table ─────────────────────────────────────────────────
    op.create_table(
        'recordings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('voice_profile_id', sa.Uuid(), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('prompt_index', sa.Integer(), nullable=False),
        sa.Column(
            'status',
            sa.Enum('uploaded', 'processing', 'processed', 'rejected', 'failed',
                     name='recordingstatus'),
            nullable=False,
            server_default='uploaded',
        ),
        sa.Column('original_file_path', sa.String(512), nullable=False),
        sa.Column('processed_file_path', sa.String(512), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('sample_rate', sa.Integer(), nullable=False),
        sa.Column('snr_db', sa.Float(), nullable=True),
        sa.Column('rms_level', sa.Float(), nullable=True),
        sa.Column('clipping_detected', sa.Boolean(), nullable=True),
        sa.Column('silence_ratio', sa.Float(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['voice_profile_id'], ['voice_profiles.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_recordings_voice_profile_id', 'recordings', ['voice_profile_id'])


def downgrade() -> None:
    op.drop_table('recordings')
    op.drop_table('voice_profiles')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS recordingstatus")
    op.execute("DROP TYPE IF EXISTS profilestatus")
