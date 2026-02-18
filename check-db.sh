#!/bin/bash
# Database diagnostic script
# Run this to check your database setup

echo "=== Database Diagnostic ==="
echo ""

# Check if docker-compose is being used
if docker-compose ps postgres &>/dev/null; then
    echo "✓ Using Docker Compose"
    echo ""
    
    echo "Postgres container status:"
    docker-compose ps postgres
    echo ""
    
    echo "Checking postgres logs (last 20 lines):"
    docker-compose logs --tail=20 postgres
    echo ""
    
    echo "Checking if tables exist:"
    docker-compose exec -T postgres psql -U aasirbad -d aasirbad -c "\dt" 2>&1
    echo ""
    
    echo "Checking migration status:"
    docker-compose exec -T postgres psql -U aasirbad -d aasirbad -c "SELECT * FROM alembic_version;" 2>&1
    echo ""
    
else
    echo "Docker Compose not detected, checking local PostgreSQL..."
    echo ""
    
    if command -v psql &>/dev/null; then
        echo "✓ psql found"
        echo ""
        
        echo "Checking if database exists:"
        psql -U aasirbad -d aasirbad -c "SELECT version();" 2>&1
        echo ""
        
        echo "Checking if tables exist:"
        psql -U aasirbad -d aasirbad -c "\dt" 2>&1
        echo ""
        
        echo "Checking migration status:"
        psql -U aasirbad -d aasirbad -c "SELECT * FROM alembic_version;" 2>&1
        echo ""
    else
        echo "✗ psql not found"
    fi
fi

echo "=== Recommendations ==="
echo ""
echo "If you see 'relation does not exist' errors above:"
echo "  → Database tables haven't been created. Run: alembic upgrade head"
echo ""
echo "If postgres container is not running:"
echo "  → Run: docker-compose up -d postgres"
echo ""
echo "If you see 'connection refused' errors:"
echo "  → Check your DATABASE_URL environment variable"
echo "  → Make sure postgres is accessible on the expected host/port"
echo ""
