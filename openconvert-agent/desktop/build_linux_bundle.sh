#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"
BUNDLE_DIR="${DIST_DIR}/openconvert-agent-desktop"
ZIP_PATH="${DIST_DIR}/openconvert-agent-desktop.zip"

mkdir -p "${BUNDLE_DIR}"
cp "${SCRIPT_DIR}/openconvert-launcher.sh" "${BUNDLE_DIR}/openconvert-launcher.sh"
cp "${SCRIPT_DIR}/openconvert-agent.desktop" "${BUNDLE_DIR}/openconvert-agent.desktop"
cp "${SCRIPT_DIR}/install_desktop_entry.sh" "${BUNDLE_DIR}/install_desktop_entry.sh"
cp "${SCRIPT_DIR}/uninstall_desktop_entry.sh" "${BUNDLE_DIR}/uninstall_desktop_entry.sh"
cp "${REPO_ROOT}/README.md" "${BUNDLE_DIR}/README.md"
chmod +x "${BUNDLE_DIR}/openconvert-launcher.sh" "${BUNDLE_DIR}/install_desktop_entry.sh" "${BUNDLE_DIR}/uninstall_desktop_entry.sh"

rm -f "${ZIP_PATH}"
(cd "${DIST_DIR}" && zip -rq "openconvert-agent-desktop.zip" "openconvert-agent-desktop")

echo "Built desktop bundle: ${ZIP_PATH}"
