#!/usr/bin/env python3
"""rocket context-gate -- heuristic and prompt helpers for the context-update pipeline.

Subcommands: extract-delta, should-fire, format-gate-prompt, parse-gate-response,
             format-writer-prompt, update-cursor, read-cursor.

All subcommands exit 0. Errors are reported on stderr; stdout carries only the
contract-defined output for the calling wrapper. Built into a single PyInstaller
binary at ``plugins/rocket/bin/context-gate``. No native C deps.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Tunable constants
# ---------------------------------------------------------------------------

CONTENT_LINES_THRESHOLD = 5
LINE_CAP_BYTES = 2048
DELTA_TEXT_CAP_BYTES = 16384
TRANSCRIPT_TAIL_FALLBACK = 500
CLAUDE_MD_CAP_BYTES = 4096


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_fields(node: object) -> None:
    """Recursively strip token-heavy fields (signature, originalFile, thinking, base64)."""
    if isinstance(node, dict):
        node.pop("signature", None)
        node.pop("originalFile", None)
        if "thinking" in node:
            node["thinking"] = "[stripped]"
        if (
            node.get("type") == "image"
            and isinstance(node.get("source"), dict)
            and node["source"].get("type") == "base64"
        ):
            data = node["source"].get("data", "")
            media = node["source"].get("media_type", "image")
            node["source"]["data"] = f"[{media} base64 stripped, {len(data)} bytes]"
        for value in list(node.values()):
            _strip_fields(value)
    elif isinstance(node, list):
        for item in node:
            _strip_fields(item)


def _classify_event(obj: dict) -> str:
    """Classify a transcript JSONL event into a category.

    Returns one of: user, assistant_prose, tool_call, tool_result,
    thinking, system, unknown.
    """
    event_type = obj.get("type", "")

    # User message
    if event_type == "human" or obj.get("role") == "user":
        return "user"

    # Thinking blocks
    if event_type == "thinking":
        return "thinking"

    # Tool use / tool calls
    if event_type in ("tool_use", "tool_call"):
        return "tool_call"

    # Tool results
    if event_type in ("tool_result", "tool_output"):
        return "tool_result"

    # System messages
    if event_type == "system" or obj.get("role") == "system":
        return "system"

    # Assistant messages -- distinguish prose from tool calls
    if event_type == "assistant" or obj.get("role") == "assistant":
        content = obj.get("content", "")
        # Content can be a list of blocks or a string
        if isinstance(content, list):
            has_text = False
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        has_text = True
                    elif block.get("type") in ("tool_use", "tool_call"):
                        pass  # tool blocks in assistant message
            return "assistant_prose" if has_text else "tool_call"
        if isinstance(content, str) and content.strip():
            return "assistant_prose"
        return "tool_call"

    # Content blocks at top level (from streaming)
    if event_type == "text" and obj.get("text", "").strip():
        return "assistant_prose"

    return "unknown"


def _extract_text(obj: dict, category: str) -> str:
    """Extract human-readable text from a classified event."""
    if category not in ("user", "assistant_prose"):
        return ""

    content = obj.get("content", "")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)

    # Top-level text field (streaming events)
    text = obj.get("text", "")
    if isinstance(text, str):
        return text

    return ""


# ---------------------------------------------------------------------------
# extract-delta
# ---------------------------------------------------------------------------

def cmd_extract_delta(args: list[str]) -> None:
    """Read transcript JSONL from since-line to EOF, emit delta JSON."""
    transcript_path: str | None = None
    since_line: int = 0

    i = 0
    while i < len(args):
        if args[i] == "--transcript" and i + 1 < len(args):
            transcript_path = args[i + 1]
            i += 2
        elif args[i] == "--since-line" and i + 1 < len(args):
            try:
                since_line = int(args[i + 1])
            except ValueError:
                since_line = 0
            i += 2
        else:
            i += 1

    if transcript_path is None:
        print(json.dumps({
            "delta_lines": 0, "content_lines": 0,
            "has_user_message": False, "has_assistant_prose": False,
            "tool_only": True, "delta_text": "",
        }))
        return

    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"extract-delta: cannot read transcript: {exc}", file=sys.stderr)
        print(json.dumps({
            "delta_lines": 0, "content_lines": 0,
            "has_user_message": False, "has_assistant_prose": False,
            "tool_only": True, "delta_text": "",
        }))
        return

    total_lines = len(lines)

    # If cursor is past EOF, fall back to last N lines
    if since_line >= total_lines:
        since_line = max(0, total_lines - TRANSCRIPT_TAIL_FALLBACK)

    delta_lines_raw = lines[since_line:]
    delta_line_count = len(delta_lines_raw)

    content_line_count = 0
    has_user_message = False
    has_assistant_prose = False
    text_parts: list[str] = []
    text_total_bytes = 0

    for raw_line in delta_lines_raw:
        if not raw_line.strip():
            continue
        try:
            obj = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        _strip_fields(obj)
        category = _classify_event(obj)

        if category == "user":
            has_user_message = True
            content_line_count += 1
        elif category == "assistant_prose":
            has_assistant_prose = True
            content_line_count += 1

        if category in ("user", "assistant_prose"):
            text = _extract_text(obj, category)
            if text:
                # Cap per line
                if len(text.encode("utf-8", errors="replace")) > LINE_CAP_BYTES:
                    text = text[:LINE_CAP_BYTES]
                text_bytes = len(text.encode("utf-8", errors="replace"))
                if text_total_bytes + text_bytes <= DELTA_TEXT_CAP_BYTES:
                    text_parts.append(text)
                    text_total_bytes += text_bytes

    tool_only = not has_user_message and not has_assistant_prose

    result = {
        "delta_lines": delta_line_count,
        "content_lines": content_line_count,
        "has_user_message": has_user_message,
        "has_assistant_prose": has_assistant_prose,
        "tool_only": tool_only,
        "delta_text": "\n".join(text_parts),
    }
    print(json.dumps(result, ensure_ascii=False))


# ---------------------------------------------------------------------------
# parse-delta-fields
# ---------------------------------------------------------------------------

def cmd_parse_delta_fields() -> None:
    """Read extract-delta JSON from stdin, print shell-friendly summary line.

    Output: ``<content_lines> <tool_only> <has_user> <has_prose>``
    One line, space-separated, ready for ``read -r`` in bash.
    """
    raw = sys.stdin.read().strip()
    try:
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
    except (json.JSONDecodeError, ValueError):
        print("0 true false false")
        return

    content_lines = obj.get("content_lines", 0)
    tool_only = "true" if obj.get("tool_only") else "false"
    has_user = "true" if obj.get("has_user_message") else "false"
    has_prose = "true" if obj.get("has_assistant_prose") else "false"
    print(f"{content_lines} {tool_only} {has_user} {has_prose}")


# ---------------------------------------------------------------------------
# extract-delta-text
# ---------------------------------------------------------------------------

def cmd_extract_delta_text() -> None:
    """Read extract-delta JSON from stdin, print the delta_text field only."""
    raw = sys.stdin.read().strip()
    try:
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
    except (json.JSONDecodeError, ValueError):
        return

    text = obj.get("delta_text", "")
    if isinstance(text, str) and text:
        print(text)


# ---------------------------------------------------------------------------
# should-fire
# ---------------------------------------------------------------------------

def cmd_should_fire(args: list[str]) -> None:
    """Apply heuristic rules, print yes or no."""
    content_lines: int = 0
    tool_only: bool = False
    has_user_message: bool = False
    has_assistant_prose: bool = False

    i = 0
    while i < len(args):
        if args[i] == "--content-lines" and i + 1 < len(args):
            try:
                content_lines = int(args[i + 1])
            except ValueError:
                content_lines = 0
            i += 2
        elif args[i] == "--tool-only" and i + 1 < len(args):
            tool_only = args[i + 1].lower() in ("true", "1", "yes")
            i += 2
        elif args[i] == "--has-user-message" and i + 1 < len(args):
            has_user_message = args[i + 1].lower() in ("true", "1", "yes")
            i += 2
        elif args[i] == "--has-assistant-prose" and i + 1 < len(args):
            has_assistant_prose = args[i + 1].lower() in ("true", "1", "yes")
            i += 2
        else:
            i += 1

    # Rule 1: short turns
    if content_lines < CONTENT_LINES_THRESHOLD:
        print("no")
        return

    # Rule 2: tool-only turns
    if tool_only:
        print("no")
        return

    # Rule 3: no user or assistant prose
    if not has_user_message and not has_assistant_prose:
        print("no")
        return

    # Rule 4: pass to Haiku gate
    print("yes")


# ---------------------------------------------------------------------------
# format-gate-prompt
# ---------------------------------------------------------------------------

def cmd_format_gate_prompt(args: list[str]) -> None:
    """Read delta_text from stdin, format Haiku gate prompt."""
    lexicon_path: str | None = None

    i = 0
    while i < len(args):
        if args[i] == "--lexicon" and i + 1 < len(args):
            lexicon_path = args[i + 1]
            i += 2
        else:
            i += 1

    delta_text = sys.stdin.read()

    # Extract concept names from lexicon
    concept_names: list[str] = []
    if lexicon_path:
        try:
            lexicon_content = Path(lexicon_path).read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"^###\s+(.+)$", lexicon_content, re.MULTILINE):
                name = match.group(1).strip()
                if name:
                    concept_names.append(name)
        except OSError:
            pass

    concepts_str = ", ".join(concept_names) if concept_names else "(none)"

    prompt = f"""Does this conversation excerpt introduce new domain concepts, architectural
decisions, or project-specific vocabulary not already captured in the lexicon?

Existing concepts: {concepts_str}

Conversation excerpt:
{delta_text}

Respond with ONLY this JSON, no other text:
{{"update": true, "candidates": ["concept1", "concept2"]}}
or
{{"update": false, "candidates": []}}"""

    print(prompt)


# ---------------------------------------------------------------------------
# parse-gate-response
# ---------------------------------------------------------------------------

def cmd_parse_gate_response() -> None:
    """Parse Haiku gate response from stdin. Print 'no' or the JSON object."""
    raw = sys.stdin.read().strip()

    # Search for a JSON object in the response
    match = re.search(r"\{[^{}]*\}", raw)
    if not match:
        print("no")
        return

    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError:
        print("no")
        return

    if not isinstance(obj, dict):
        print("no")
        return

    update = obj.get("update", False)
    if not update:
        print("no")
        return

    candidates = obj.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        print("no")
        return

    # Return the JSON verbatim
    print(json.dumps(obj, ensure_ascii=False))


# ---------------------------------------------------------------------------
# format-writer-prompt
# ---------------------------------------------------------------------------

def cmd_format_writer_prompt(args: list[str]) -> None:
    """Read candidates JSON from stdin, format scoped Sonnet prompt."""
    lexicon_path: str | None = None
    claude_md_path: str | None = None

    i = 0
    while i < len(args):
        if args[i] == "--lexicon" and i + 1 < len(args):
            lexicon_path = args[i + 1]
            i += 2
        elif args[i] == "--claude-md" and i + 1 < len(args):
            claude_md_path = args[i + 1]
            i += 2
        else:
            i += 1

    raw = sys.stdin.read().strip()

    # Parse candidates from stdin JSON
    candidates: list[str] = []
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            candidates = obj.get("candidates", [])
        elif isinstance(obj, list):
            candidates = obj
    except json.JSONDecodeError:
        pass

    candidates_str = ", ".join(str(c) for c in candidates) if candidates else "(none)"

    # Read lexicon
    lexicon_content = ""
    if lexicon_path:
        try:
            lexicon_content = Path(lexicon_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            lexicon_content = "(lexicon file not found)"

    if not lexicon_content.strip():
        lexicon_content = "(empty)"

    # Read CLAUDE.md, capped at 4 KB
    claude_md_content = ""
    if claude_md_path:
        try:
            raw_md = Path(claude_md_path).read_text(encoding="utf-8", errors="replace")
            if len(raw_md.encode("utf-8", errors="replace")) > CLAUDE_MD_CAP_BYTES:
                claude_md_content = raw_md[:CLAUDE_MD_CAP_BYTES]
            else:
                claude_md_content = raw_md
        except OSError:
            claude_md_content = "(CLAUDE.md not found)"

    if not claude_md_content.strip():
        claude_md_content = "(empty)"

    prompt = f"""/rocket:context-update

Integrate these candidate concepts into the project lexicon at
`.roc/rocket/lexicon.md`. The candidates were identified by a pre-classifier
from the latest conversation turn.

Candidates: {candidates_str}

Existing lexicon:
{lexicon_content}

Project conventions (from CLAUDE.md):
{claude_md_content}

Run the context-update workflow (Steps 2-7) for these candidates only.
Do not re-analyze the full conversation -- the candidates are pre-validated."""

    print(prompt)


# ---------------------------------------------------------------------------
# update-cursor
# ---------------------------------------------------------------------------

def cmd_update_cursor(args: list[str]) -> None:
    """Write cursor state atomically."""
    state_path: str | None = None
    line: int = 0

    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_path = args[i + 1]
            i += 2
        elif args[i] == "--line" and i + 1 < len(args):
            try:
                line = int(args[i + 1])
            except ValueError:
                line = 0
            i += 2
        else:
            i += 1

    if state_path is None:
        print("error: --state is required", file=sys.stderr)
        return

    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    state = {"last_processed_line": line}

    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=".context-gate-state-", suffix=".tmp"
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


# ---------------------------------------------------------------------------
# read-cursor
# ---------------------------------------------------------------------------

def cmd_read_cursor(args: list[str]) -> None:
    """Read cursor state, print last_processed_line or 0."""
    state_path: str | None = None

    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_path = args[i + 1]
            i += 2
        else:
            i += 1

    if state_path is None:
        print("0")
        return

    try:
        raw = Path(state_path).read_text(encoding="utf-8")
        obj = json.loads(raw)
        if isinstance(obj, dict):
            val = obj.get("last_processed_line", 0)
            if isinstance(val, int) and val >= 0:
                print(val)
                return
    except (OSError, json.JSONDecodeError, ValueError):
        pass

    print("0")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: context-gate <extract-delta|parse-delta-fields|extract-delta-text|"
            "should-fire|format-gate-prompt|parse-gate-response|format-writer-prompt|"
            "update-cursor|read-cursor> [options]",
            file=sys.stderr,
        )
        return 0

    subcmd = sys.argv[1]
    rest = sys.argv[2:]

    if subcmd == "extract-delta":
        cmd_extract_delta(rest)
    elif subcmd == "parse-delta-fields":
        cmd_parse_delta_fields()
    elif subcmd == "extract-delta-text":
        cmd_extract_delta_text()
    elif subcmd == "should-fire":
        cmd_should_fire(rest)
    elif subcmd == "format-gate-prompt":
        cmd_format_gate_prompt(rest)
    elif subcmd == "parse-gate-response":
        cmd_parse_gate_response()
    elif subcmd == "format-writer-prompt":
        cmd_format_writer_prompt(rest)
    elif subcmd == "update-cursor":
        cmd_update_cursor(rest)
    elif subcmd == "read-cursor":
        cmd_read_cursor(rest)
    else:
        print(f"unknown subcommand: {subcmd}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
