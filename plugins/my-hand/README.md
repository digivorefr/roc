# my-hand

A Claude Code plugin that hosts personal-expression features tied to the user's own voice, hand, and identity. It bundles two cooperating but independent feature sets:

- **reMarkable page capture** — pull the current page of a reMarkable 2 notebook over USB into the model as a multimodal image.
- **Gmail inbox watcher with voice-grounded reply drafts** — distill the user's email voice from sent Gmail, periodically poll the inbox in a dedicated mail-session conversation, suggest 2-4 sentence replies in that voice, and on demand finalize a Gmail draft inside the existing thread. Drafts are never sent.

Slash commands shipped:

- `/my-hand:remarkable-grab [notebook-name]` — capture a notebook page.
- `/my-hand:tone-profile` — distill the user's email voice into `~/.claude/state/my-hand/tone.md`.
- `/my-hand:inbox-watch start | stop | tick` — manage a Gmail mail-session loop.
- `/my-hand:inbox-reply <sender or subject keyword>` — finalize a Gmail draft inside the existing thread.

## Hardware and OS prerequisites

`my-hand` is the first sanctioned **non-portable** plugin in the `roc` marketplace (see the addendum to the repo `CLAUDE.md`). It is **macOS-arm64 only**. Linux, Intel Mac, and Windows are out of scope.

### reMarkable feature

- A **reMarkable 2** tablet, firmware **3.x or later**.
- The tablet **plugged in over USB**, screen **unlocked**, and **USB web interface** enabled (`Settings -> Storage -> USB web interface`). The device must answer at `http://10.11.99.1`.
- **No runtime dependencies.** The plugin ships a self-contained ~17 MB binary at `bin/darwin-arm64/my-hand-grab` with `rmc`, `cairosvg`, and `libcairo` (plus transitive `.dylib` deps) bundled via PyInstaller. The build itself (only relevant to maintainers) requires Python 3.11+ and `brew install cairo` — see `build/build.sh`.

### Gmail feature

- A **Gmail account** with an **MCP server** installed and bound on the host that exposes the standard Gmail tool suffixes: `search_threads`, `get_thread`, `create_draft`. The plugin references these by stable suffix only; the local UUID prefix is never embedded in any committed file.
- `osascript` on `PATH` (default on macOS) for banner notifications.
- Single-account, single-operator. Multi-account Gmail is out of scope.

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

### reMarkable feature

#### List mode — discover notebook names

```text
/my-hand:remarkable-grab
```

Lists every notebook on the device with its folder breadcrumb and last-modified timestamp. Use this to find the exact name to pass next.

#### Capture mode — grab a page

```text
/my-hand:remarkable-grab Claude
```

Resolves the name (case-insensitive, **exact** match — no substring), downloads the notebook's `rmdoc` archive, locates the visible page targeted by `CurrentPage` (filtering deleted pages out of `cPages.pages`), renders the corresponding `.rm` file through `rmc` (SVG) and `cairosvg` (PNG) at native **1404×1872**, writes it to `/tmp/my-hand-remarkable-grab-<timestamp>.png`, and instructs the model to `Read` the file. The image becomes available to the model as a multimodal block.

#### Capture with a free-text prompt

Anything after the first newline is forwarded to the model as instructions for what to do with the image:

```text
/my-hand:remarkable-grab Claude
What does this say? Reply only in French.
```

### Gmail feature

#### One-time setup

Run once, then refresh every ~30 days as your style drifts:

```text
/my-hand:tone-profile
```

The model queries the last 30 days of sent Gmail (capped at 50 messages), extracts user-composed text only, distills 5-10 saliency bullets and three representative example messages, and writes the file to `~/.claude/state/my-hand/tone.md` (capped at 5 KB).

#### Mail-session loop

Open a Claude Code conversation in a project of your choosing — a dedicated `~/inbox-watch/` project is suggested so the conversation stays clean and predictable.

```text
/my-hand:inbox-watch start
```

That conversation becomes the **mail session**. The loop polls Gmail every 10 minutes via the `loop` skill. Empty polls produce **no output**. Non-empty polls emit one short markdown table (per-tick context cost is bounded by a forked sub-agent) and fire a macOS banner notification with the title `Claude — N nouveau(x) mail(s)`.

When you reopen Claude Code in the same project, polling auto-resumes via a `SessionStart` hook. In any other project, this plugin is silent.

```text
/my-hand:inbox-watch stop
```

Disables auto-resume by removing `~/.claude/state/my-hand/mail-session.path`. **Note:** in V1, `stop` only removes the sentinel; it does not stop the currently running loop. To stop polling immediately, end the conversation.

```text
/my-hand:inbox-watch tick
```

Forces a poll right now without waiting for the loop. Same output contract as a scheduled tick.

#### Manual draft

```text
/my-hand:inbox-reply <sender or subject keyword>
```

The model looks up the keyword against the most recent tick's `pending_replies`, generates a polished email matching `tone.md` in the language of the original message, and saves it as a Gmail draft attached to the existing thread. **Sending is forbidden by the slash command's `allowed-tools` declaration.** Open Gmail to review and send manually.

## Behavior notes

### reMarkable

- **Current page only.** Captures `CurrentPage` of the notebook. Multi-page capture and explicit page indexing are deferred.
- **Full-resolution capture.** Each invocation produces a 1404×1872 PNG, the reMarkable 2 native page resolution. Fine handwriting and small annotations remain legible to the multimodal model.
- **Deleted-page filter.** `CurrentPage` is interpreted as an index into the notebook's *visible* pages, not the raw `cPages.pages[]` array (which retains tombstones for deleted pages).
- **24h cleanup.** Every invocation deletes `/tmp/my-hand-remarkable-grab-*.png` files older than 24 hours.
- **No caching.** Every invocation re-fetches the rmdoc archive from the tablet and re-renders.
- **Never crashes.** The binary always exits 0 and prints a well-formed prompt body. Errors are reported as English prose for the model to relay.

### Gmail

- **Polling interval.** 10 minutes via the `loop` skill. Empty ticks are silent.
- **Auto-resume scope.** Only the project recorded in `~/.claude/state/my-hand/mail-session.path` triggers the SessionStart bootstrap. Every other project is untouched.
- **Voice profile cap.** `tone.md` is capped at 5 KB. The model trims before writing if needed.
- **Reply suggestions.** 2-4 sentences, language-matched to the source message.
- **Drafts only.** `/my-hand:inbox-reply` uses `create_draft` exclusively. Sending always happens manually via the Gmail UI.
- **Concurrency.** Ticks are serialized by an atomic `mkdir`-based lock at `~/.claude/state/my-hand/mail-poll.lock.d/`. A stale lock (mtime > 600 s) is reaped automatically.
- **Notification language.** The macOS banner title is intentionally French (`Claude — N nouveau(x) mail(s)`) for one-glance recognition. The body content is English-clean. This is the single intentional French string in the plugin.

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| "tablet not reachable at `http://10.11.99.1`" | Tablet not plugged in, screen locked, or USB web interface disabled. Check `Settings -> Storage -> USB web interface`. |
| "`CurrentPage` out of range" or "content metadata empty" | Sync mismatch between the device and the USB web interface. Reopen the notebook on the tablet (open it, swipe to a page, then come back), then retry. |
| "Could not parse the page … unsupported reMarkable firmware" | The page was authored on a firmware whose `.rm` v6 schema `rmscene` does not yet handle. Report the firmware version. |
| "target page file is missing from the rmdoc archive" | Same fix as the sync mismatch above: reopen the notebook on the tablet and retry. |
| Two notebooks share a name | No path-qualified resolution syntax yet. Rename one of the conflicting notebooks on the tablet, then retry. |
| "OSError writing /tmp/..." | `/tmp` not writable. Confirm filesystem permissions. |
| `Voice profile missing` printed by `/my-hand:inbox-watch start` or `/my-hand:inbox-reply` | Run `/my-hand:tone-profile` first. |
| Tick output empty when new mail expected | Thread already in `last_seen_thread_ids` from a prior tick; check `~/.claude/state/my-hand/inbox-state.json`. |
| Tick output empty + lock present | Stale lock from a crashed prior run; reaped at 600 s automatically. To force-release, `rmdir ~/.claude/state/my-hand/mail-poll.lock.d/`. |
| No macOS notification on non-empty tick | `osascript` unreachable, or the system has banner notifications disabled for Terminal/iTerm. |
| Watcher not auto-resuming on session start | Confirm `~/.claude/state/my-hand/mail-session.path` matches your `pwd` (resolved via `realpath`). |
| `inbox-reply <args>` finds 0 matches | The keyword does not match any sender/company/subject in `pending_replies` from the most recent tick. Use a more specific keyword or wait for the next tick. |
| `inbox-reply` returns "Draft created" but Gmail UI shows nothing | The Gmail MCP server may have written to a different account. Check the MCP server config. |
| Polling does not auto-resume even in the configured project | Verify the sentinel exists (`cat ~/.claude/state/my-hand/mail-session.path`). To opt out entirely, run `/my-hand:inbox-watch stop` or delete the sentinel by hand. |

## What is **not** here (deferred)

- SSH access, developer mode, reMarkable cloud API.
- OCR / handwriting recognition.
- Multi-page capture, page-index argument (`--pages 3-7`, `--page 5`).
- Caching of fetched rmdoc or rendered PNG.
- MCP server architecture for reMarkable.
- Hooks beyond the SessionStart bootstrap.
- Linux, Intel Mac, and Windows builds.
- CI workflow producing the binary on tag (currently the maintainer runs `build/build.sh` by hand).
- 24/7 polling with Claude Code closed (would require launchd + `claude -p`).
- macOS notification click actions (would require the `terminal-notifier` brew dependency).
- Reply sending. `/my-hand:inbox-reply` only ever creates drafts.
- Multi-account Gmail. Outlook / IMAP / other providers.
- Filter by label, sender, sensitivity. Spam / promotions exclusion.
- Auto-rebuild of the tone profile on a schedule.
- Cross-language reply translation.
