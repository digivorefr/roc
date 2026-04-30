# Roc — Claude Code plugin

Skills and agents that assist a senior developer through the development process: writing specs, implementing them, reviewing changes, and producing commit and PR messages.

This plugin is opinionated: each project that uses it should declare its own test command, stack conventions, and quality gates in its `CLAUDE.md` so the agents read them instead of carrying hardcoded assumptions. Run [`/roc:setup`](#rocsetup) to bootstrap that block interactively.

## Installation

```bash
claude plugins add https://github.com/digivorefr/roc
```

Then enable it in `/plugin` or via your settings.

## Agents

Agents are invoked via the `Task` tool (or by asking Claude to "use the spec-writer agent").

### `roc:spec-writer`

Writes a functional specification for a topic, anchored on existing patterns of the target codebase.

- Trigger: `write a spec with roc:spec-writer about ...`
- Refine: `relaunch spec-writer with these details: ...`

### `roc:spec-maker`

Implements a specification, plan, or detailed instructions autonomously, then runs the project's verification commands.

- Trigger: `implement with roc:spec-maker from specs/<file>.md`

The agent expects project-specific conventions (test command, lint rules, error-handling style) to be declared in the project's `CLAUDE.md`. Run [`/roc:setup`](#rocsetup) to generate that block.

## Skills

Skills can be invoked explicitly with `/roc:<name>` or auto-triggered when the description matches the request.

### `/roc:commit-writer`

Proposes 3 inline commit messages from the current diff.

- `/roc:commit-writer`
- `/roc:commit-writer only for these files: ...`

### `/roc:pr-writer`

Proposes a short, product-focused PR description ready to copy-paste.

- `/roc:pr-writer`

### `/roc:review`

Reviews uncommitted/unpushed changes against six criteria: DRY, contiguous patterns, integration with existing conventions, test coverage, dead code, documentation drift. Produces a structured report.

- `/roc:review`

### `/roc:myself`

The user wants to write the code themselves. The agent stops editing files and produces a precise change plan (`file:line` + short prose + why) instead.

- `/roc:myself`

Manual-only — never auto-triggered.

### `/roc:no-code`

Forces a chat-only response. The agent will not create, edit, or delete any file for the rest of the turn.

- `/roc:no-code`

Manual-only — never auto-triggered.

### `/roc:setup`

Initializes or refreshes the `## Project conventions` block in the current project's `CLAUDE.md`. Auto-detects stack signals from manifests (`package.json`, `pyproject.toml`, lockfiles, etc.), asks a few questions to fill the rest, then writes the block. Creates `CLAUDE.md` if it does not exist.

- `/roc:setup`

Manual-only — never auto-triggered. The block it writes is consumed by `roc:spec-maker` and `roc:spec-writer`.

## Trigger language

Skill descriptions accept triggers in both English and French (`"write a commit message"` and `"redige un message de commit"` both fire `commit-writer`). Outputs are always in English, per the project quality rule.
