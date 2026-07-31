#!/usr/bin/env bash
#
# One-command local runner for the Homoeo CDSS backend.
# Uses your local Postgres (trust auth as the current OS user) and the
# lightweight dev requirements. Overrides the committed .env so it "just works".
#
# Usage:
#   ./scripts/run_local.sh              # start backend on :8000
#   ANTHROPIC_API_KEY=sk-... ./scripts/run_local.sh   # enable real AI generation
#
set -euo pipefail
cd "$(dirname "$0")/.."

# --- config (overrides .env via environment precedence) ---
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB="${POSTGRES_DB:-homoeo_dev}"
export POSTGRES_USER="${POSTGRES_USER:-$(whoami)}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
export SECRET_KEY="${SECRET_KEY:-dev-secret-change-me}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
export VECTOR_STORE_DIR="$PWD/knowledge_base/_index"

echo "==> Ensuring database '$POSTGRES_DB' exists"
createdb "$POSTGRES_DB" 2>/dev/null && echo "   created" || echo "   already exists"

echo "==> Setting up Python venv + deps"
[ -d backend/.venv ] || python3 -m venv backend/.venv
# shellcheck disable=SC1091
source backend/.venv/bin/activate
pip install -q --upgrade pip
pip install -q -r backend/requirements-dev.txt

echo "==> Applying database migrations (alembic upgrade head)"
( cd backend && alembic upgrade head )

echo "==> Seeding materia medica knowledge base"
PYTHONPATH=backend python scripts/seed/index_knowledge_base.py

echo "==> Starting API at http://localhost:8000  (docs: /api/docs)"
# --reload-dir scoped to app/ so the watcher ignores .venv (avoids reload storms).
exec uvicorn app.main:app --app-dir backend --reload --reload-dir backend/app --host 127.0.0.1 --port 8000
