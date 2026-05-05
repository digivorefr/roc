#!/usr/bin/env bash
# shellcheck disable=SC2155
# Maintainer build script for the my-hand plugin.
#
# Produces one or both PyInstaller --onefile binaries at:
#   plugins/my-hand/bin/darwin-arm64/my-hand-grab
#   plugins/my-hand/bin/darwin-arm64/inbox-poll
#
# Usage:
#   bash plugins/my-hand/build/build.sh              # builds both
#   bash plugins/my-hand/build/build.sh grab          # builds my-hand-grab only
#   bash plugins/my-hand/build/build.sh inbox-poll    # builds inbox-poll only
#
# The my-hand-grab binary bundles cairo and its dylib dependencies so it
# runs on a fresh macOS-arm64 install without `brew install cairo`.
# cairocffi's dlopen lookup is redirected to the PyInstaller extraction
# directory via a runtime hook that sets DYLD_FALLBACK_LIBRARY_PATH
# before any cairocffi import.
#
# The inbox-poll binary has NO native C deps (no cairo, no dylib
# bundling), so its PyInstaller call is simpler.
#
# Run from any directory:
#   bash plugins/my-hand/build/build.sh
#
# Run twice = same behavior (idempotent). The build/.venv/, build/build/,
# build/dist/, and *.spec artefacts are wiped before exit on success.
#
# macOS-arm64 only. Linux/Intel Mac/Windows are out of scope.

set -euo pipefail

# ---------- Parse arguments ----------
BUILD_TARGET="${1:-all}"
case "${BUILD_TARGET}" in
  all|grab|inbox-poll) ;;
  *)
    echo "[build] error: unknown target '${BUILD_TARGET}'. Use: grab, inbox-poll, or omit for both." >&2
    exit 1
    ;;
esac

BUILD_GRAB=false
BUILD_INBOX_POLL=false
if [[ "${BUILD_TARGET}" == "all" || "${BUILD_TARGET}" == "grab" ]]; then
  BUILD_GRAB=true
fi
if [[ "${BUILD_TARGET}" == "all" || "${BUILD_TARGET}" == "inbox-poll" ]]; then
  BUILD_INBOX_POLL=true
fi

# ---------- Locate paths ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
GRAB_SRC="${SCRIPT_DIR}/src/grab.py"
INBOX_POLL_SRC="${SCRIPT_DIR}/src/inbox_poll.py"
VENV_DIR="${SCRIPT_DIR}/.venv"
WORK_DIR="${SCRIPT_DIR}/.pyinstaller-work"
DIST_DIR="${SCRIPT_DIR}/.pyinstaller-dist"
SPEC_DIR="${SCRIPT_DIR}/.pyinstaller-spec"
HOOK_FILE="${SCRIPT_DIR}/.pyinstaller-rthook.py"
BIN_DIR="${PLUGIN_DIR}/bin/darwin-arm64"

# ---------- Cleanup helpers ----------
cleanup() {
  rm -rf "${VENV_DIR}" "${WORK_DIR}" "${DIST_DIR}" "${SPEC_DIR}" "${HOOK_FILE}"
  rm -f "${SCRIPT_DIR}/my-hand-grab.spec" "${SCRIPT_DIR}/inbox-poll.spec" "${SCRIPT_DIR}/.dylib-seen"
}
trap 'echo "[build] failed; cleaning intermediates" >&2; cleanup' ERR

# ---------- Preflight checks ----------
if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "[build] error: this script targets darwin-arm64 only (got $(uname -s)/$(uname -m))." >&2
  exit 1
fi

if [[ "${BUILD_GRAB}" == "true" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "[build] error: Homebrew is required to discover cairo dylibs. Install brew first." >&2
    exit 1
  fi

  CAIRO_PREFIX="$(brew --prefix cairo 2>/dev/null || true)"
  if [[ -z "${CAIRO_PREFIX}" || ! -f "${CAIRO_PREFIX}/lib/libcairo.2.dylib" ]]; then
    echo "[build] error: 'brew install cairo' is required (libcairo.2.dylib not found)." >&2
    exit 1
  fi
fi

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

# ---------- Wipe any stale build artefacts ----------
echo "[build] cleaning previous build artefacts"
rm -rf "${VENV_DIR}" "${WORK_DIR}" "${DIST_DIR}" "${SPEC_DIR}" "${HOOK_FILE}"
rm -f "${SCRIPT_DIR}/my-hand-grab.spec" "${SCRIPT_DIR}/inbox-poll.spec"

# ---------- Create isolated venv ----------
echo "[build] creating venv at ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[build] installing pinned dependencies"
pip install --quiet --upgrade pip

if [[ "${BUILD_GRAB}" == "true" ]]; then
  pip install --quiet \
    "rmc==0.3.0" \
    "rmscene==0.6.1" \
    "cairosvg==2.9.0" \
    "pyinstaller"
else
  # inbox-poll only needs pyinstaller (no native deps).
  pip install --quiet "pyinstaller"
fi

# ---------- Build my-hand-grab ----------
if [[ "${BUILD_GRAB}" == "true" ]]; then
  echo ""
  echo "[build] === my-hand-grab ==="

  # Resolve dylibs to bundle.
  echo "[build] resolving dylib dependencies of libcairo"
  CAIRO_DYLIB="${CAIRO_PREFIX}/lib/libcairo.2.dylib"

  SEEN_FILE="${SCRIPT_DIR}/.dylib-seen"
  : > "${SEEN_FILE}"

  walk_deps() {
    local dylib="$1"
    local resolved
    resolved="$(/usr/bin/python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "${dylib}")"
    if grep -Fxq "${resolved}" "${SEEN_FILE}"; then
      return
    fi
    echo "${resolved}" >> "${SEEN_FILE}"
    while IFS= read -r line; do
      local dep
      dep="$(echo "${line}" | awk '{print $1}')"
      case "${dep}" in
        /opt/homebrew/*|/usr/local/*)
          if [[ -f "${dep}" ]]; then
            walk_deps "${dep}"
          fi
          ;;
        *)
          # System or self entry, skip.
          ;;
      esac
    done < <(otool -L "${resolved}" | tail -n +2)
  }

  walk_deps "${CAIRO_DYLIB}"

  echo "[build] dylibs to bundle:"
  while IFS= read -r d; do
    echo "  - ${d}"
  done < "${SEEN_FILE}"

  # Write the runtime hook.
  cat > "${HOOK_FILE}" <<'PYEOF'
"""PyInstaller runtime hook: redirect dylib lookup to the extraction dir.

Runs before user code. Prepends sys._MEIPASS to DYLD_FALLBACK_LIBRARY_PATH
so cairocffi finds the bundled libcairo (and its transitive Homebrew deps)
ahead of any system-installed cairo. Without this hook the binary requires
``brew install cairo`` on the user's machine, which V2 explicitly rejects.
"""
import os
import sys

meipass = getattr(sys, "_MEIPASS", None)
if meipass:
    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if existing:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = meipass + os.pathsep + existing
    else:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = meipass
PYEOF

  # Build with PyInstaller.
  echo "[build] running pyinstaller for my-hand-grab"
  ADD_BINARY_ARGS=()
  while IFS= read -r d; do
    ADD_BINARY_ARGS+=("--add-binary" "${d}:.")
  done < "${SEEN_FILE}"

  pyinstaller \
    --onefile \
    --name my-hand-grab \
    --distpath "${DIST_DIR}" \
    --workpath "${WORK_DIR}" \
    --specpath "${SPEC_DIR}" \
    --runtime-hook "${HOOK_FILE}" \
    --noconfirm \
    --log-level WARN \
    "${ADD_BINARY_ARGS[@]}" \
    "${GRAB_SRC}"

  rm -f "${SEEN_FILE}"

  # Move binary into place.
  mkdir -p "${BIN_DIR}"
  mv -f "${DIST_DIR}/my-hand-grab" "${BIN_DIR}/my-hand-grab"
  chmod +x "${BIN_DIR}/my-hand-grab"

  GRAB_PATH="${BIN_DIR}/my-hand-grab"
  echo "[build] my-hand-grab built"
  echo "  path: ${GRAB_PATH}"
  echo "  size: $(ls -lh "${GRAB_PATH}" | awk '{print $5}')"

  # Clean intermediate build artefacts between targets.
  rm -rf "${WORK_DIR}" "${DIST_DIR}" "${SPEC_DIR}" "${HOOK_FILE}"
fi

# ---------- Build inbox-poll ----------
if [[ "${BUILD_INBOX_POLL}" == "true" ]]; then
  echo ""
  echo "[build] === inbox-poll ==="

  echo "[build] running pyinstaller for inbox-poll"
  pyinstaller \
    --onefile \
    --name inbox-poll \
    --distpath "${DIST_DIR}" \
    --workpath "${WORK_DIR}" \
    --specpath "${SPEC_DIR}" \
    --noconfirm \
    --log-level WARN \
    "${INBOX_POLL_SRC}"

  # Move binary into place.
  mkdir -p "${BIN_DIR}"
  mv -f "${DIST_DIR}/inbox-poll" "${BIN_DIR}/inbox-poll"
  chmod +x "${BIN_DIR}/inbox-poll"

  INBOX_POLL_PATH="${BIN_DIR}/inbox-poll"
  echo "[build] inbox-poll built"
  echo "  path: ${INBOX_POLL_PATH}"
  echo "  size: $(ls -lh "${INBOX_POLL_PATH}" | awk '{print $5}')"
fi

# ---------- Cleanup ----------
echo ""
echo "[build] cleaning intermediates"
cleanup
trap - ERR

# ---------- Report ----------
echo ""
echo "[build] success"
if [[ "${BUILD_GRAB}" == "true" ]]; then
  echo "  my-hand-grab: ${BIN_DIR}/my-hand-grab ($(ls -lh "${BIN_DIR}/my-hand-grab" | awk '{print $5}'))"
fi
if [[ "${BUILD_INBOX_POLL}" == "true" ]]; then
  echo "  inbox-poll:   ${BIN_DIR}/inbox-poll ($(ls -lh "${BIN_DIR}/inbox-poll" | awk '{print $5}'))"
fi
