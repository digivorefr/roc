#!/usr/bin/env bash
# Stop-hook wrapper for rocket:context-update.
# Spawns a `claude -p --model "sonnet[1m]"` subprocess that updates the
# project lexicon at `<project>/.roc/rocket/lexicon.md` from the current
# session transcript. Runs async, never blocks the user.
#
# State layout (project-local):
#   .roc/rocket/lexicon.md             — the lexicon itself (committed)
#   .roc/rocket/lexicon-update.log     — wrapper log (gitignore)
#   .roc/rocket/lexicon.md.lock.d/     — atomic lock (gitignore)
#
# Path migration note: previous versions stored these under .claude/, but
# Claude Code's harness flags any .claude/ path as sensitive and refuses to
# permanently approve writes to it from sub-agents. The skill is unable to
# write back, the hook is silently broken. The migration to .roc/<plugin>/
# escapes the sensitive zone.

set -u

# Recursion guard: the `claude -p` subprocess we spawn below also fires Stop
# hooks and would re-invoke this script. The exported sentinel propagates to
# the subprocess; subsequent invocations exit immediately.
[ -n "${ROCKET_CONTEXT_UPDATE_INVOKED:-}" ] && exit 0
export ROCKET_CONTEXT_UPDATE_INVOKED=1

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
ROC_DIR="${PROJECT_DIR}/.roc/rocket"
LEXICON="${ROC_DIR}/lexicon.md"
LOCK_DIR="${ROC_DIR}/lexicon.md.lock.d"
LOG="${ROC_DIR}/lexicon-update.log"
DEBOUNCE_SECONDS=30
STALE_LOCK_SECONDS=600
LOG_MAX_BYTES=$((1024 * 1024))
LOG_KEEP=3
# Slice the trailing N lines of the transcript and pipe them through the
# strip preprocessor (siblings update-context-strip.py). The strip removes
# `signature`, `thinking`, `originalFile`, and image base64 payloads — these
# fields dominate the token count without carrying semantic signal — and
# stubs any line that remains over the per-line cap. With both a line cap
# and a per-line size cap, the worst case is bounded at ~4 MB which fits in
# sonnet[1m]'s 1M-token (~3.7 MB) context window.
TRANSCRIPT_TAIL_LINES=500
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRIP_SCRIPT="${SCRIPT_DIR}/update-context-strip.py"

# Read hook payload from stdin (Claude Code passes a JSON object on stdin).
PAYLOAD="$(cat || true)"

# Skip silently if the claude CLI or python3 is unavailable.
command -v claude >/dev/null 2>&1 || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

mkdir -p "${ROC_DIR}" || exit 0

# Rotate log if it exceeds the size cap.
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

# Debounce: skip if the lexicon was updated within the last DEBOUNCE_SECONDS seconds.
if [ -f "${LEXICON}" ]; then
  now=$(date +%s)
  mtime=$(stat -f %m "${LEXICON}" 2>/dev/null || stat -c %Y "${LEXICON}" 2>/dev/null || echo 0)
  if [ -n "${mtime}" ] && [ "$((now - mtime))" -lt "${DEBOUNCE_SECONDS}" ]; then
    log "skip: debounced (mtime ${mtime}, now ${now})"
    exit 0
  fi
fi

# Extract transcript_path from the JSON payload via python3 (already required
# above for the strip pipeline). Fall back to sed if python parsing fails for
# any reason.
TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("transcript_path",""))
except Exception:
    pass' 2>/dev/null)"
if [ -z "${TRANSCRIPT_PATH}" ]; then
  TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
fi

if [ -z "${TRANSCRIPT_PATH}" ] || [ ! -r "${TRANSCRIPT_PATH}" ]; then
  log "skip: transcript_path missing or unreadable"
  exit 0
fi

start=$(date +%s)
log "start: project=${PROJECT_DIR} transcript=${TRANSCRIPT_PATH}"

# Acquire a non-blocking exclusive lock via mkdir (atomic on POSIX, portable;
# flock is not available by default on macOS). Reap a stale lock if its mtime
# is older than STALE_LOCK_SECONDS — protects against crashed prior runs that
# could not clean up.
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

PROMPT='/rocket:context-update

The transcript of the current Claude Code session is provided on stdin (JSONL, one event per line). Each event has been preprocessed: `signature`, `thinking`, `originalFile`, and image base64 payloads are stripped or stubbed. Lines that exceeded the size cap are replaced by a small JSON stub. Run the context-update workflow against the remaining content and the project lexicon at `.roc/rocket/lexicon.md`.'

# Tail to TRANSCRIPT_TAIL_LINES, run through the strip preprocessor, pipe to
# the subprocess. cd into the project so the skill resolves
# .roc/rocket/lexicon.md relative to the right root.
transcript_total_lines=$(wc -l <"${TRANSCRIPT_PATH}" 2>/dev/null | tr -d ' ')
log "tailing transcript: ${transcript_total_lines} lines -> last ${TRANSCRIPT_TAIL_LINES} lines (with strip)"
(
  cd "${PROJECT_DIR}" || exit 1
  tail -n "${TRANSCRIPT_TAIL_LINES}" "${TRANSCRIPT_PATH}" \
    | python3 "${STRIP_SCRIPT}" \
    | claude -p --model "sonnet[1m]" "${PROMPT}" 2>>"${LOG}"
) >>"${LOG}"
status=$?

end=$(date +%s)
log "end: status=${status} duration=$((end - start))s"

# Always exit 0: this is an async hook. Returning the subprocess status would
# risk propagating exit code 2 (the Stop-hook block signal) to the user's main
# session, forcing Claude to keep responding when the subprocess hits an error.
exit 0
