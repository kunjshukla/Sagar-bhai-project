#!/usr/bin/env bash

set -euo pipefail

screen -S mechman-local-https -X quit >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)/com.mechman.local-https" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.mechman.local-https.plist"

echo "Stopped the Mechman local HTTPS service."

