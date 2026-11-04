# Database Fix - Updated_at Triggers

## Problem
When registering a voice profile (or updating any record), the application was failing with an internal server error because PostgreSQL doesn't automatically update `updated_at` columns - it requires explicit triggers.

## Root Cause
The SQLAlchemy models had `onupdate=func.now()` which only works at the ORM level, not at the database level. PostgreSQL needs explicit triggers to auto-update `updated_at` timestamps.

## Solution
Added PostgreSQL triggers to automatically update `updated_at` columns when rows are modified.

## Files Changed
1. **backend/alembic/versions/001_initial.py** - Updated initial migration to include triggers
2. **backend/alembic/versions/002_add_updated_at_triggers.py** - New migration for existing databases

## How to Apply the Fix

### Option 1: Fresh Database (New Installation)
If you're starting fresh or can recreate the database:

```bash
cd backend
# Drop and recreate the database
alembic downgrade base  # or drop the database manually
alembic upgrade head    # This will use the updated 001_initial.py with triggers
```

### Option 2: Existing Database (Recommended)
If you have an existing database with data:

```bash
cd backend
# Just run the new migration
alembic upgrade head
```

This will apply migration `002_add_updated_at_triggers.py` which adds the triggers to existing tables.

### Option 3: Using Docker Compose
```bash
# Stop containers
docker-compose down

# Remove the database volume (WARNING: This deletes all data!)
docker volume rm aasirbad_postgres_data

# Start fresh with the fixed migration
docker-compose up -d
```

## Verification
After applying the fix, test by:
1. Creating a new voice profile via the website
2. Updating user information
3. Check that no "internal server error" occurs

## Technical Details
The fix adds a PostgreSQL function and triggers:
- `update_updated_at_column()` - PL/pgSQL function that sets `NEW.updated_at = NOW()`
- Triggers on `users` and `voice_profiles` tables that call this function before updates

This ensures `updated_at` columns are automatically maintained at the database level, not just the application level.
