# roc — maintainer guide

This file applies when **working on this repository** (authoring or maintaining the marketplace and the plugins it ships), not when *consuming* a plugin from another project.

## What this repo is

A Claude Code **marketplace** named `roc` (displayed as **Roc**). It currently distributes two plugins: `rocket` (displayed as **Rocket 🚀**) and `my-hand` (displayed as **my-hand 🖐**). The marketplace is structured to host more plugins under `plugins/<name>/` over time.

`rocket` ships a curated set of skills and agents for assisted development; every skill and agent here is meant to be **stack-agnostic** and reused across multiple codebases.

`my-hand` ships four slash commands (`/my-hand:remarkable-grab`, `/my-hand:tone-profile`, `/my-hand:inbox-watch`, `/my-hand:inbox-reply`), one forked skill (`inbox-watch-tick`), one `SessionStart` hook, and two compiled binaries (reMarkable capture pipeline and inbox poller). It is the first sanctioned exception to the stack-agnostic rule (see Hard rule 4) on two grounds: it depends on local hardware (reMarkable tablet over USB) **and** on a per-user Gmail MCP server.

Each consumer project declares its own stack-specific conventions (test command, typing rules, error-handling style) in its own `CLAUDE.md`. The conventions block is generated interactively by the [`/rocket:setup`](plugins/rocket/skills/setup/SKILL.md) skill — its template is the source of truth. The plugins read those rules instead of carrying their own.

## Repository structure

```
.claude-plugin/marketplace.json     Marketplace manifest (lists the plugins)
plugins/<plugin-name>/
  .claude-plugin/plugin.json        Plugin manifest
  agents/                           Optional: agent definitions, one .md per agent
  skills/                           Optional: skills, one directory per skill, each with a SKILL.md
  commands/                         Optional: slash commands, one .md per command
  hooks/                            Optional: hooks.json + helper scripts invoked by the harness
  bin/<platform>/                   Optional: compiled binaries (non-portable plugins, per Hard rule 4)
  build/                            Optional: maintainer build script and sources for the binary
  README.md                         Plugin-specific user-facing doc
specs/                              Functional specs for plugins or features (one .md per topic/version)
README.md                           Public documentation (install, list of plugins/skills/agents)
CLAUDE.md                           This file — maintainer guide
```

A plugin uses whichever of `agents/`, `skills/`, `commands/`, `hooks/`, `bin/`, `build/` it needs — none are mandatory. `rocket` uses `agents/`, `skills/`, `hooks/`. `my-hand` uses `commands/`, `skills/`, `hooks/`, `bin/darwin-arm64/`, `build/`.

Currently there are two plugins: `plugins/rocket/` and `plugins/my-hand/`. Add a sibling directory under `plugins/` to ship a new plugin and register it in `marketplace.json#plugins`.

The conventions block template lives inside [`plugins/rocket/skills/setup/SKILL.md`](plugins/rocket/skills/setup/SKILL.md) (between `=== TEMPLATE START ===` and `=== TEMPLATE END ===`). It is the single source of truth — edit it there.

## Working commands

```bash
# Test a single plugin locally without installing it
claude --plugin-dir plugins/rocket

# Test the whole marketplace from this repo (installs the plugins it lists)
/plugin marketplace add .
/plugin install rocket@roc

# After editing a skill or agent, reload without restarting Claude Code
/reload-plugins
```

There is no build step, no test runner, no lint. Validation is manual: load the plugin and exercise the skills.

## Hard rules — what every contribution must follow

### 1. Plugin code must be stack-agnostic

Plugins are installed in projects with different stacks (TypeScript, Python, Go, etc.). Therefore:

- **Never hardcode stack-specific commands** (`yarn check`, `pytest`, `cargo build`, `docker compose ...`). Defer to the consumer's `CLAUDE.md`.
- **Never hardcode language rules** (`no any`, `absolute imports`, `no async-in-loops`). Same — defer.
- **Never reference a specific tool path** (`src/api/handlers/`). Plugins do not know the consumer's layout.

If a skill or agent needs project-specific behavior, instruct it to read the consumer's `CLAUDE.md` instead of carrying assumptions.

### 2. Skills and agents must be portable

A skill or agent that only works in one stack does not belong in this marketplace. If you need stack-specific behavior, build it as a project-level skill in the consumer's `.claude/skills/` directory instead (this is Claude Code's documented location for user-authored static skill markdown — not for plugin runtime state, which goes under `.roc/<plugin>/` per the "State location convention" section below).

### 3. English everywhere

All identifiers, frontmatter, comments, and prose are in English. Skill descriptions may list French triggers as alternative keywords (the user base is bilingual), but skill output is always English.

### 4. Exceptions to stack-agnosticism

A plugin may depend on local hardware, a specific OS, or a per-user external account (e.g. a personal MCP server bound to a single identity) if (a) it serves a narrow audience of operators who already meet those prerequisites, (b) it has no equivalent that fits within the consumer's `CLAUDE.md` model, and (c) the plugin's `README.md` explicitly states the hardware/OS/account prerequisite. `my-hand` is the first such plugin: it requires a reMarkable 2 tablet plugged in over USB **and** a per-user Gmail MCP server, and is tested only on macOS-arm64. Hardware non-portability and per-user-identity dependencies both qualify under this exception.

## Authoring a new skill

A skill lives in `plugins/<plugin>/skills/<name>/SKILL.md`. Frontmatter follows the [official spec](https://code.claude.com/docs/en/skills#frontmatter-reference).

### Frontmatter rules

```yaml
---
name: <kebab-case, matches directory name>
description: <see rules below>
disable-model-invocation: true   # Only if the skill is manual-only (e.g. /rocket:myself, /rocket:no-code)
---
```

- **`name`**: lowercase, hyphens, max 64 chars. Match the directory name.
- **`description`**: third person, max 1024 chars. Two questions to answer: *what does this skill do?* and *when should Claude invoke it?* Front-load the trigger keywords (`/<plugin>:<name>` first, then natural-language patterns in EN and FR). **Do NOT summarize the workflow in the description** — Claude may follow the description instead of reading the body.
- **`disable-model-invocation: true`**: add this only if the skill must be triggered explicitly by the user (e.g. modal skills like `/rocket:myself`, `/rocket:no-code`). The default — auto-invocation by Claude — is preferred for most skills.
- **`context: fork`** + **`agent: <name>`**: make the skill execute in a forked subagent with an isolated context. Use these for skills that must analyse the conversation in the background without blocking the main turn (e.g. `context-update`). The `agent` field picks the subagent type to run inside (`general-purpose`, `Explore`, or any custom subagent).
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
description: Generate git commit messages from staged or unstaged changes. Use this skill whenever the user invokes "/rocket:commit-writer", asks for a commit message, says "what should I commit?", "redige un message de commit", or any similar request.
```

Bad (no triggers, vague):

```yaml
description: Helps with git commits.
```

## Authoring a new agent

Agents live in `plugins/<plugin>/agents/<name>.md`. Frontmatter:

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
- `spec-maker` and `spec-writer` share an identical Step 0 (`Read .roc/rocket/lexicon.md if it exists...`). When changing it in one agent, apply the same change to the other to prevent drift.

## Authoring a new slash command

Slash commands live in `plugins/<plugin>/commands/<name>.md`. They are namespaced as `/<plugin>:<name>`. Frontmatter:

```yaml
---
description: <see rules below — same conventions as a skill description>
argument-hint: <one-line hint shown in the TUI when the user types the command>
allowed-tools:
  - Bash("${CLAUDE_PLUGIN_ROOT}/path/to/binary-or-script":*)
  - Read
---
```

- **`description`**: same rules as a skill description (third person, front-loaded triggers, EN/FR triggers OK). Front-load `/<plugin>:<command>` first, then natural-language patterns.
- **`argument-hint`**: optional but recommended. Single line, e.g. `[notebook-name]\n[optional free-text prompt]`.
- **`allowed-tools`**: pre-approves the tool calls the command body needs so the user is not prompted on every invocation.
  - For a `Bash(...)` pattern that calls a script or binary at `${CLAUDE_PLUGIN_ROOT}/...`, **wrap the path in double quotes inside the pattern**: `Bash("${CLAUDE_PLUGIN_ROOT}/bin/.../my-hand-grab":*)`. The `!`-prefix invocation in the body also quotes the path; the permission matcher compares strings literally, so unquoted patterns fail to match a quoted invocation. (Lesson learned in commit `0f196c8`.)
  - List every other tool the command needs (`Read`, etc.) so the model can use them without per-invocation approval.

### Body rules

- The body of the slash command markdown is the prompt the model sees after `$ARGUMENTS` substitution.
- A `!`-prefix line runs a bash command and inlines its stdout into the body. Use this to call a script or binary that produces the prompt body dynamically.
- Keep the body short. Most logic should live in the script/binary the body invokes; the body is a thin wrapper that runs it and forwards the output.
- The script the body invokes must always exit `0` and print a well-formed prompt body even on error. Crashing it propagates a failure to the slash command and the model loses context.

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with at minimum `name`, `version`, `description`, `author`. Use the [`rocket` plugin manifest](plugins/rocket/.claude-plugin/plugin.json) as a template.
2. Create `plugins/<plugin-name>/skills/` and/or `plugins/<plugin-name>/agents/`.
3. Register the plugin in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) by appending an entry to `plugins[]` with `"source": "./plugins/<plugin-name>"`.
4. Bump the marketplace `version` if applicable.

## Manifest rules

- Bump `version` in the relevant `plugin.json` on every behavioral change of that plugin. Without a version bump, distributed installs use commit SHA and every commit counts as an update.
- `plugin.json#name` is the **namespace prefix** for that plugin. Skills become `/<plugin>:<skill>`. Renaming a plugin breaks every consumer.
- `marketplace.json#name` is the marketplace identifier used in `/plugin install <plugin>@<marketplace>`. Renaming the marketplace breaks every consumer's `/plugin marketplace add` line.

## State location convention

**Never store plugin state under `.claude/` (project-local) or `~/.claude/` (user-global).** Claude Code's harness treats anything under those prefixes as sensitive and refuses to grant a permanent "always allow" on Bash, Read, Write, or Edit operations targeting them — breaking silent automation (every poll, every save prompts the user).

Use this layout instead:

- **User-global state** → `~/.roc/<plugin-name>/`. Survives across projects and sessions. Examples: `~/.roc/my-hand/tone.md`, `~/.roc/my-hand/inbox-state.json`.
- **Project-local state** → `<project>/.roc/<plugin-name>/`. Scoped to the working tree, can be committed selectively. Examples: `<project>/.roc/rocket/lexicon.md` (committed), `<project>/.roc/rocket/lexicon-update.log` (gitignored), `<project>/.roc/rocket/lexicon.md.lock.d/` (gitignored).

The `.claude/` directory remains exclusively for Claude Code's own state (plugin manifest cache, settings.local.json) and the user's personal overrides (`CLAUDE.local.md`, `settings.local.json`). Plugins never write there.

## Validating changes locally

1. From this repo's root: `claude --plugin-dir plugins/<plugin-name>` (e.g. `plugins/rocket`).
2. For each modified skill, run its slash command (`/rocket:commit-writer`, etc.) on a test repo.
3. For each modified agent, ask Claude to invoke it via the `Task` tool.
4. Confirm the description triggers it: rephrase a natural-language prompt and check that Claude proposes the right skill.
5. Run `/reload-plugins` between edits — no need to restart.
6. To validate the marketplace itself end-to-end, run `/plugin marketplace add .` then `/plugin install <plugin>@roc`.

## What NOT to do

- Do not add a skill for a workflow that already exists as a built-in (e.g. `/init`, `/review`, `/security-review`).
- Do not write code-style rules (indentation, quote style, semicolon policy). That is a linter's job in the consumer project.
- Do not include `Test plan` sections in skill outputs — `pr-writer` enforces this rule, and any skill that generates documentation must follow it.
- Do not add files to a plugin's `.claude-plugin/` directory other than `plugin.json`. Skills, agents, and hooks live at the plugin root (`plugins/<plugin>/skills/`, `plugins/<plugin>/agents/`, `plugins/<plugin>/hooks/`).
- Do not put `marketplace.json` anywhere other than the repo-root `.claude-plugin/`.
- Do not commit `CLAUDE.local.md` or `.claude/settings.local.json`. They are personal.

## When this CLAUDE.md should change

Add to it when:

- A skill or agent makes the same authoring mistake twice (hardcoded path, missing trigger, oversized description).
- A new convention emerges from a refactor (e.g. all skills now use bilingual triggers).
- The plugin or marketplace spec changes upstream (frontmatter fields, namespace rules, manifest schema).
- A new plugin is added under `plugins/` and warrants documentation specific to it.

Keep entries terse. If a section grows past ~40 lines, split it into a file under `docs/` and link it.

## References

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Plugins guide](https://code.claude.com/docs/en/plugins)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [CLAUDE.md memory guide](https://code.claude.com/docs/en/memory)
