#!/usr/bin/env bash
# shellcheck disable=SC2155
# Maintainer build script for the rocket plugin.
#
# Produces one PyInstaller --onefile binary at:
#   plugins/rocket/bin/context-gate
#
# Usage:
#   bash plugins/rocket/build/build.sh
#
# The context-gate binary has NO native C deps (pure Python, no dylib
# bundling), so the PyInstaller call is straightforward.
#
# Run from any directory:
#   bash plugins/rocket/build/build.sh
#
# Run twice = same behavior (idempotent). The build/.venv/, and
# PyInstaller intermediates are wiped before exit on success.

set -euo pipefail

# ---------- Locate paths ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC="${SCRIPT_DIR}/src/context_gate.py"
VENV_DIR="${SCRIPT_DIR}/.venv"
WORK_DIR="${SCRIPT_DIR}/.pyinstaller-work"
DIST_DIR="${SCRIPT_DIR}/.pyinstaller-dist"
SPEC_DIR="${SCRIPT_DIR}/.pyinstaller-spec"
BIN_DIR="${PLUGIN_DIR}/bin"

# ---------- Cleanup helpers ----------
cleanup() {
  rm -rf "${VENV_DIR}" "${WORK_DIR}" "${DIST_DIR}" "${SPEC_DIR}"
}
trap 'echo "[build] failed; cleaning intermediates" >&2; cleanup' ERR

# ---------- Preflight checks ----------
if ! command -v python3 >/dev/null 2>&1; then
  echo "[build] error: python3 is required on PATH." >&2
  exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
PYTHON_MAJOR="$(echo "${PYTHON_VERSION}" | cut -d. -f1)"
PYTHON_MINOR="$(echo "${PYTHON_VERSION}" | cut -d. -f2)"
if [[ "${PYTHON_MAJOR}" -lt 3 || ( "${PYTHON_MAJOR}" -eq 3 && "${PYTHON_MINOR}" -lt 11 ) ]]; then
  echo "[build] error: Python 3.11+ required (got ${PYTHON_VERSION})." >&2
  exit 1
fi

if [[ ! -f "${SRC}" ]]; then
  echo "[build] error: source not found at ${SRC}" >&2
  exit 1
fi

# ---------- Wipe any stale build artefacts ----------
echo "[build] cleaning previous build artefacts"
rm -rf "${VENV_DIR}" "${WORK_DIR}" "${DIST_DIR}" "${SPEC_DIR}"

# ---------- Create isolated venv ----------
echo "[build] creating venv at ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[build] installing pyinstaller"
pip install --quiet --upgrade pip
pip install --quiet "pyinstaller"

# ---------- Build context-gate ----------
echo ""
echo "[build] === context-gate ==="

echo "[build] running pyinstaller for context-gate"
pyinstaller \
  --onefile \
  --name context-gate \
  --distpath "${DIST_DIR}" \
  --workpath "${WORK_DIR}" \
  --specpath "${SPEC_DIR}" \
  --noconfirm \
  --log-level WARN \
  "${SRC}"

# Move binary into place.
mkdir -p "${BIN_DIR}"
mv -f "${DIST_DIR}/context-gate" "${BIN_DIR}/context-gate"
chmod +x "${BIN_DIR}/context-gate"

BIN_PATH="${BIN_DIR}/context-gate"
echo "[build] context-gate built"
echo "  path: ${BIN_PATH}"
echo "  size: $(ls -lh "${BIN_PATH}" | awk '{print $5}')"

# ---------- Cleanup ----------
echo ""
echo "[build] cleaning intermediates"
cleanup
trap - ERR

# ---------- Report ----------
echo ""
echo "[build] success"
echo "  context-gate: ${BIN_DIR}/context-gate ($(ls -lh "${BIN_DIR}/context-gate" | awk '{print $5}'))"
