#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORTAL_DIR="$PROJECT_ROOT/portal"
CERT_DIR="$PROJECT_ROOT/data/local-https"
LOCAL_API="https://localhost:8443"
SCREEN_NAME="mechman-local-https"

for command_name in curl mkcert screen vercel; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

if [[ ! -x "$PROJECT_ROOT/.venv/bin/uvicorn" || ! -f "$PROJECT_ROOT/.env" ]]; then
  echo "The project .venv or .env file is missing." >&2
  exit 1
fi

mkdir -p "$CERT_DIR"
chmod +x "$PROJECT_ROOT/scripts/run_local_https_service.sh"

if ! security find-certificate -a -c mkcert "$HOME/Library/Keychains/login.keychain-db" \
  >/dev/null 2>&1; then
  security add-trusted-cert -r trustRoot \
    -k "$HOME/Library/Keychains/login.keychain-db" \
    "$(mkcert -CAROOT)/rootCA.pem"
fi
mkcert \
  -cert-file "$CERT_DIR/localhost.pem" \
  -key-file "$CERT_DIR/localhost-key.pem" \
  localhost 127.0.0.1 ::1
chmod 600 "$CERT_DIR/localhost-key.pem"

launchctl bootout "gui/$(id -u)/com.mechman.local-https" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.mechman.local-https.plist"
screen -S "$SCREEN_NAME" -X quit >/dev/null 2>&1 || true
existing_pid="$(lsof -tiTCP:8443 -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "$existing_pid" ]] && ps -p "$existing_pid" -o command= | grep -q 'mechman_bot.web:create_app'; then
  kill "$existing_pid"
  for _ in {1..20}; do
    kill -0 "$existing_pid" 2>/dev/null || break
    sleep 0.1
  done
fi
screen -wipe >/dev/null 2>&1 || true
screen -dmS "$SCREEN_NAME" /bin/bash -lc \
  "exec '$PROJECT_ROOT/scripts/run_local_https_service.sh' >>'$CERT_DIR/backend.log' 2>>'$CERT_DIR/backend.error.log'"

healthy=false
for _ in {1..30}; do
  if curl --fail --silent --max-time 5 "$LOCAL_API/healthz" >/dev/null 2>&1; then
    healthy=true
    break
  fi
  sleep 1
done

if [[ "$healthy" != true ]]; then
  echo "Local HTTPS backend did not become healthy. See $CERT_DIR/backend.error.log" >&2
  exit 1
fi

(
  cd "$PORTAL_DIR"
  vercel env rm VITE_API_URL production --yes >/dev/null 2>&1 || true
  printf '%s\n' "$LOCAL_API" | vercel env add VITE_API_URL production >/dev/null
  vercel --prod --yes
)

echo
echo "Local HTTPS API: $LOCAL_API"
echo "Vercel dashboard: https://portal-gamma-tan-62.vercel.app/login"
echo "Background session: screen -r $SCREEN_NAME"

