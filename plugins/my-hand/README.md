# my-hand

A Claude Code plugin that captures the **current page** of a reMarkable 2 notebook over USB and delivers it to the model as a multimodal image. Useful when you think on paper and want Claude to read what you just wrote or drew.

Ships a single slash command: **`/my-hand:remarkable-grab`**.

## Hardware and OS prerequisites

`my-hand` is the first sanctioned **non-portable** plugin in the `roc` marketplace (see the addendum to the repo `CLAUDE.md`). It requires:

- A **reMarkable 2** tablet, firmware **3.x or later**.
- The tablet **plugged in over USB**, screen **unlocked**, and **USB web interface** enabled (`Settings -> Storage -> USB web interface`). The device must answer at `http://10.11.99.1`.
- **macOS-arm64**. Linux, Intel Mac, and Windows are out of scope.
- **No runtime dependencies.** The plugin ships a self-contained ~17 MB binary at `bin/darwin-arm64/my-hand-grab` with `rmc`, `cairosvg`, and `libcairo` (plus transitive `.dylib` deps) bundled via PyInstaller. The build itself (only relevant to maintainers) requires Python 3.11+ and `brew install cairo` — see `build/build.sh`.

If any prerequisite is missing, the slash command will still run but the model will surface a clear English error explaining what to fix.

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

Resolves the name (case-insensitive, **exact** match — no substring), downloads the notebook's `rmdoc` archive, locates the visible page targeted by `CurrentPage` (filtering deleted pages out of `cPages.pages`), renders the corresponding `.rm` file through `rmc` (SVG) and `cairosvg` (PNG) at native **1404×1872**, writes it to `/tmp/my-hand-remarkable-grab-<timestamp>.png`, and instructs the model to `Read` the file. The image becomes available to the model as a multimodal block.

### Capture with a free-text prompt

Anything after the first newline is forwarded to the model as instructions for what to do with the image:

```text
/my-hand:remarkable-grab Claude
What does this say? Reply only in French.
```

## Behavior notes

- **Current page only.** Captures `CurrentPage` of the notebook. Multi-page capture and explicit page indexing are deferred.
- **Full-resolution capture.** Each invocation produces a 1404×1872 PNG, the reMarkable 2 native page resolution. Fine handwriting and small annotations remain legible to the multimodal model.
- **Deleted-page filter.** `CurrentPage` is interpreted as an index into the notebook's *visible* pages, not the raw `cPages.pages[]` array (which retains tombstones for deleted pages).
- **24h cleanup.** Every invocation deletes `/tmp/my-hand-remarkable-grab-*.png` files older than 24 hours.
- **No caching.** Every invocation re-fetches the rmdoc archive from the tablet and re-renders.
- **Never crashes.** The binary always exits 0 and prints a well-formed prompt body. Errors are reported as English prose for the model to relay.

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| "tablet not reachable at `http://10.11.99.1`" | Tablet not plugged in, screen locked, or USB web interface disabled. Check `Settings -> Storage -> USB web interface`. |
| "`CurrentPage` out of range" or "content metadata empty" | Sync mismatch between the device and the USB web interface. Reopen the notebook on the tablet (open it, swipe to a page, then come back), then retry. |
| "Could not parse the page … unsupported reMarkable firmware" | The page was authored on a firmware whose `.rm` v6 schema `rmscene` does not yet handle. Report the firmware version. |
| "target page file is missing from the rmdoc archive" | Same fix as the sync mismatch above: reopen the notebook on the tablet and retry. |
| Two notebooks share a name | No path-qualified resolution syntax yet. Rename one of the conflicting notebooks on the tablet, then retry. |
| "OSError writing /tmp/..." | `/tmp` not writable. Confirm filesystem permissions. |

## What is **not** here (deferred)

- SSH access, developer mode, reMarkable cloud API.
- OCR / handwriting recognition.
- Multi-page capture, page-index argument (`--pages 3-7`, `--page 5`).
- Caching of fetched rmdoc or rendered PNG.
- MCP server architecture.
- Hooks, configuration files, environment variables.
- Linux, Intel Mac, and Windows builds.
- CI workflow producing the binary on tag (currently the maintainer runs `build/build.sh` by hand).
