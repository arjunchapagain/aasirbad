#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root/backend"
[ "$(alembic heads 2>/dev/null | grep -c head)" = "1" ] || { echo "Multiple alembic heads"; exit 1; }
DB_BACKEND=sqlite python -m pytest -q
cd "$root/frontend" && npx tsc --noEmit
