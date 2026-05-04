#!/usr/bin/env python3
# Strip token-heavy fields from a Claude Code transcript JSONL stream.
#
# The transcript piped on stdin contains events whose `signature`, `thinking`,
# and `originalFile` fields plus base64 image payloads dominate the token
# count. This script removes them so the resulting slice stays within the
# subprocess's context budget. Per-line cap of 8 KB protects against any
# remaining outliers.
#
# Reads JSONL on stdin, writes JSONL on stdout. Non-JSON lines are passed
# through (or stubbed if oversized).

import json
import sys

LINE_CAP = 8192


def strip(node):
    if isinstance(node, dict):
        # Drop fields that are token-expensive but carry no semantic signal.
        node.pop("signature", None)
        node.pop("originalFile", None)
        # Keep thinking blocks structurally but drop their content.
        if "thinking" in node:
            node["thinking"] = "[stripped]"
        # Replace image base64 payloads with a size marker.
        if (
            node.get("type") == "image"
            and isinstance(node.get("source"), dict)
            and node["source"].get("type") == "base64"
        ):
            data = node["source"].get("data", "")
            media = node["source"].get("media_type", "image")
            node["source"]["data"] = (
                f"[{media} base64 stripped, {len(data)} bytes]"
            )
        for value in list(node.values()):
            strip(value)
    elif isinstance(node, list):
        for item in node:
            strip(item)


def main() -> int:
    for raw in sys.stdin:
        line = raw.rstrip("\n")
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            # Unparseable line: pass through if small, stub if huge.
            if len(line) > LINE_CAP:
                sys.stdout.write(
                    json.dumps(
                        {"_truncated_unparseable": True, "_size": len(line)}
                    )
                    + "\n"
                )
            else:
                sys.stdout.write(line + "\n")
            continue
        strip(obj)
        out = json.dumps(obj, ensure_ascii=False)
        if len(out) > LINE_CAP:
            sys.stdout.write(
                json.dumps(
                    {
                        "_truncated_post_strip": True,
                        "_size": len(out),
                        "_type": obj.get("type", "?"),
                    }
                )
                + "\n"
            )
        else:
            sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
