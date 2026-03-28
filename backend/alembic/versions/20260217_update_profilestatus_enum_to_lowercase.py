"""
Update profilestatus enum to use lowercase values
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260217_update_profilestatus_enum_to_lowercase'
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

    # Alter the column to use the new type
    op.execute("""
        ALTER TABLE voice_profiles
        ALTER COLUMN status TYPE profilestatus USING LOWER(status)::profilestatus;
    """)

    # Drop the old enum type
    op.execute("DROP TYPE profilestatus_old;")

def downgrade():
    # Recreate the old enum type with uppercase values
    op.execute("""
        CREATE TYPE profilestatus_old AS ENUM (
            'PENDING', 'RECORDING', 'PROCESSING', 'TRAINING', 'READY', 'FAILED', 'ARCHIVED'
        );
    """)

    # Alter the column to use the old type
    op.execute("""
        ALTER TABLE voice_profiles
        ALTER COLUMN status TYPE profilestatus_old USING UPPER(status)::profilestatus_old;
    """)

    # Drop the new enum type
    op.execute("DROP TYPE profilestatus;")

    # Rename the old type back
    op.execute("ALTER TYPE profilestatus_old RENAME TO profilestatus;")
