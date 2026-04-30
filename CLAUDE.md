# roc — maintainer guide

This file applies when **working on this repository** (authoring or maintaining the plugin), not when *using* the plugin in another project.

## What this repo is

A Claude Code plugin that ships a curated set of skills and agents for assisted development. It is consumed by other projects via `claude plugins add`. Every skill and agent here is meant to be **stack-agnostic** and reused across multiple codebases.

Each consumer project declares its stack-specific conventions (test command, typing rules, error-handling style) in its own `CLAUDE.md`. The conventions block is generated interactively by the [`/roc:setup`](skills/setup/SKILL.md) skill — its template is the source of truth. The plugin reads those rules instead of carrying its own.

## Repository structure

```
.claude-plugin/plugin.json   Plugin manifest (name, version, author, repo, license)
agents/                      Agent definitions, one .md per agent
skills/                      Skills, one directory per skill, each with a SKILL.md
README.md                    Public documentation (install, list of skills/agents)
CLAUDE.md                    This file — maintainer guide
```

The conventions block template lives inside [`skills/setup/SKILL.md`](skills/setup/SKILL.md) (between `=== TEMPLATE START ===` and `=== TEMPLATE END ===`). It is the single source of truth — edit it there.

## Working commands

```bash
# Test the plugin locally without installing it
claude --plugin-dir .

# After editing a skill or agent, reload without restarting Claude Code
/reload-plugins
```

There is no build step, no test runner, no lint. Validation is manual: load the plugin and exercise the skills.

## Hard rules — what every contribution must follow

### 1. Plugin code must be stack-agnostic

The plugin is installed in projects with different stacks (TypeScript, Python, Go, etc.). Therefore:

- **Never hardcode stack-specific commands** (`yarn check`, `pytest`, `cargo build`, `docker compose ...`). Defer to the consumer's `CLAUDE.md`.
- **Never hardcode language rules** (`no any`, `absolute imports`, `no async-in-loops`). Same — defer.
- **Never reference a specific tool path** (`src/api/handlers/`). The plugin doesn't know the consumer's layout.

If a skill or agent needs project-specific behavior, instruct it to read the consumer's `CLAUDE.md` instead of carrying assumptions.

### 2. Skills and agents must be portable

A skill or agent that only works in one stack does not belong in this plugin. If you need stack-specific behavior, build it as a project-level skill in the consumer's `.claude/skills/` directory instead.

### 3. English everywhere

All identifiers, frontmatter, comments, and prose are in English. Skill descriptions may list French triggers as alternative keywords (the plugin user base is bilingual), but skill output is always English.

## Authoring a new skill

A skill lives in `skills/<name>/SKILL.md`. Frontmatter follows the [official spec](https://code.claude.com/docs/en/skills#frontmatter-reference).

### Frontmatter rules

```yaml
---
name: <kebab-case, matches directory name>
description: <see rules below>
disable-model-invocation: true   # Only if the skill is manual-only (e.g. /myself, /no-code)
---
```

- **`name`**: lowercase, hyphens, max 64 chars. Match the directory name.
- **`description`**: third person, max 1024 chars. Two questions to answer: *what does this skill do?* and *when should Claude invoke it?* Front-load the trigger keywords (`/roc:<name>` first, then natural-language patterns in EN and FR). **Do NOT summarize the workflow in the description** — Claude may follow the description instead of reading the body.
- **`disable-model-invocation: true`**: add this only if the skill must be triggered explicitly by the user (e.g. modal skills like `/roc:myself`, `/roc:no-code`). The default — auto-invocation by Claude — is preferred for most skills.
- Do **not** set `user-invocable: true`. It is the default and adds noise.

### Body rules

- Keep `SKILL.md` **under 500 lines**. Above that, split into sibling files (`reference.md`, `examples.md`) and link them with one-level-deep references from `SKILL.md`.
- Open with a one-paragraph description of the mode/role the skill enacts.
- Then a `## Rules` or `## Output contract` section listing hard constraints.
- Then a `## Workflow` section with numbered steps if the skill is procedural.
- End with concrete `## Good examples` and `## Bad examples` if output format matters (commit messages, PR descriptions). Examples beat descriptions.
- Match degrees of freedom to fragility: rigid workflow (commit-writer, pr-writer, review) → numbered steps and explicit constraints; modal/judgment skill (myself, no-code) → principles and a single illustrative example.
- No time-sensitive content. No "as of 2026". No magic numbers without justification.

### Description examples (from this repo)

Good (specific trigger + intent):

```yaml
description: Generate git commit messages from staged or unstaged changes. Use this skill whenever the user invokes "/roc:commit-writer", asks for a commit message, says "what should I commit?", "redige un message de commit", or any similar request.
```

Bad (no triggers, vague):

```yaml
description: Helps with git commits.
```

## Authoring a new agent

Agents live in `agents/<name>.md`. Frontmatter:

```yaml
---
name: <kebab-case>
description: "<JSON-escaped string with ONE example using <example>...<commentary> tags>"
model: <inherit | opus | sonnet | haiku>
color: <visual hint>
---
```

- One example is enough. Multi-example descriptions inflate startup context.
- Body opens with a role statement, then sections like `## Core Philosophy`, `## Workflow`, `## What You Must NOT Do`.
- An agent that implements features (`spec-maker`) must read the consumer's `CLAUDE.md` for stack rules and use the verification command declared there.
- An agent that produces documents (`spec-writer`) must defer stack rules to the consumer's `CLAUDE.md` rather than restating them.

## Plugin manifest rules

- Bump `version` in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) on every behavioral change. Without a version bump, distributed installs use commit SHA and every commit counts as an update.
- `name` is the namespace prefix. Skills become `/roc:<skill>`. Renaming the plugin breaks every consumer.

## Validating changes locally

1. `claude --plugin-dir .` from this repo's root.
2. For each modified skill, run its slash command (`/roc:commit-writer`, etc.) on a test repo.
3. For each modified agent, ask Claude to invoke it via the `Task` tool.
4. Confirm the description triggers it: rephrase a natural-language prompt and check that Claude proposes the right skill.
5. Run `/reload-plugins` between edits — no need to restart.

## What NOT to do

- Do not add a skill for a workflow that already exists as a built-in (e.g. `/init`, `/review`, `/security-review`).
- Do not write code-style rules (indentation, quote style, semicolon policy). That is a linter's job in the consumer project.
- Do not include `Test plan` sections in skill outputs — `pr-writer` enforces this rule, and any skill that generates documentation must follow it.
- Do not add files to `.claude-plugin/` other than `plugin.json`. Skills, agents, and hooks live at the repo root.
- Do not commit `CLAUDE.local.md` or `.claude/settings.local.json`. They are personal.

## When this CLAUDE.md should change

Add to it when:

- A skill or agent makes the same authoring mistake twice (hardcoded path, missing trigger, oversized description).
- A new convention emerges from a refactor (e.g. all skills now use bilingual triggers).
- The plugin spec changes upstream (frontmatter fields, namespace rules, manifest schema).

Keep entries terse. If a section grows past ~40 lines, split it into a file under `docs/` and link it.

## References

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Plugins guide](https://code.claude.com/docs/en/plugins)
- [CLAUDE.md memory guide](https://code.claude.com/docs/en/memory)
