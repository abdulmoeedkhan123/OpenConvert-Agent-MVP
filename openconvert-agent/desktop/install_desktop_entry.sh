#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEST_DIR="${HOME}/.local/share/applications"
mkdir -p "${DEST_DIR}"

cp "${SCRIPT_DIR}/openconvert-agent.desktop" "${DEST_DIR}/openconvert-agent.desktop"
chmod +x "${SCRIPT_DIR}/openconvert-launcher.sh"
chmod +x "${DEST_DIR}/openconvert-agent.desktop"

if command -v xdg-desktop-menu >/dev/null 2>&1; then
  xdg-desktop-menu forceupdate
fi

echo "OpenConvert Agent desktop entry installed to ${DEST_DIR}/openconvert-agent.desktop"
