#!/usr/bin/env python3
"""my-hand — reMarkable 2 page capture (V2, full-resolution rendering).

Reads the device tree from a reMarkable 2 tablet's USB web interface,
resolves a notebook by name, downloads its rmdoc archive, picks the visible
page targeted by ``CurrentPage`` (filtering deleted pages), renders it
through ``rmc`` (.rm -> SVG) and ``cairosvg`` (SVG -> PNG at 1404x1872),
writes the PNG under ``/tmp``, and prints a prompt body on stdout
instructing the model to read the file. Always exits 0; errors are
reported as English prose for the model to relay to the user.

This source is built into a single PyInstaller binary at
``plugins/my-hand/bin/darwin-arm64/my-hand-grab``. It is not the
runtime entry point on a user machine.
"""

from __future__ import annotations

import glob
import io
import json
import logging
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

DEVICE_BASE = "http://10.11.99.1"
LIST_TIMEOUT_S = 5
RMDOC_TIMEOUT_S = 60
TMP_DIR = "/tmp"
FILE_PREFIX = "my-hand-remarkable-grab-"
FILE_TTL_S = 24 * 3600
USER_AGENT = "my-hand/0.2"
RENDER_WIDTH = 1404
RENDER_HEIGHT = 1872


# ---------- Library noise suppression ----------

def _silence_third_party_logs() -> None:
    """Suppress ``rmscene``'s benign tagged-block-reader warning so it does
    not leak into the prompt body. Other third-party logs are also routed
    away from stdout/stderr to keep stdout clean (stdout is the model
    contract). Call once before any ``rmc`` import or invocation."""
    for name in (
        "rmscene",
        "rmscene.tagged_block_reader",
        "rmscene.scene_stream",
        "rmc",
    ):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.propagate = False


# ---------- HTTP helpers ----------

def _http_get(path: str, timeout_s: int) -> tuple[int, bytes]:
    """Perform a GET and return (status, body). Raises on transport errors."""
    url = DEVICE_BASE + path
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        body = response.read()
        return response.status, body


# ---------- Device tree ----------

def _list_folder(uuid: str) -> list[dict]:
    """Fetch a folder listing from the device. Empty uuid means root."""
    path = "/documents/" if not uuid else f"/documents/{uuid}"
    status, body = _http_get(path, LIST_TIMEOUT_S)
    if status != 200:
        raise RuntimeError(f"GET {path} returned HTTP {status}")
    return json.loads(body.decode("utf-8"))


def _visible_name(entry: dict) -> str:
    name = entry.get("VisibleName")
    if not name:
        name = entry.get("VissibleName")
    return (name or "").strip()


def fetch_tree() -> list[dict]:
    """Walk the device tree and return a flat list of notebook descriptors.

    Each descriptor is a dict with keys: uuid, name, breadcrumb, modified,
    current_page. Only ``DocumentType`` entries with ``fileType == "notebook"``
    are kept.
    """
    notebooks: list[dict] = []
    # Stack items: (folder_uuid, breadcrumb_segments)
    stack: list[tuple[str, list[str]]] = [("", [])]
    visited: set[str] = set()
    while stack:
        folder_uuid, crumbs = stack.pop()
        key = folder_uuid or ""
        if key in visited:
            continue
        visited.add(key)
        try:
            entries = _list_folder(folder_uuid)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError, RuntimeError) as exc:
            # Re-raise root failures so callers can show the right error;
            # swallow sub-folder failures so a single bad folder doesn't kill the walk.
            if folder_uuid == "":
                raise
            print(f"[my-hand] subfolder {folder_uuid} listing failed: {exc}", file=sys.stderr)
            continue
        if not isinstance(entries, list):
            if folder_uuid == "":
                raise RuntimeError("root listing was not a JSON array")
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_type = entry.get("Type")
            name = _visible_name(entry)
            uuid = entry.get("ID") or ""
            if entry_type == "CollectionType" and uuid:
                stack.append((uuid, crumbs + [name]))
            elif entry_type == "DocumentType" and entry.get("fileType") == "notebook" and uuid:
                breadcrumb = " / ".join(crumbs + [name]) if crumbs else name
                current_page_raw = entry.get("CurrentPage", 0)
                try:
                    current_page = int(current_page_raw)
                except (TypeError, ValueError):
                    current_page = 0
                notebooks.append({
                    "uuid": uuid,
                    "name": name,
                    "breadcrumb": breadcrumb,
                    "modified": entry.get("ModifiedClient", ""),
                    "current_page": current_page,
                })
    notebooks.sort(key=lambda n: n["breadcrumb"].lower())
    return notebooks


# ---------- Resolution ----------

def resolve(name: str, notebooks: list[dict]) -> list[dict]:
    """Return all notebooks whose name matches `name` (case-insensitive, trimmed)."""
    needle = name.strip().lower()
    if not needle:
        return []
    return [n for n in notebooks if n["name"].strip().lower() == needle]


# ---------- Rmdoc fetch and parse ----------

def fetch_rmdoc(uuid: str) -> tuple[Optional[bytes], Optional[str]]:
    """Fetch /download/<uuid>/rmdoc. Returns (body, error_message)."""
    try:
        status, body = _http_get(f"/download/{uuid}/rmdoc", RMDOC_TIMEOUT_S)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        print(f"[my-hand] rmdoc-fetch failed: {exc}", file=sys.stderr)
        return None, f"transport error: {exc}"
    if status != 200:
        print(f"[my-hand] rmdoc-fetch HTTP {status}", file=sys.stderr)
        return None, f"HTTP {status}"
    if not body:
        return None, "empty body"
    return body, None


def parse_content(zip_bytes: bytes, doc_uuid: str) -> tuple[Optional[dict], Optional[str]]:
    """Open the rmdoc ZIP, read ``<doc_uuid>.content`` and return its JSON.

    Returns (content_json, error_message). On any failure, content_json is
    None and error_message describes the issue in English.
    """
    try:
        archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        return None, f"bad zip: {exc}"
    content_name = f"{doc_uuid}.content"
    namelist = archive.namelist()
    if content_name not in namelist:
        # Some firmwares may nest entries under a top-level dir; try to find it.
        candidates = [n for n in namelist if n.endswith(f"/{content_name}") or n == content_name]
        if not candidates:
            return None, f"missing entry {content_name} in archive"
        content_name = candidates[0]
    try:
        with archive.open(content_name) as handle:
            content_json = json.loads(handle.read().decode("utf-8"))
    except (KeyError, json.JSONDecodeError, OSError) as exc:
        return None, f"cannot read {content_name}: {exc}"
    return content_json, None


def select_visible_page(content_json: dict, current_page: int) -> tuple[Optional[str], Optional[str]]:
    """Apply the visible-page filter to ``cPages.pages`` and return the
    target page UUID at index ``current_page``.

    Returns (page_uuid, error_kind). ``error_kind`` is one of:
    - ``"content-empty"``: cPages.pages is missing or empty.
    - ``"current-page-out-of-range"``: index past visible pages.
    """
    cpages = content_json.get("cPages") if isinstance(content_json, dict) else None
    if not isinstance(cpages, dict):
        return None, "content-empty"
    pages = cpages.get("pages")
    if not isinstance(pages, list) or len(pages) == 0:
        return None, "content-empty"
    visible_pages = [p for p in pages if isinstance(p, dict) and "deleted" not in p]
    if len(visible_pages) == 0:
        return None, "content-empty"
    index = current_page if current_page >= 0 else 0
    if index >= len(visible_pages):
        return None, "current-page-out-of-range"
    target = visible_pages[index]
    page_uuid = target.get("id") if isinstance(target, dict) else None
    if not isinstance(page_uuid, str) or not page_uuid:
        return None, "content-empty"
    return page_uuid, None


def extract_rm(zip_bytes: bytes, doc_uuid: str, page_uuid: str, dest_dir: Path) -> tuple[Optional[Path], Optional[str]]:
    """Extract the target ``<doc_uuid>/<page_uuid>.rm`` to ``dest_dir``.

    Returns (path, error_message).
    """
    try:
        archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        return None, f"bad zip: {exc}"
    expected = f"{doc_uuid}/{page_uuid}.rm"
    namelist = archive.namelist()
    chosen: Optional[str] = None
    if expected in namelist:
        chosen = expected
    else:
        # Fallback: tolerate nested layouts.
        candidates = [n for n in namelist if n.endswith(f"/{page_uuid}.rm")]
        if candidates:
            chosen = candidates[0]
    if chosen is None:
        return None, f"missing entry {expected} in archive"
    out_path = dest_dir / f"{page_uuid}.rm"
    try:
        with archive.open(chosen) as src, open(out_path, "wb") as dst:
            dst.write(src.read())
    except (KeyError, OSError) as exc:
        return None, f"cannot extract {chosen}: {exc}"
    return out_path, None


# ---------- Rendering ----------

def render_rm_to_png(rm_path: Path, out_path: Path) -> Optional[str]:
    """Render a single ``.rm`` page to a 1404x1872 PNG at ``out_path``.

    Returns None on success, an error message string otherwise.
    """
    _silence_third_party_logs()
    try:
        from rmc import rm_to_svg  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001 - third-party import surface
        return f"rmc import failed: {exc}"
    try:
        import cairosvg  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001 - third-party import surface
        return f"cairosvg import failed: {exc}"

    with tempfile.TemporaryDirectory(prefix="my-hand-render-") as tmpdir:
        svg_path = Path(tmpdir) / "page.svg"
        try:
            rm_to_svg(str(rm_path), str(svg_path))
        except Exception as exc:  # noqa: BLE001 - rmc raises a wide range
            return f"rmc render failed: {exc}"
        if not svg_path.exists() or svg_path.stat().st_size == 0:
            return "rmc produced an empty SVG"
        try:
            svg_bytes = svg_path.read_bytes()
            cairosvg.svg2png(
                bytestring=svg_bytes,
                output_width=RENDER_WIDTH,
                output_height=RENDER_HEIGHT,
                write_to=str(out_path),
            )
        except Exception as exc:  # noqa: BLE001 - cairosvg raises broadly
            return f"cairosvg render failed: {exc}"
    if not out_path.exists() or out_path.stat().st_size == 0:
        return "rendered PNG is empty"
    return None


# ---------- File handling ----------

def cleanup_tmp() -> None:
    """Delete previous capture files older than FILE_TTL_S. Best-effort."""
    pattern = os.path.join(TMP_DIR, f"{FILE_PREFIX}*.png")
    cutoff = time.time() - FILE_TTL_S
    for path in glob.glob(pattern):
        try:
            if os.path.getmtime(path) < cutoff:
                os.unlink(path)
        except OSError as exc:
            print(f"[my-hand] cleanup failed for {path}: {exc}", file=sys.stderr)


def reserve_capture_path() -> str:
    """Pick a unique /tmp path for the capture PNG."""
    base = f"{FILE_PREFIX}{int(time.time())}.png"
    path = os.path.join(TMP_DIR, base)
    suffix = 0
    while os.path.exists(path):
        suffix += 1
        path = os.path.join(TMP_DIR, f"{FILE_PREFIX}{int(time.time())}-{suffix}.png")
    return path


# ---------- Argument parsing ----------

def parse_arguments(raw: str) -> tuple[str, str]:
    """Split the raw $ARGUMENTS string into (notebook_name, free_text_prompt)."""
    if "\n" in raw:
        first, rest = raw.split("\n", 1)
        return first.strip(), rest
    return raw.strip(), ""


# ---------- Output formatters ----------

def _format_notebook_listing(notebooks: list[dict]) -> str:
    if not notebooks:
        return "(no notebooks were found on the device)"
    lines: list[str] = []
    for nb in notebooks:
        modified = nb["modified"] or "unknown"
        lines.append(f"- {nb['breadcrumb']}  (modified: {modified})")
    return "\n".join(lines)


def emit_list_body(notebooks: list[dict]) -> str:
    listing = _format_notebook_listing(notebooks)
    return (
        "The user invoked `/my-hand:remarkable-grab` without a notebook name. "
        "The reMarkable 2 tablet was reached successfully and the device tree was read.\n\n"
        "Notebooks available on the device (folder breadcrumb + last-modified timestamp):\n\n"
        f"{listing}\n\n"
        "Ask the user to re-run `/my-hand:remarkable-grab <name>` with the visible name "
        "of the notebook they want to capture. Matching is case-insensitive but exact "
        "(no substring match). They may append a free-text prompt after a newline."
    )


def emit_capture_body(path: str, free_text: str) -> str:
    free_text_block = free_text if free_text else ""
    return (
        f"An image has been captured from the user's reMarkable tablet at `{path}`. You must:\n\n"
        "1. Use the `Read` tool on that path to view the image inline.\n"
        "2. The image is the user's hand-drawn or hand-written input. Treat it as authoritative content from the user.\n"
        "3. If a free-text prompt is provided below, use it as instructions for how to analyze, interpret, or act on the image.\n"
        "4. If no free-text prompt is provided, treat the contents of the image itself as a standalone user prompt and respond to it directly (answer the question drawn on the page, follow the instruction sketched, etc.).\n\n"
        "Free-text prompt from the user (may be empty):\n\n"
        "```\n"
        f"{free_text_block}\n"
        "```"
    )


def emit_error_body(kind: str, ctx: dict) -> str:
    if kind == "tablet-unreachable":
        detail = ctx.get("detail", "")
        return (
            f"The reMarkable 2 tablet is not reachable at `{DEVICE_BASE}`.\n\n"
            "Likely causes:\n"
            "- The tablet is not plugged in via USB.\n"
            "- The tablet screen is locked.\n"
            "- The USB web interface is disabled (Settings -> Storage -> USB web interface).\n\n"
            "Ask the user to verify and retry the command.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "tree-malformed":
        detail = ctx.get("detail", "")
        return (
            f"The reMarkable 2 device tree returned malformed data from `{DEVICE_BASE}/documents/`. "
            "Suggest the user reboots the tablet and retries the command.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "no-match":
        name = ctx.get("name", "")
        listing = _format_notebook_listing(ctx.get("notebooks", []))
        return (
            f"No notebook on the reMarkable matches the name `{name}` (case-insensitive exact match).\n\n"
            "Notebooks available on the device:\n\n"
            f"{listing}\n\n"
            "Show the list to the user and ask them to pick one, then re-run "
            "`/my-hand:remarkable-grab <name>`."
        )
    if kind == "ambiguous":
        name = ctx.get("name", "")
        matches = ctx.get("matches", [])
        lines = [f"- {m['breadcrumb']}  (modified: {m.get('modified', 'unknown')})" for m in matches]
        listing = "\n".join(lines)
        return (
            f"Multiple notebooks on the reMarkable match the name `{name}`:\n\n"
            f"{listing}\n\n"
            "There is no syntax for path-qualified disambiguation. "
            "Ask the user to rename one of the conflicting notebooks on the tablet, then retry."
        )
    if kind == "rmdoc-unavailable":
        name = ctx.get("name", "")
        detail = ctx.get("detail", "")
        return (
            f"The rmdoc archive for notebook `{name}` is unavailable. The device may be busy syncing. "
            "Ask the user to wait about 5 seconds and retry the command.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "rmdoc-malformed":
        name = ctx.get("name", "")
        detail = ctx.get("detail", "")
        return (
            f"The rmdoc archive for notebook `{name}` is malformed. "
            "Ask the user to reopen the notebook on the device and retry the command.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "content-empty":
        name = ctx.get("name", "")
        return (
            f"The content metadata for notebook `{name}` is missing or empty. "
            "Ask the user to reopen the notebook on the device and retry the command."
        )
    if kind == "current-page-out-of-range":
        name = ctx.get("name", "")
        return (
            f"The reMarkable 2 reports a `CurrentPage` out of range for notebook `{name}`. "
            "This is a sync issue between the device and the USB web interface. "
            "Ask the user to reopen the notebook on the device (open it, swipe to a page, then come back) and retry the command."
        )
    if kind == "page-missing":
        name = ctx.get("name", "")
        return (
            f"The target page file is missing from the rmdoc archive for notebook `{name}`. "
            "Ask the user to reopen the notebook on the device and retry the command."
        )
    if kind == "render-rm-failure":
        name = ctx.get("name", "")
        detail = ctx.get("detail", "")
        return (
            f"Could not parse the page of notebook `{name}`. "
            "The file may be from an unsupported reMarkable firmware. "
            "Ask the user to retry the command, and if it persists, report the device firmware version.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "render-png-failure":
        name = ctx.get("name", "")
        detail = ctx.get("detail", "")
        return (
            f"Could not render the page of notebook `{name}` to PNG. "
            "The bundled rendering libraries failed; the binary may be incomplete or corrupted. "
            "Ask the user to reinstall the plugin or rebuild the binary.\n\n"
            f"Technical detail (for debugging only): {detail}"
        )
    if kind == "write-failure":
        return (
            "Capturing the page failed because the PNG could not be written to `/tmp`. "
            f"{ctx.get('detail', '')}\n\n"
            "Ask the user to verify that `/tmp` exists and is writable on their machine, then retry."
        )
    return f"Unexpected error: {kind} ({ctx})."


# ---------- Main ----------

def main() -> int:
    _silence_third_party_logs()
    cleanup_tmp()

    raw = sys.argv[1] if len(sys.argv) > 1 else ""
    notebook_name, free_text = parse_arguments(raw)

    # Fetch the device tree once. List mode and capture mode both depend on it.
    try:
        notebooks = fetch_tree()
    except (urllib.error.URLError, urllib.error.HTTPError, ConnectionRefusedError, OSError) as exc:
        sys.stdout.write(emit_error_body("tablet-unreachable", {"detail": repr(exc)}))
        sys.stdout.write("\n")
        return 0
    except (json.JSONDecodeError, RuntimeError, ValueError) as exc:
        sys.stdout.write(emit_error_body("tree-malformed", {"detail": repr(exc)}))
        sys.stdout.write("\n")
        return 0

    # List mode.
    if not notebook_name:
        sys.stdout.write(emit_list_body(notebooks))
        sys.stdout.write("\n")
        return 0

    # Capture mode.
    matches = resolve(notebook_name, notebooks)
    if len(matches) == 0:
        sys.stdout.write(emit_error_body("no-match", {"name": notebook_name, "notebooks": notebooks}))
        sys.stdout.write("\n")
        return 0
    if len(matches) > 1:
        sys.stdout.write(emit_error_body("ambiguous", {"name": notebook_name, "matches": matches}))
        sys.stdout.write("\n")
        return 0

    target = matches[0]
    rmdoc_bytes, fetch_err = fetch_rmdoc(target["uuid"])
    if rmdoc_bytes is None:
        sys.stdout.write(emit_error_body("rmdoc-unavailable", {"name": target["name"], "detail": fetch_err or ""}))
        sys.stdout.write("\n")
        return 0

    content_json, parse_err = parse_content(rmdoc_bytes, target["uuid"])
    if content_json is None:
        sys.stdout.write(emit_error_body("rmdoc-malformed", {"name": target["name"], "detail": parse_err or ""}))
        sys.stdout.write("\n")
        return 0

    page_uuid, page_err = select_visible_page(content_json, target["current_page"])
    if page_uuid is None:
        if page_err == "current-page-out-of-range":
            sys.stdout.write(emit_error_body("current-page-out-of-range", {"name": target["name"]}))
        else:
            sys.stdout.write(emit_error_body("content-empty", {"name": target["name"]}))
        sys.stdout.write("\n")
        return 0

    out_path = reserve_capture_path()
    with tempfile.TemporaryDirectory(prefix="my-hand-extract-") as tmpdir:
        rm_path, extract_err = extract_rm(rmdoc_bytes, target["uuid"], page_uuid, Path(tmpdir))
        if rm_path is None:
            sys.stdout.write(emit_error_body("page-missing", {"name": target["name"], "detail": extract_err or ""}))
            sys.stdout.write("\n")
            return 0

        render_err = render_rm_to_png(rm_path, Path(out_path))
        if render_err is not None:
            # Distinguish parse failures (rmc) from rasterization failures (cairosvg).
            kind = "render-rm-failure" if "rmc" in render_err.lower() else "render-png-failure"
            sys.stdout.write(emit_error_body(kind, {"name": target["name"], "detail": render_err}))
            sys.stdout.write("\n")
            try:
                if os.path.exists(out_path):
                    os.unlink(out_path)
            except OSError:
                pass
            return 0

    sys.stdout.write(emit_capture_body(out_path, free_text))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
