# Roc — Claude Code marketplace

A Claude Code marketplace bundling AI-assisted development plugins. Currently ships two plugins:

- **Rocket 🚀** — stack-agnostic skills and agents that help a senior developer write specs, implement them, review changes, and produce commit and PR messages.
- **my-hand 🖐** — personal-expression toolkit: reMarkable page capture, email voice profile, and voice-grounded Gmail reply drafts. macOS-arm64 only; sanctioned non-portability exception per the repo's authoring rules.

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
- `/rocket:commit-writer rebase` — pick which commits since the default branch (plus uncommitted changes) define the scope; useful before a squash or rebase.

#### `/rocket:pr-writer`

Proposes a structured, product-focused PR description organised by topic, ready to copy-paste. Capped at 1-3 topics and ~30 lines.

- `/rocket:pr-writer`
- `/rocket:pr-writer rebase` — same commit picker as commit-writer.

#### `/rocket:review`

Reviews uncommitted/unpushed changes against six criteria: DRY, contiguous patterns, integration with existing conventions, test coverage, dead code, documentation drift. Produces a structured report.

- `/rocket:review`
- `/rocket:review rebase` — same commit picker as commit-writer.

#### `/rocket:myself`

The user wants to write the code themselves. The agent stops editing files and produces a precise change plan (`file:line` + short prose + why) instead.

- `/rocket:myself`

Manual-only — never auto-triggered.

#### `/rocket:no-code`

Forces a chat-only response. The agent will not create, edit, or delete any file for the rest of the turn.

- `/rocket:no-code`

Manual-only — never auto-triggered.

#### `/rocket:setup`

Initializes or refreshes the `## Project conventions` block in the current project's `CLAUDE.md`. Detects stack signals from manifests, lockfiles, CI workflows, and lint configs, composes the complete block, then asks for a single confirmation before writing. The block is delimited by `<!-- rocket:conventions:start/end -->` markers, so re-running anytime is safe: only the managed region is ever touched. Creates `CLAUDE.md` if it does not exist.

- `/rocket:setup`

Manual-only — never auto-triggered. The block it writes is consumed by `rocket:spec-maker` and `rocket:spec-writer`.

## my-hand 🖐

A personal-expression toolkit. Two independent feature sets, both **macOS-arm64 only**:

- **reMarkable page capture** — pull the current page of a reMarkable 2 notebook over USB into the model as a 1404×1872 multimodal image.
- **Voice-grounded Gmail reply drafts** — distill the user's email voice from sent Gmail, then on demand finalize a Gmail draft inside an existing thread, in that voice. Drafts are never sent.

### Slash commands

- `/my-hand:remarkable-grab [notebook-name]` — capture a notebook page (list mode if no name).
- `/my-hand:tone-profile` — distill the user's email voice into `~/.roc/my-hand/tone.md`.
- `/my-hand:inbox-reply <sender or subject keyword>` — finalize a Gmail draft inside the existing thread, asking you first for the answers the reply needs.

### Prerequisites

- **macOS-arm64.** Linux, Intel Mac, and Windows are out of scope.
- For the reMarkable feature: a **reMarkable 2** tablet (firmware 3.x+), plugged in over USB, screen unlocked, and **USB web interface** enabled (`Settings → Storage → USB web interface`). The device must answer at `http://10.11.99.1`.
- For the Gmail feature: a **Gmail MCP server** installed and bound on the host, exposing `search_threads`, `get_thread`, `create_draft`.
- **No runtime dependencies.** Ships a self-contained binary (~17 MB for the reMarkable pipeline); no Python or Homebrew needed at runtime.

See [`plugins/my-hand/README.md`](plugins/my-hand/README.md) for the rendering pipeline, troubleshooting, and what is intentionally deferred.

## Trigger language

Skill descriptions accept triggers in both English and French (`"write a commit message"` and `"redige un message de commit"` both fire `commit-writer`). Outputs are always in English, per the project quality rule.
