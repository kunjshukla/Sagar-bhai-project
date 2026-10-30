#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="$PROJECT_ROOT/data/local-https"

cd "$PROJECT_ROOT"
set -a
source .env
set +a

exec .venv/bin/uvicorn mechman_bot.web:create_app --factory \
  --host 127.0.0.1 \
  --port 8443 \
  --ssl-certfile "$CERT_DIR/localhost.pem" \
  --ssl-keyfile "$CERT_DIR/localhost-key.pem"

