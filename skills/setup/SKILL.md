---
name: setup
disable-model-invocation: true
description: Initialize or update the project's CLAUDE.md with the conventions block consumed by roc:spec-maker and roc:spec-writer. Auto-detects stack signals from manifests, asks a few questions to fill the rest, then writes the block to CLAUDE.md (creating the file if absent). Manual-only — invoked by the user via "/roc:setup".
---

# Project conventions setup

The user wants to add (or refresh) the `## Project conventions` block in this project's `CLAUDE.md`. That block is read by `roc:spec-maker` and `roc:spec-writer` to follow project-specific stack rules.

Drive an interactive setup: detect what you can from the project's manifests, ask the user only for what cannot be inferred, then write the block.

## Workflow

### Step 1 — Read existing state

1. Check if `CLAUDE.md` exists at the repo root (cwd).
2. If it exists, read it and check whether the heading `## Project conventions (read by` is already present.
3. If the block is already present, ask the user how to handle it via `AskUserQuestion`:

   - **Replace** — overwrite the existing block with a new one
   - **Skip** — exit the skill, change nothing
   - **Append below** — keep the existing block, add a second one underneath

   If the user picks **Skip**, stop here.

### Step 2 — Auto-detect signals (minimal)

Run these reads in parallel. Do not ask the user yet — just collect what is available:

- `package.json` — language is JS/TS, capture `name`, `packageManager`, `engines.node`, key dependencies (`next`, `react`, `express`, `nestjs`, `fastify`, `vue`...)
- `pyproject.toml` — language is Python, capture `project.name`, `requires-python`, `[tool.poetry]` / `[tool.uv]` markers
- `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json` — capture language and version if present
- Lockfiles — `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`, `uv.lock`, `poetry.lock`, `Pipfile.lock` — infer the package manager
- `package.json#scripts.check`, `scripts.test`, `scripts.lint` — candidates for the verification command
- `pyproject.toml` task runners (`[tool.poe.tasks]`, `[tool.taskipy.tasks]`) — same
- `Makefile` — candidates if a `check` or `test` target exists

Store the detected values. Do not run any command.

### Step 3 — Round 1 questions

Ask up to 4 questions in a single `AskUserQuestion` call. For each detected value, put it as the first option labelled `(Recommended)`. The free-text "Other" option is added automatically by the tool — do not add it manually.

The four questions:

1. **`Stack summary`** — present the detected language + framework as the recommended option. Two-three alternatives covering common stacks. The user picks or types their own.
2. **`Verify cmd`** — present detected `check`/`test` script(s) as recommended. If multiple were detected, list each as a separate option (max 4).
3. **`Typing rules`** — three options:
   - `Strict (Recommended)` — bans `any`/equivalent, no inline lint disables
   - `Loose` — typed but pragmatic, allow occasional escapes
   - `Not applicable` — untyped language
4. **`Optional sections`** — `multiSelect: true`. Options:
   - `Logging & observability`
   - `Error handling philosophy`
   - `Naming and structure`
   - `Async control flow`

   The user ticks which sections to include. Mandatory sections (Stack, Verification command, What NOT to do) are always written and not listed here.

### Step 4 — Round 2 questions (conditional)

For each section the user ticked in Round 1.4, ask the corresponding question. Batch them in a single `AskUserQuestion` call (up to 4 at once).

- **Logging & observability** — `Logger`: ask for the logger library or wrapper file path (no recommended option — free text expected).
- **Error handling philosophy** — `Error policy`: two options:
  - `Standard (Recommended)` — uses the default rules (no global try/catch, optimistic, validate at boundaries)
  - `Custom` — user provides their own rules in the "Other" field
- **Naming and structure** — `File naming` (kebab / camel / snake / Pascal — pick the convention that matches the detected stack as recommended) and `Tests location` (e.g. `__tests__/` next to source, `tests/` mirror tree, `_test.go` suffix — pick based on detected stack).
- **Async control flow** — `Async rules`: two options:
  - `Standard (Recommended)` — "No `await` inside `for` loops. Use `Promise.all` / batching."
  - `Custom` — free text

If more than 4 questions accumulate (rare — only if all 4 sections ticked AND naming has 2 sub-questions), split into two `AskUserQuestion` calls.

### Step 5 — Render the block

Take the template below and:

- Substitute every `<TO FILL: ...>` with the corresponding answer or detected value.
- Drop entire `### <section>` blocks for sections the user did NOT tick in Round 1.4 (apart from Stack, Verification command, and What NOT to do which are always kept).
- For the "Standard" choices in Round 2, keep the bullets exactly as written in the template. For "Custom" choices, replace the bullets with the user's free-text answer.

### Step 6 — Write to CLAUDE.md

- **No `CLAUDE.md`** — create it. Open with a single line: `# <project-name>` (use the name from `package.json#name` / `pyproject.toml#project.name` / cwd directory name as fallback), one blank line, then the rendered block.
- **`CLAUDE.md` exists, no conventions block** — append the rendered block at the end of the file with one blank line separator before it.
- **`CLAUDE.md` exists, conventions block present** — apply the action chosen at Step 1:
  - `Replace` — replace the existing block (from `## Project conventions (read by` up to the next top-level `##` heading or EOF) with the rendered one.
  - `Append below` — insert the rendered block right after the existing one with one blank line separator.

### Step 7 — Confirm

Output a short summary:

- Path written
- Whether the file was created or updated
- Sections included
- Detected values that were accepted as-is
- Any field still containing a placeholder the user should review

Keep it under 10 lines. No emojis.

## Template

The text between `=== TEMPLATE START ===` and `=== TEMPLATE END ===` is the literal block to write. Substitute every `<TO FILL: ...>` placeholder. Triple backticks inside the template are part of the output.

=== TEMPLATE START ===
## Project conventions (read by `roc:spec-maker` and `roc:spec-writer`)

### Stack

- Language(s): <TO FILL: language and major version>
- Runtime / framework: <TO FILL: runtime + framework>
- Package manager: <TO FILL: pnpm / yarn 4 / npm / uv / poetry / cargo / go modules / ...>
- Test framework: <TO FILL: Jest / Vitest / pytest / go test / cargo test / ...>

### Verification command

Run this single command after implementation. It must return non-zero on lint, type, or test failure:

```bash
<TO FILL: full command>
```

If it fails, fix the underlying issue. Never bypass it (no `--no-verify`, no rule-disable comments, no skipped tests).

### Typing rules

- The `any` type (or its language equivalent) is forbidden. Use proper types or `unknown` / `object` / generics.
- Lint rules must not be disabled inline. If a rule fires, fix the code.
- All identifiers, comments, and strings are written in English regardless of conversation language.

### Error handling philosophy

- No global `try/catch` wrappers around business logic. Errors bubble up to a single handler at the framework boundary, which already logs them.
- Be optimistic: do not catch errors you cannot meaningfully recover from.
- Validation happens at system boundaries (request handlers, external APIs). Internal code trusts its callers.
- Never swallow errors silently.

### Logging & observability

- Logger: <TO FILL: logger library or wrapper file path>
- Use `debug` / `info` levels generously for troubleshooting context.
- Wrap non-trivial operations with `logger.span(...)` (or your project's tracing helper) for distributed-trace visibility.
- Do not log secrets, tokens, or PII.

### Naming and structure

- File naming: <TO FILL: kebab-case / camelCase / snake_case / PascalCase for components>
- One responsibility per file.
- Tests live in <TO FILL: location pattern>.

### Async control flow

- No `await` inside `for` loops. Use `Promise.all`, batching helpers, or streaming instead.

### What NOT to do

- Do not add features beyond the spec.
- Do not create abstractions for one-time use.
- Do not validate scenarios that cannot occur (trust framework guarantees and internal callers).
- Do not write comments that restate what the code does — only comments that explain non-obvious *why*.
- Do not create README/docs files unless the user asks.
=== TEMPLATE END ===

## Variants for "Loose" typing

If the user picks `Loose` typing in Round 1.3, replace the bullets of the `### Typing rules` section with:

- The `any` type (or equivalent) is allowed only at boundaries that are explicitly typed at the next layer. No inline lint disables.
- All identifiers, comments, and strings are written in English regardless of conversation language.

## Variants for "Not applicable" typing

If the user picks `Not applicable`, drop the entire `### Typing rules` section.

## Rules

1. **Do NOT** run any command from `package.json#scripts` or other manifests during detection. Read files only.
2. **Do NOT** invent values. If a detection signal is missing, ask the user.
3. **Do NOT** add a section that the user did not request.
4. **Do NOT** modify any file other than `CLAUDE.md`.
5. Detection runs once at Step 2. If `CLAUDE.md` resolution fails midway, abort with a clear error message rather than partial writes.
6. The whole flow must complete in 1 to 3 `AskUserQuestion` calls. Do not chain extra confirmation questions.
