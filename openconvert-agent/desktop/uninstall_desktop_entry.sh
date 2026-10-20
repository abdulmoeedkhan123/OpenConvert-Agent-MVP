#!/usr/bin/env bash
set -euo pipefail

DEST_FILE="${HOME}/.local/share/applications/openconvert-agent.desktop"
rm -f "${DEST_FILE}"
if command -v xdg-desktop-menu >/dev/null 2>&1; then
  xdg-desktop-menu forceupdate
fi

echo "OpenConvert Agent desktop entry removed."
