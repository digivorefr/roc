#!/usr/bin/env bash
# Stop-hook wrapper for rocket:context-update.
# Spawns a Haiku-tier `claude -p` subprocess that updates .claude/lexicon.md
# from the current session transcript. Runs async, never blocks the user.

set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CLAUDE_DIR="${PROJECT_DIR}/.claude"
LEXICON="${CLAUDE_DIR}/lexicon.md"
LOCK="${CLAUDE_DIR}/lexicon.md.lock"
LOG="${CLAUDE_DIR}/lexicon-update.log"
DEBOUNCE_SECONDS=30
LOG_MAX_BYTES=$((1024 * 1024))
LOG_KEEP=3

# Read hook payload from stdin (Claude Code passes a JSON object on stdin).
PAYLOAD="$(cat || true)"

# Skip silently if the claude CLI is unavailable.
command -v claude >/dev/null 2>&1 || exit 0

mkdir -p "${CLAUDE_DIR}" || exit 0

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

# Extract transcript_path from the JSON payload without requiring jq.
TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"

if [ -z "${TRANSCRIPT_PATH}" ] || [ ! -r "${TRANSCRIPT_PATH}" ]; then
  log "skip: transcript_path missing or unreadable"
  exit 0
fi

start=$(date +%s)
log "start: project=${PROJECT_DIR} transcript=${TRANSCRIPT_PATH}"

# Acquire a non-blocking exclusive lock; bail out if another run is in progress.
exec 9>"${LOCK}" || exit 0
if ! flock -n 9; then
  log "skip: lock held by another invocation"
  exit 0
fi

PROMPT='/rocket:context-update

The transcript of the current Claude Code session is provided on stdin (JSONL, one event per line). Run the context-update workflow against it and the project lexicon.'

# Pipe the transcript on stdin to the subprocess. cd into the project so the
# skill resolves .claude/lexicon.md relative to the right root.
(
  cd "${PROJECT_DIR}" || exit 1
  cat "${TRANSCRIPT_PATH}" | claude -p --model haiku "${PROMPT}" 2>>"${LOG}"
) >>"${LOG}"
status=$?

end=$(date +%s)
log "end: status=${status} duration=$((end - start))s"

exit "${status}"
