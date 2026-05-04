#!/usr/bin/env bash
# SessionStart hook for my-hand inbox watcher.
# Emits an additionalContext directive that auto-resumes the polling loop —
# but only when the current Claude Code session is opened inside the project
# recorded as the mail-session by `/my-hand:inbox-watch start`. In every
# other project, this hook is silent.
#
# Always exits 0. Never blocks session start. Mirrors the defensive style of
# plugins/rocket/hooks/update-context.sh.

set -u

STATE_DIR="${HOME}/.roc/my-hand"
SENTINEL="${STATE_DIR}/mail-session.path"

# Drain hook payload from stdin to be polite, even though we do not need it.
PAYLOAD="$(cat || true)"
: "${PAYLOAD}"  # silence unused-var warnings

# No sentinel = no mail-session configured. Silent exit.
[ -r "${SENTINEL}" ] || exit 0

# Read the first line of the sentinel and trim trailing whitespace/newline.
RAW_SESSION_PATH="$(head -n1 "${SENTINEL}" 2>/dev/null | tr -d '\r' | sed -e 's/[[:space:]]*$//')"
[ -n "${RAW_SESSION_PATH}" ] || exit 0

resolve_path() {
  # Prefer realpath if available (macOS-native command).
  if command -v realpath >/dev/null 2>&1; then
    realpath "$1" 2>/dev/null && return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null && return 0
  fi
  # Fallback: print as-is.
  printf '%s' "$1"
}

SESSION_PATH="$(resolve_path "${RAW_SESSION_PATH}")"
CURRENT_PATH="$(resolve_path "${PWD}")"

# Compare byte-exact after resolution. If different, this is not the
# mail-session project — exit silently.
[ "${SESSION_PATH}" = "${CURRENT_PATH}" ] || exit 0

# Match: emit the SessionStart directive that nudges the model to resume the
# polling loop. The directive is a single JSON object on stdout.
cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "my-hand mail session: this conversation is configured as the mail-session project. Resume polling now by invoking the `loop` skill with `10m /my-hand:inbox-watch tick`. Do not announce it; just start it. If a loop for this command is already running for this session, skip."
  }
}
JSON

exit 0
