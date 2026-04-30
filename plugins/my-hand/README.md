# my-hand

A Claude Code plugin that captures the **current page** of a reMarkable 2 notebook over USB and delivers it to the model as a multimodal image. Useful when you think on paper and want Claude to read what you just wrote or drew.

V0 ships a single slash command: **`/my-hand:remarkable-grab`**.

## Hardware and OS prerequisites

`my-hand` is the first sanctioned **non-portable** plugin in the `roc` marketplace (see the addendum to the repo `CLAUDE.md`). It requires:

- A **reMarkable 2** tablet, firmware **3.x or later**.
- The tablet **plugged in over USB**, screen **unlocked**, and **USB web interface** enabled (`Settings -> Storage -> USB web interface`). The device must answer at `http://10.11.99.1`.
- **macOS** (tested) or Linux (incidentally compatible). Windows is out of scope.
- **Python 3.11+** on `PATH` as `python3`. Standard library only — no `pip install`.

If any of those is missing, the slash command will still run but the model will surface a clear English error explaining what to fix.

## Install

From a project where you want the plugin available:

```text
/plugin marketplace add digivorefr/roc
/plugin install my-hand@roc
```

If you are testing this repository locally:

```bash
claude --plugin-dir plugins/my-hand
```

## Usage

### List mode — discover notebook names

```text
/my-hand:remarkable-grab
```

Lists every notebook on the device with its folder breadcrumb and last-modified timestamp. Use this to find the exact name to pass next.

### Capture mode — grab a page

```text
/my-hand:remarkable-grab Claude
```

Resolves the name (case-insensitive, **exact** match — no substring), fetches the **current page** thumbnail, writes it to `/tmp/my-hand-remarkable-grab-<timestamp>.png`, and instructs the model to `Read` the file. The image becomes available to the model as a multimodal block.

### Capture with a free-text prompt

Anything after the first newline is forwarded to the model as instructions for what to do with the image:

```text
/my-hand:remarkable-grab Claude
What does this say? Reply only in French.
```

## Behavior notes

- **Current page only.** V0 captures `CurrentPage` of the notebook. Multi-page capture and page indexing are deferred.
- **Thumbnail resolution.** The device serves a small (~384x512) PNG. Fine for handwriting and rough sketches, not for fine detail. Full-resolution rendering is deferred to V2+.
- **24h cleanup.** Every invocation deletes `/tmp/my-hand-remarkable-grab-*.png` files older than 24 hours.
- **No caching.** Every invocation re-fetches the thumbnail from the tablet.
- **Never crashes.** The script always exits 0 and prints a well-formed prompt body. Errors are reported as English prose for the model to relay.

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| "tablet not reachable at `http://10.11.99.1`" | Tablet not plugged in, screen locked, or USB web interface disabled. Check `Settings -> Storage -> USB web interface`. |
| "page may not be rendered yet" | The tablet has not yet rendered a thumbnail for that page. Draw a quick stroke and wait 2-3 seconds, or re-open the notebook on the tablet. |
| Two notebooks share a name | V0 has no path-qualified resolution syntax. Rename one of the conflicting notebooks on the tablet, then retry. |
| "OSError writing /tmp/..." | `/tmp` not writable. Confirm filesystem permissions. |

## What is **not** here (deferred)

- Full-resolution rendering via `rmdoc` + `rmc` / `cairosvg` / `drawj2d`.
- PDF endpoint usage and `pdftoppm`.
- SSH access, developer mode, reMarkable cloud API.
- OCR / handwriting recognition.
- Multi-page capture, page-index argument.
- Caching.
- MCP server architecture.
- Hooks, configuration files, environment variables.
