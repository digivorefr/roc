# Roc — Claude Code marketplace

A Claude Code marketplace bundling AI-assisted development plugins. Currently ships one plugin: **Rocket 🚀** — skills and agents that help a senior developer write specs, implement them, review changes, and produce commit and PR messages.

Rocket is opinionated: each project that uses it should declare its own test command, stack conventions, and quality gates in its `CLAUDE.md` so the agents read them instead of carrying hardcoded assumptions. Run [`/rocket:setup`](#rocketsetup) to bootstrap that block interactively.

## Installation

From inside Claude Code:

```text
/plugin marketplace add digivorefr/roc
/plugin install rocket@roc
```

From Claude Desktop: open **Customize → Plugins personnels**, click **Ajouter une marketplace**, paste `digivorefr/roc` in the URL field, then install the `rocket` plugin from the marketplace listing.

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

#### `/rocket:setup`

Initializes or refreshes the `## Project conventions` block in the current project's `CLAUDE.md`. Auto-detects stack signals from manifests (`package.json`, `pyproject.toml`, lockfiles, etc.), asks a few questions to fill the rest, then writes the block. Creates `CLAUDE.md` if it does not exist.

- `/rocket:setup`

Manual-only — never auto-triggered. The block it writes is consumed by `rocket:spec-maker` and `rocket:spec-writer`.

## Trigger language

Skill descriptions accept triggers in both English and French (`"write a commit message"` and `"redige un message de commit"` both fire `commit-writer`). Outputs are always in English, per the project quality rule.
