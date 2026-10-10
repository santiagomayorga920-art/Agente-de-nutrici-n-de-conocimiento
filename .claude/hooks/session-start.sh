#!/bin/bash
# Prepara cada sesión en la nube: entorno Python, .env y grafo de Graphify.
# Sin hooks de git de Graphify: regeneran el grafo tras cada commit y dejan el árbol siempre sucio.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -e ".[dev]"

[ -f .env ] || cp .env.example .env

.venv/bin/graphify update . >/dev/null

echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
