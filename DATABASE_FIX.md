# Database Fix - Updated_at Triggers & Sign-in Issues

## Problems
1. **Voice registration error** - Internal server error when registering a voice profile
2. **Sign-in issues** - Unable to sign in after attempting the fix

## Root Causes
1. PostgreSQL doesn't automatically update `updated_at` columns - requires explicit triggers
2. Database migrations not properly applied or database not created

## Solution
Added PostgreSQL triggers + proper migration steps to ensure database is correctly set up.

## Files Changed
1. **backend/alembic/versions/001_initial.py** - Updated initial migration to include triggers
2. **backend/alembic/versions/002_add_updated_at_triggers.py** - New migration for existing databases

## How to Apply the Fix

### Step 0: Check Database Connection
First, verify your database is running and accessible:

```bash
# If using Docker Compose
docker-compose ps  # Check if postgres container is running
docker-compose logs postgres  # Check postgres logs

# If using local PostgreSQL
psql -U aasirbad -d aasirbad -c "SELECT 1;"  # Test connection
```

### Step 1: Apply Database Migrations

**RECOMMENDED: Docker Compose (Fresh Start)**
```bash
# Stop all containers
docker-compose down

# Remove the database volume (WARNING: This deletes all data!)
docker volume rm aasirbad_postgres_data

# Start services (postgres will recreate the database)
docker-compose up -d postgres redis

# Wait for postgres to be ready
sleep 5

# Run migrations inside the backend container OR from your host
docker-compose run --rm api alembic upgrade head

# Start all services
docker-compose up -d
```

**Alternative: Existing Database (Keep Data)**
```bash
cd backend
# Just apply new migrations
alembic upgrade head
```

### Step 2: Verify the Fix
After applying migrations, check that tables exist:

```bash
# Using Docker
docker-compose exec postgres psql -U aasirbad -d aasirbad -c "\dt"

# Using local psql
psql -U aasirbad -d aasirbad -c "\dt"
```

You should see tables: `users`, `voice_profiles`, `recordings`, `alembic_version`

### Step 3: Test the Application
1. Restart the backend: `docker-compose restart api` or restart your dev server
2. Try to sign up a new user
3. Try to sign in with the new user
4. Try to create a voice profile

## Troubleshooting

### "Can't connect to database" error
```bash
# Check if postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### "relation 'users' does not exist" error
This means migrations haven't run. Follow Step 1 above to run migrations.

### "Invalid credentials" when signing in
- Make sure you created a new account AFTER running the migrations
- Old accounts may not exist if you recreated the database

### Still having issues?
```bash
# Check alembic migration status
cd backend
alembic current  # Should show: 002_add_triggers (or 001_initial for fresh installs)
alembic history  # Show all available migrations

# Check if tables exist
docker-compose exec postgres psql -U aasirbad -d aasirbad -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

## Technical Details
The fix adds a PostgreSQL function and triggers:
- `update_updated_at_column()` - PL/pgSQL function that sets `NEW.updated_at = NOW()`
- Triggers on `users` and `voice_profiles` tables that call this function before updates

This ensures `updated_at` columns are automatically maintained at the database level, not just the application level.
