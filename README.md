# Roc — Claude Code marketplace

A Claude Code marketplace bundling AI-assisted development plugins. Currently ships two plugins:

- **Rocket 🚀** — stack-agnostic skills and agents that help a senior developer write specs, implement them, review changes, produce commit and PR messages, maintain a per-project semantic lexicon, and reset it on demand.
- **my-hand 🖐** — personal-expression toolkit: reMarkable page capture, Gmail inbox watcher, and voice-grounded reply drafts. macOS-arm64 only; sanctioned non-portability exception per the repo's authoring rules.

Rocket is opinionated: each project that uses it should declare its own test command, stack conventions, and quality gates in its `CLAUDE.md` so the agents read them instead of carrying hardcoded assumptions. Run [`/rocket:setup`](#rocketsetup) to bootstrap that block interactively.

## Installation

From inside Claude Code:

```text
/plugin marketplace add digivorefr/roc
/plugin install rocket@roc
/plugin install my-hand@roc      # optional, macOS-arm64 only — useful with a reMarkable 2 and/or a Gmail MCP server
```

From Claude Desktop: open **Customize → Plugins personnels**, click **Ajouter une marketplace**, paste `digivorefr/roc` in the URL field, then install the desired plugin from the marketplace listing.

## Rocket 🚀

### Agents

Agents are invoked via the `Task` tool (or by asking Claude to "use the spec-writer agent").

#### `rocket:spec-writer`

Writes a functional specification for a topic, anchored on existing patterns of the target codebase.

- Trigger: `write a spec with rocket:spec-writer about ...`
- Refine: `relaunch spec-writer with these details: ...`

#### `rocket:spec-maker`

Implements a specification, plan, or detailed instructions autonomously, then runs the project's verification commands.

- Trigger: `implement with rocket:spec-maker from specs/<file>.md`

The agent expects project-specific conventions (test command, lint rules, error-handling style) to be declared in the project's `CLAUDE.md`. Run [`/rocket:setup`](#rocketsetup) to generate that block.

### Skills

Skills can be invoked explicitly with `/rocket:<name>` or auto-triggered when the description matches the request.

#### `/rocket:commit-writer`

Proposes 3 inline commit messages from the current diff.

- `/rocket:commit-writer`
- `/rocket:commit-writer only for these files: ...`

#### `/rocket:pr-writer`

Proposes a structured, product-focused PR description organised by topic, ready to copy-paste.

- `/rocket:pr-writer`

#### `/rocket:review`

Reviews uncommitted/unpushed changes against six criteria: DRY, contiguous patterns, integration with existing conventions, test coverage, dead code, documentation drift. Produces a structured report.

- `/rocket:review`

#### `/rocket:myself`

The user wants to write the code themselves. The agent stops editing files and produces a precise change plan (`file:line` + short prose + why) instead.

- `/rocket:myself`

Manual-only — never auto-triggered.

#### `/rocket:no-code`

Forces a chat-only response. The agent will not create, edit, or delete any file for the rest of the turn.

- `/rocket:no-code`

Manual-only — never auto-triggered.

#### `/rocket:context-update`

Updates the project's semantic lexicon at `.roc/rocket/lexicon.md` from the current conversation. The lexicon is a compact catalog of project-specific concepts, vocabulary, patterns, and decisions, read by `rocket:spec-writer` and `rocket:spec-maker` to align their vocabulary with yours.

- `/rocket:context-update`

Auto-triggered by Claude when a major semantic shift just happened in the conversation. Also auto-runs in the background after every assistant turn via a `Stop` hook (asynchronous, non-blocking, `claude -p --model "sonnet[1m]"` subprocess). The hook is debounced 30 s, tails the transcript to its last 500 lines, runs them through a stripper that removes token-heavy fields (`signature`, `thinking`, `originalFile`, image base64) and caps each line at 8 KB, then pipes the result to the subprocess. Logs land in `.roc/rocket/lexicon-update.log` (rotated at 1 MB, last 3 kept). Bootstrap the lexicon and the `## Project semantic context` reference in `CLAUDE.md` by running [`/rocket:setup`](#rocketsetup).

The lexicon is a flat catalog of `## <Area>` sections (e.g. Domain, Architecture, Roles, Conventions, Decisions) containing `### <Concept>` entries. Each entry has exactly four bullets — `Definition`, `Aliases`, `Relations`, `Source` — and stays compact (cap: 300 lines or 12 KB, whichever smaller). Manual edits are preserved when consistent; contradictions are flagged with a `<!-- TODO -->` comment for human review.

#### `/rocket:context-clear`

Wipes the project's rocket-managed contextualization files under `.roc/rocket/` (lexicon, logs, lock dirs, leftover temp files). Two-step: list, then delete with `force`.

- `/rocket:context-clear` — list mode (no deletion).
- `/rocket:context-clear force` — actually delete.

Manual-only — never auto-triggered. Scoped to the current project; user-global state under `~/.roc/...` is not touched. The `## Project semantic context` block in `CLAUDE.md` is preserved; remove it manually if you also want to reset that.

#### `/rocket:setup`

Initializes or refreshes the `## Project conventions` block in the current project's `CLAUDE.md`. Auto-detects stack signals from manifests (`package.json`, `pyproject.toml`, lockfiles, etc.), asks a few questions to fill the rest, then writes the block. Creates `CLAUDE.md` if it does not exist.

- `/rocket:setup`

Manual-only — never auto-triggered. The block it writes is consumed by `rocket:spec-maker` and `rocket:spec-writer`.

## my-hand 🖐

A personal-expression toolkit. Two cooperating but independent feature sets, both **macOS-arm64 only**:

- **reMarkable page capture** — pull the current page of a reMarkable 2 notebook over USB into the model as a 1404×1872 multimodal image.
- **Gmail inbox watcher with voice-grounded reply drafts** — distill the user's email voice from sent Gmail, periodically poll the inbox in a dedicated mail-session conversation, suggest 2-4 sentence replies in that voice, and on demand finalize a Gmail draft inside the existing thread. Drafts are never sent.

### Slash commands

- `/my-hand:remarkable-grab [notebook-name]` — capture a notebook page (list mode if no name).
- `/my-hand:tone-profile` — distill the user's email voice into `~/.roc/my-hand/tone.md`.
- `/my-hand:inbox-watch start | stop | tick` — manage the Gmail mail-session loop.
- `/my-hand:inbox-reply <sender or subject keyword>` — finalize a Gmail draft inside the existing thread.

### Prerequisites

- **macOS-arm64.** Linux, Intel Mac, and Windows are out of scope.
- For the reMarkable feature: a **reMarkable 2** tablet (firmware 3.x+), plugged in over USB, screen unlocked, and **USB web interface** enabled (`Settings → Storage → USB web interface`). The device must answer at `http://10.11.99.1`.
- For the Gmail feature: a **Gmail MCP server** installed and bound on the host, exposing `search_threads`, `get_thread`, `create_draft`. `osascript` (default on macOS) for banner notifications.
- **No runtime dependencies.** Ships a self-contained ~17 MB binary for the reMarkable pipeline; the Gmail features are pure prompt orchestration.

See [`plugins/my-hand/README.md`](plugins/my-hand/README.md) for the rendering pipeline, the mail-session flow, troubleshooting, and what is intentionally deferred.

## Trigger language

Skill descriptions accept triggers in both English and French (`"write a commit message"` and `"redige un message de commit"` both fire `commit-writer`). Outputs are always in English, per the project quality rule.
