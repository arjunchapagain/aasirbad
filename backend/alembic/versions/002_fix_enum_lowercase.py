"""
Migration to fix Postgres enum 'profilestatus' values to lowercase.

This migration will:
- Rename the existing enum type
- Create a new enum type with lowercase values
- Alter the table to use the new enum type
- Update any existing data if needed
- Drop the old enum type
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_fix_enum_lowercase'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Rename the old enum type
    op.execute("ALTER TYPE profilestatus RENAME TO profilestatus_old;")

    # Create the new enum type with lowercase values
    op.execute("""
        CREATE TYPE profilestatus AS ENUM (
            'pending', 'recording', 'processing', 'training', 'ready', 'failed', 'archived'
        );
    """)

    # Alter the column to use text temporarily
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE text;")

    # Update any existing data to lowercase (if any)
    op.execute("""
        UPDATE voice_profiles SET status = LOWER(status);
    """)

    # Alter the column to use the new enum type
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE profilestatus USING status::profilestatus;")

    # Drop the old enum type
    op.execute("DROP TYPE profilestatus_old;")

def downgrade():
    # Recreate the old enum type (with uppercase values)
    op.execute("""
        CREATE TYPE profilestatus_old AS ENUM (
            'PENDING', 'RECORDING', 'PROCESSING', 'TRAINING', 'READY', 'FAILED', 'ARCHIVED'
        );
    """)
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE text;")
    op.execute("UPDATE voice_profiles SET status = UPPER(status);")
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE profilestatus_old USING status::profilestatus_old;")
    op.execute("DROP TYPE profilestatus;")
    op.execute("ALTER TYPE profilestatus_old RENAME TO profilestatus;")
