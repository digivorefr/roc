#!/usr/bin/env python3
"""my-hand inbox-poll — non-LLM inbox polling helpers.

Subcommands: lock, unlock, last-poll, check, render, update, notify.

All subcommands exit 0. Errors are reported on stderr; stdout carries
only the contract-defined output for the calling skill. Built into a
single PyInstaller binary at
``plugins/my-hand/bin/darwin-arm64/inbox-poll``. No native C deps.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".roc" / "my-hand"
LOCK_DIR = STATE_DIR / "mail-poll.lock.d"
LOCK_STALE_SECONDS = 600
SEEN_IDS_CAP = 200
PENDING_REPLIES_CAP = 200


# ---------- lock ----------

def cmd_lock() -> None:
    """Acquire the mkdir-based atomic lock."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        LOCK_DIR.mkdir()
        print("ok")
        return
    except FileExistsError:
        pass

    # Lock exists: check staleness.
    try:
        mtime = LOCK_DIR.stat().st_mtime
    except OSError:
        # Lock vanished between the mkdir attempt and stat; retry once.
        try:
            LOCK_DIR.mkdir()
            print("ok")
            return
        except FileExistsError:
            print("held")
            return

    age = time.time() - mtime
    if age >= LOCK_STALE_SECONDS:
        # Reap stale lock and retry once.
        try:
            LOCK_DIR.rmdir()
        except OSError:
            print("held")
            return
        try:
            LOCK_DIR.mkdir()
            print("ok")
            return
        except FileExistsError:
            pass

    print("held")


# ---------- unlock ----------

def cmd_unlock() -> None:
    """Release the lock. Silent if lock does not exist."""
    try:
        LOCK_DIR.rmdir()
    except OSError:
        pass


# ---------- last-poll ----------

def cmd_last_poll(args: list[str]) -> None:
    """Print last_poll_at from state, or 'null' if unset."""
    state_path: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_path = args[i + 1]
            i += 2
        else:
            i += 1

    if state_path is None:
        print("error: --state is required", file=sys.stderr)
        print("null")
        return

    state = _read_state(Path(state_path))
    last_poll = state.get("last_poll_at")
    if last_poll and isinstance(last_poll, str):
        print(last_poll)
    else:
        print("null")


# ---------- check ----------

def cmd_check(args: list[str]) -> None:
    """Compare thread IDs against persisted state."""
    state_path: str | None = None
    ids_json: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_path = args[i + 1]
            i += 2
        elif args[i] == "--ids" and i + 1 < len(args):
            ids_json = args[i + 1]
            i += 2
        else:
            i += 1

    if state_path is None or ids_json is None:
        print("error: --state and --ids are required", file=sys.stderr)
        print("empty")
        return

    state_file = Path(state_path)
    state = _read_state(state_file)

    try:
        ids = json.loads(ids_json)
        if not isinstance(ids, list):
            ids = []
    except (json.JSONDecodeError, TypeError):
        ids = []

    last_seen = set(state.get("last_seen_thread_ids", []))
    new_ids = [tid for tid in ids if tid not in last_seen]

    if not new_ids:
        # No new threads: update last_poll_at and persist.
        state["last_poll_at"] = _now_iso()
        _write_state(state_file, state)
        print("empty")
    else:
        result = {"new_ids": new_ids, "count": len(new_ids)}
        print(json.dumps(result))


# ---------- render ----------

def cmd_render() -> None:
    """Read analysis JSON from stdin, render markdown table to stdout."""
    raw = sys.stdin.read()
    try:
        items = json.loads(raw)
        if not isinstance(items, list):
            raise ValueError("expected a JSON array")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"render: malformed input: {exc}", file=sys.stderr)
        return

    lines: list[str] = []
    lines.append("| Reply? | From (company) | Subject | Suggested reply |")
    lines.append("| --- | --- | --- | --- |")

    for item in items:
        if not isinstance(item, dict):
            continue
        reply = "✅" if item.get("reply") else "—"
        sender = _escape_cell(str(item.get("sender", "")))
        company = item.get("company")
        if company:
            from_col = f"{sender} ({_escape_cell(str(company))})"
        else:
            from_col = sender
        subject = _escape_cell(_truncate(str(item.get("subject", "")), 60))
        suggestion = item.get("suggestion")
        suggestion_col = _escape_cell(str(suggestion)) if suggestion else ""
        lines.append(f"| {reply} | {from_col} | {subject} | {suggestion_col} |")

    lines.append("")
    lines.append("Run /my-hand:inbox-reply <sender or subject> to draft a reply in the thread.")

    print("\n".join(lines))


# ---------- update ----------

def cmd_update(args: list[str]) -> None:
    """Read a state patch from stdin, merge into inbox-state.json."""
    state_path: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_path = args[i + 1]
            i += 2
        else:
            i += 1

    if state_path is None:
        print("error: --state is required", file=sys.stderr)
        return

    raw = sys.stdin.read()
    try:
        patch = json.loads(raw)
        if not isinstance(patch, dict):
            raise ValueError("expected a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"update: malformed input: {exc}", file=sys.stderr)
        return

    state_file = Path(state_path)
    state = _read_state(state_file)

    # Prepend new seen IDs.
    add_ids = patch.get("add_seen_ids", [])
    if isinstance(add_ids, list):
        existing = state.get("last_seen_thread_ids", [])
        merged = list(add_ids) + [tid for tid in existing if tid not in set(add_ids)]
        state["last_seen_thread_ids"] = merged[:SEEN_IDS_CAP]

    # Merge pending replies.
    new_pending = patch.get("pending_replies", {})
    if isinstance(new_pending, dict):
        existing_pending = state.get("pending_replies", {})
        if not isinstance(existing_pending, dict):
            existing_pending = {}
        existing_pending.update(new_pending)
        # Cap at 200 entries, drop oldest (first keys).
        if len(existing_pending) > PENDING_REPLIES_CAP:
            keys = list(existing_pending.keys())
            for key in keys[: len(keys) - PENDING_REPLIES_CAP]:
                del existing_pending[key]
        state["pending_replies"] = existing_pending

    state["last_poll_at"] = _now_iso()
    _write_state(state_file, state)


# ---------- notify ----------

def cmd_notify(args: list[str]) -> None:
    """Fire a macOS notification via osascript."""
    count: int = 0
    senders: str = ""
    i = 0
    while i < len(args):
        if args[i] == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
            except ValueError:
                count = 0
            i += 2
        elif args[i] == "--senders" and i + 1 < len(args):
            senders = args[i + 1]
            i += 2
        else:
            i += 1

    title = f"Claude — {count} nouveau(x) mail(s)"
    body = f"From: {senders}" if senders else ""

    # Escape double quotes for AppleScript.
    title_escaped = title.replace('"', '\\"')
    body_escaped = body.replace('"', '\\"')

    script = (
        f'display notification "{body_escaped}" '
        f'with title "{title_escaped}" sound name "default"'
    )

    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        # Silent failure per spec.
        pass


# ---------- Helpers ----------

def _read_state(path: Path) -> dict:
    """Read and parse the state file. Returns fresh state on any failure."""
    fresh = {"last_seen_thread_ids": [], "last_poll_at": None, "pending_replies": {}}
    try:
        raw = path.read_text(encoding="utf-8")
        state = json.loads(raw)
        if not isinstance(state, dict):
            return fresh
        return state
    except (OSError, json.JSONDecodeError):
        return fresh


def _write_state(path: Path, state: dict) -> None:
    """Write state atomically via tmp + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=".inbox-state-", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, str(path))
    except OSError:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _now_iso() -> str:
    """Current UTC time as ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _escape_cell(text: str) -> str:
    """Escape pipe and newline characters for markdown table cells."""
    return text.replace("|", "\\|").replace("\n", "; ").replace("\r", "")


def _truncate(text: str, limit: int) -> str:
    """Truncate text to limit characters, appending ellipsis if needed."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


# ---------- Main ----------

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: inbox-poll <lock|unlock|last-poll|check|render|update|notify> [options]", file=sys.stderr)
        return 0

    subcmd = sys.argv[1]
    rest = sys.argv[2:]

    if subcmd == "lock":
        cmd_lock()
    elif subcmd == "unlock":
        cmd_unlock()
    elif subcmd == "last-poll":
        cmd_last_poll(rest)
    elif subcmd == "check":
        cmd_check(rest)
    elif subcmd == "render":
        cmd_render()
    elif subcmd == "update":
        cmd_update(rest)
    elif subcmd == "notify":
        cmd_notify(rest)
    else:
        print(f"unknown subcommand: {subcmd}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
