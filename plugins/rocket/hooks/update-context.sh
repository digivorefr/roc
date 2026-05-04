#!/usr/bin/env bash
# Stop-hook wrapper for rocket:context-update.
# Spawns a `claude -p --model "sonnet[1m]"` subprocess that updates
# .claude/lexicon.md from the current session transcript. Runs async, never
# blocks the user.

set -u

# Recursion guard: the `claude -p` subprocess we spawn below also fires Stop
# hooks and would re-invoke this script. The exported sentinel propagates to
# the subprocess; subsequent invocations exit immediately.
[ -n "${ROCKET_CONTEXT_UPDATE_INVOKED:-}" ] && exit 0
export ROCKET_CONTEXT_UPDATE_INVOKED=1

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CLAUDE_DIR="${PROJECT_DIR}/.claude"
LEXICON="${CLAUDE_DIR}/lexicon.md"
LOCK_DIR="${CLAUDE_DIR}/lexicon.md.lock.d"
LOG="${CLAUDE_DIR}/lexicon-update.log"
DEBOUNCE_SECONDS=30
STALE_LOCK_SECONDS=600
LOG_MAX_BYTES=$((1024 * 1024))
LOG_KEEP=3
# Transcripts can grow to tens of MB (full session JSONL). We invoke Sonnet
# with the 1M-context tier (`sonnet[1m]`, ~3.7 MB). Cap the slice fed on
# stdin to ~800 KB so the prompt stays small enough to keep latency and cost
# reasonable while almost never tripping the limit. The skill extracts
# incremental concepts from the most recent activity.
TRANSCRIPT_BYTE_CAP=$((800 * 1024))

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

# Extract transcript_path from the JSON payload without requiring jq. The sed
# regex assumes the value contains no escaped quotes (transcript paths in
# practice never do). If a python3 interpreter is available, prefer it as a
# robust fallback; otherwise stick with sed.
TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
if [ -z "${TRANSCRIPT_PATH}" ] && command -v python3 >/dev/null 2>&1; then
  TRANSCRIPT_PATH="$(printf '%s' "${PAYLOAD}" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("transcript_path",""))
except Exception:
    pass' 2>/dev/null)"
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

The transcript of the current Claude Code session is provided on stdin (JSONL, one event per line). Run the context-update workflow against it and the project lexicon.'

# Pipe the (possibly truncated) transcript on stdin to the subprocess. cd into
# the project so the skill resolves .claude/lexicon.md relative to the right
# root. If the transcript exceeds TRANSCRIPT_BYTE_CAP, take the trailing slice
# and drop the first (likely partial) JSONL line so the subprocess only sees
# whole events.
transcript_size=$(wc -c <"${TRANSCRIPT_PATH}" 2>/dev/null | tr -d ' ')
(
  cd "${PROJECT_DIR}" || exit 1
  if [ -n "${transcript_size}" ] && [ "${transcript_size}" -gt "${TRANSCRIPT_BYTE_CAP}" ]; then
    log "tailing transcript: ${transcript_size} bytes -> last ${TRANSCRIPT_BYTE_CAP} bytes"
    tail -c "${TRANSCRIPT_BYTE_CAP}" "${TRANSCRIPT_PATH}" | tail -n +2 | claude -p --model "sonnet[1m]" "${PROMPT}" 2>>"${LOG}"
  else
    cat "${TRANSCRIPT_PATH}" | claude -p --model "sonnet[1m]" "${PROMPT}" 2>>"${LOG}"
  fi
) >>"${LOG}"
status=$?

end=$(date +%s)
log "end: status=${status} duration=$((end - start))s"

# Always exit 0: this is an async hook. Returning the subprocess status would
# risk propagating exit code 2 (the Stop-hook block signal) to the user's main
# session, forcing Claude to keep responding when the subprocess hits an error.
exit 0
