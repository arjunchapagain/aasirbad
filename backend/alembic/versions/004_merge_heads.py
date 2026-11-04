"""Merge the updated_at-trigger and enum-lowercase migration branches.

Revision ID: 004_merge_heads
Revises: 003_force_enum_lowercase, 002_add_triggers
"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '004_merge_heads'
down_revision: str | Sequence[str] | None = ('003_force_enum_lowercase', '002_add_triggers')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Pure merge; no schema changes."""


def downgrade() -> None:
    """Pure merge; no schema changes."""
