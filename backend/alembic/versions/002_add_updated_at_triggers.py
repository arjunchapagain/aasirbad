"""Add updated_at triggers for PostgreSQL

Revision ID: 002_add_triggers
Revises: 001_initial
Create Date: 2026-02-18
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002_add_triggers'
down_revision: str = '001_initial'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add PostgreSQL triggers to auto-update updated_at columns."""
    # Create trigger function (if not exists)
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Add trigger for users table
    op.execute("""
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)

    # Add trigger for voice_profiles table
    op.execute("""
    DROP TRIGGER IF EXISTS update_voice_profiles_updated_at ON voice_profiles;
    CREATE TRIGGER update_voice_profiles_updated_at
    BEFORE UPDATE ON voice_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Remove updated_at triggers."""
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    op.execute("DROP TRIGGER IF EXISTS update_voice_profiles_updated_at ON voice_profiles")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE")
