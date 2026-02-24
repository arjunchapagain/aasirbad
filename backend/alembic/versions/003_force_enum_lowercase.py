"""
Force recreate Postgres enum 'profilestatus' with lowercase values and update all data.
"""
from alembic import op
import sqlalchemy as sa

revision = '003_force_enum_lowercase'
down_revision = '002_fix_enum_lowercase'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Set all status values to lowercase (if any left)
    op.execute("UPDATE voice_profiles SET status = LOWER(status);")

    # 2. Drop default and constraints
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status DROP DEFAULT;")

    # 3. Rename the old enum type
    op.execute("ALTER TYPE profilestatus RENAME TO profilestatus_old2;")

    # 4. Create the new enum type with lowercase values
    op.execute("""
        CREATE TYPE profilestatus AS ENUM (
            'pending', 'recording', 'processing', 'training', 'ready', 'failed', 'archived'
        );
    """)

    # 5. Alter the column to use text temporarily
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE text;")

    # 6. Update any remaining data to lowercase (safety)
    op.execute("UPDATE voice_profiles SET status = LOWER(status);")

    # 7. Alter the column to use the new enum type
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status TYPE profilestatus USING status::profilestatus;")

    # 8. Set default back if needed
    op.execute("ALTER TABLE voice_profiles ALTER COLUMN status SET DEFAULT 'pending';")

    # 9. Drop the old enum type
    op.execute("DROP TYPE profilestatus_old2;")

def downgrade():
    pass  # Not needed for this fix
