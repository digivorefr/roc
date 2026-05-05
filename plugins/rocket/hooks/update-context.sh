#!/usr/bin/env bash
# Stop-hook wrapper for rocket:context-update (v2 — hybrid gate architecture).
#
# Multi-stage pipeline:
#   1. Recursion guard
#   2. Project toggle (Background context: enabled/disabled)
#   3. Extract transcript path from stdin payload
#   4. Read cursor (last processed transcript line)
#   5. Debounce (lexicon mtime < 300s)
#   6. Extract delta via context-gate binary
#   7. Heuristic pre-filter via context-gate binary
#   8. Haiku gate (claude -p --model haiku)
#   9. Acquire lock
#  10. Sonnet writer (claude -p --model "sonnet[1m]" with scoped prompt)
#  11. Update cursor + unlock
#
# State layout (project-local):
#   .roc/rocket/lexicon.md                  — the lexicon itself (committed)
#   .roc/rocket/lexicon-update.log          — wrapper log (gitignore)
#   .roc/rocket/lexicon.md.lock.d/          — atomic lock (gitignore)
#   .roc/rocket/context-gate-state.json     — cursor position (gitignore)

set -u

# ---------- 1. Recursion guard ----------
[ -n "${ROCKET_CONTEXT_UPDATE_INVOKED:-}" ] && exit 0
export ROCKET_CONTEXT_UPDATE_INVOKED=1

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# ---------- 2. Project toggle ----------
CLAUDE_MD="${PROJECT_DIR}/CLAUDE.md"
if [ -f "${CLAUDE_MD}" ]; then
  if ! grep -qiE '^\s*-\s*Background context\s*:\s*enabled' "${CLAUDE_MD}"; then
    exit 0
  fi
else
  exit 0
fi

# ---------- Constants ----------
ROC_DIR="${PROJECT_DIR}/.roc/rocket"
LEXICON="${ROC_DIR}/lexicon.md"
LOCK_DIR="${ROC_DIR}/lexicon.md.lock.d"
LOG="${ROC_DIR}/lexicon-update.log"
GATE_STATE="${ROC_DIR}/context-gate-state.json"
DEBOUNCE_SECONDS=300
STALE_LOCK_SECONDS=600
LOG_MAX_BYTES=$((1024 * 1024))
LOG_KEEP=3
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
GATE_BIN="${PLUGIN_DIR}/bin/context-gate"

# Read hook payload from stdin (Claude Code passes a JSON object on stdin).
PAYLOAD="$(cat || true)"

# Skip silently if the claude CLI is unavailable.
command -v claude >/dev/null 2>&1 || exit 0

mkdir -p "${ROC_DIR}" || exit 0

# ---------- Rotate log ----------
if [ -f "${LOG}" ]; then
  size=$(wc -c <"${LOG}" 2>/dev/null | tr -d ' ')
  if [ -n "${size}" ] && [ "${size}" -ge "${LOG_MAX_BYTES}" ]; then
    i=$((LOG_KEEP - 1))
    while [ "${i}" -ge 1 ]; do
      [ -f "${LOG}.${i}" ] && mv -f "${LOG}.${i}" "${LOG}.$((i + 1))"
      i=$((i - 1))
    done
    mv -f "${LOG}" "${LOG}.1"
  fi
fi

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"${LOG}"; }

# ---------- Shared helpers ----------
# Extract transcript_path from the hook payload JSON. Tries python3 first,
# falls back to sed. Sets TRANSCRIPT_PATH or leaves it empty.
extract_transcript_path() {
  TRANSCRIPT_PATH=""
  if command -v python3 >/dev/null 2>&1; then
    TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("transcript_path",""))
except Exception:
    pass' 2>/dev/null || true)"
  fi
  if [ -z "${TRANSCRIPT_PATH}" ]; then
    TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
  fi
}

# ---------- Check binary availability ----------
# If the context-gate binary is missing, fall back to v1 behavior.
if [ ! -x "${GATE_BIN}" ]; then
  log "warn: context-gate binary not found at ${GATE_BIN}, falling back to v1"

  # v1 fallback: debounce, tail 500 lines, pipe to Sonnet
  if [ -f "${LEXICON}" ]; then
    now=$(date +%s)
    mtime=$(stat -f %m "${LEXICON}" 2>/dev/null || stat -c %Y "${LEXICON}" 2>/dev/null || echo 0)
    if [ -n "${mtime}" ] && [ "$((now - mtime))" -lt 30 ]; then
      log "skip: debounced (v1 fallback, mtime ${mtime}, now ${now})"
      exit 0
    fi
  fi

  extract_transcript_path

  if [ -z "${TRANSCRIPT_PATH}" ] || [ ! -r "${TRANSCRIPT_PATH}" ]; then
    exit 0
  fi

  if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
    exit 0
  fi
  trap 'rmdir "${LOCK_DIR}" 2>/dev/null' EXIT INT TERM HUP

  PROMPT='/rocket:context-update

The transcript of the current Claude Code session is provided on stdin (JSONL, one event per line). Run the context-update workflow against the remaining content and the project lexicon at `.roc/rocket/lexicon.md`.'

  (
    cd "${PROJECT_DIR}" || exit 1
    tail -n 500 "${TRANSCRIPT_PATH}" \
      | claude -p --model "sonnet[1m]" "${PROMPT}" 2>>"${LOG}"
  ) >>"${LOG}"
  exit 0
fi

# ---------- 3. Extract transcript path ----------
extract_transcript_path

if [ -z "${TRANSCRIPT_PATH}" ] || [ ! -r "${TRANSCRIPT_PATH}" ]; then
  log "skip: transcript_path missing or unreadable"
  exit 0
fi

# ---------- 4. Read cursor ----------
CURSOR=$("${GATE_BIN}" read-cursor --state "${GATE_STATE}")
TRANSCRIPT_TOTAL_LINES=$(wc -l <"${TRANSCRIPT_PATH}" 2>/dev/null | tr -d ' ')

if [ "${CURSOR}" -ge "${TRANSCRIPT_TOTAL_LINES}" ] 2>/dev/null; then
  exit 0
fi

# ---------- 5. Debounce (300s) ----------
if [ -f "${LEXICON}" ]; then
  now=$(date +%s)
  mtime=$(stat -f %m "${LEXICON}" 2>/dev/null || stat -c %Y "${LEXICON}" 2>/dev/null || echo 0)
  if [ -n "${mtime}" ] && [ "$((now - mtime))" -lt "${DEBOUNCE_SECONDS}" ]; then
    # Advance cursor even on debounce skip
    "${GATE_BIN}" update-cursor --state "${GATE_STATE}" --line "${TRANSCRIPT_TOTAL_LINES}"
    log "skip: debounced (mtime ${mtime}, now ${now})"
    exit 0
  fi
fi

# ---------- 6. Extract delta ----------
DELTA_JSON=$("${GATE_BIN}" extract-delta --transcript "${TRANSCRIPT_PATH}" --since-line "${CURSOR}")

# Parse all fields from the delta JSON in a single python3 call.
# Output: "content_lines tool_only has_user has_prose"
DELTA_FIELDS=$("${GATE_BIN}" parse-delta-fields <<< "${DELTA_JSON}" 2>/dev/null || echo "0 true false false")
read -r CONTENT_LINES TOOL_ONLY HAS_USER HAS_PROSE <<< "${DELTA_FIELDS}"

log "delta: content_lines=${CONTENT_LINES} tool_only=${TOOL_ONLY} has_user=${HAS_USER} has_prose=${HAS_PROSE}"

# ---------- 7. Heuristic pre-filter ----------
SHOULD=$("${GATE_BIN}" should-fire --content-lines "${CONTENT_LINES}" --tool-only "${TOOL_ONLY}" \
           --has-user-message "${HAS_USER}" --has-assistant-prose "${HAS_PROSE}")

if [ "${SHOULD}" = "no" ]; then
  "${GATE_BIN}" update-cursor --state "${GATE_STATE}" --line "${TRANSCRIPT_TOTAL_LINES}"
  log "skip: heuristic rejected (content_lines=${CONTENT_LINES}, tool_only=${TOOL_ONLY})"
  exit 0
fi

# ---------- 8. Haiku gate ----------
DELTA_TEXT=$("${GATE_BIN}" extract-delta-text <<< "${DELTA_JSON}" 2>/dev/null || echo "")
GATE_PROMPT=$(printf '%s' "${DELTA_TEXT}" | "${GATE_BIN}" format-gate-prompt --lexicon "${LEXICON}")
GATE_RESPONSE=$(printf '%s' "${GATE_PROMPT}" | claude -p --model haiku 2>>"${LOG}")
GATE_RESULT=$(printf '%s' "${GATE_RESPONSE}" | "${GATE_BIN}" parse-gate-response)

if [ "${GATE_RESULT}" = "no" ]; then
  "${GATE_BIN}" update-cursor --state "${GATE_STATE}" --line "${TRANSCRIPT_TOTAL_LINES}"
  log "skip: haiku gate rejected"
  exit 0
fi

log "haiku gate passed: ${GATE_RESULT}"

# ---------- 9. Acquire lock ----------
start=$(date +%s)
log "start: project=${PROJECT_DIR} transcript=${TRANSCRIPT_PATH}"

if [ -d "${LOCK_DIR}" ]; then
  lock_mtime=$(stat -f %m "${LOCK_DIR}" 2>/dev/null || stat -c %Y "${LOCK_DIR}" 2>/dev/null || echo 0)
  if [ -n "${lock_mtime}" ] && [ "$(($(date +%s) - lock_mtime))" -ge "${STALE_LOCK_SECONDS}" ]; then
    log "reaping stale lock (mtime ${lock_mtime})"
    rmdir "${LOCK_DIR}" 2>/dev/null || rm -rf "${LOCK_DIR}"
  fi
fi
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  log "skip: lock held by another invocation"
  exit 0
fi
trap 'rmdir "${LOCK_DIR}" 2>/dev/null' EXIT INT TERM HUP

# ---------- 10. Sonnet writer (scoped prompt) ----------
WRITER_PROMPT=$(printf '%s' "${GATE_RESULT}" | "${GATE_BIN}" format-writer-prompt \
                  --lexicon "${LEXICON}" --claude-md "${CLAUDE_MD}")

(
  cd "${PROJECT_DIR}" || exit 1
  printf '%s' "${WRITER_PROMPT}" | claude -p --model "sonnet[1m]" 2>>"${LOG}"
) >>"${LOG}"
status=$?

# ---------- 11. Update cursor + unlock ----------
"${GATE_BIN}" update-cursor --state "${GATE_STATE}" --line "${TRANSCRIPT_TOTAL_LINES}"

end=$(date +%s)
log "end: status=${status} duration=$((end - start))s"

# Always exit 0: this is an async hook. Returning the subprocess status would
# risk propagating exit code 2 (the Stop-hook block signal) to the user's main
# session.
exit 0
