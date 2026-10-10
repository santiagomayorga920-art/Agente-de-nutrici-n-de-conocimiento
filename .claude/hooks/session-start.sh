#!/bin/bash
# Prepara cada sesión en la nube: entorno Python, .env, grafo de Graphify y hooks de git.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -e ".[dev,telegram]"

[ -f .env ] || cp .env.example .env

.venv/bin/graphify update . >/dev/null
.venv/bin/graphify hook install >/dev/null

echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
