---
name: setup
disable-model-invocation: true
description: Initialize or update the project's CLAUDE.md with the conventions block consumed by rocket:spec-maker and rocket:spec-writer. Detects the stack from manifests, lockfiles, CI workflows, and lint configs, composes the complete block, and asks for a single confirmation before writing. Safe to re-run anytime — only the marker-delimited block is ever touched. Manual-only — invoked by the user via "/rocket:setup".
---

# Project conventions setup

Write (or refresh) the `## Project conventions` block in this project's `CLAUDE.md`. The block is read by `rocket:spec-maker` and `rocket:spec-writer` so they follow project-specific stack rules instead of hunting for them.

Philosophy: **detect everything detectable, compose the complete result, show one diff, ask once.** The user's time is spent approving, not answering a questionnaire.

## Managed region

The block is delimited by literal markers:

```
<!-- rocket:conventions:start -->
...block content...
<!-- rocket:conventions:end -->
```

- The skill only ever writes between the markers (plus inserting the marker pair on first run).
- Everything outside the markers is never modified — re-running can never destroy user content.
- Re-running with unchanged detection results is a no-op: report "already up to date" and stop.

## Workflow

### Step 1 — Detect

Read files only. **Never execute a project command.** Collect in parallel reads:

1. **Manifests** — `package.json` (name, `packageManager`, `engines`, key dependencies), `pyproject.toml`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json` → language, runtime, framework.
2. **Lockfiles** — `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`, `uv.lock`, `poetry.lock` → package manager.
3. **CI workflows** — `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`: extract the lint/type/test commands CI actually runs. This is the **highest-authority source** for the verification command — a command CI runs outranks a guessed script name.
4. **Manifest scripts and Makefile targets** (`check`, `test`, `lint`, `typecheck`) — fallback candidates for the verification command.
5. **Lint/format/type configs** — `.eslintrc*`, `biome.json`, `.prettierrc`, `ruff.toml`, `mypy.ini`, `tsconfig.json` strictness flags → typing rules and lint posture.
6. **Monorepo signals** — `workspaces` globs, `pnpm-workspace.yaml`, `turbo.json`, `nx.json` → whether the verification command runs at the root or per package.
7. **Existing `CLAUDE.md`** — dominant prose language, voice and heading case (see [Style adaptation](#style-adaptation-guidelines)), an existing managed region (markers) or a legacy `## Project conventions` block (no markers), and any conventions already stated in prose (test commands in backticks, logger names, typing rules). Prose statements rank just below CI as a source: the user wrote them deliberately.

Record the **source of every detected value** — it is shown in the preview.

### Step 2 — Compose

Build the complete block from the [Template](#template):

1. Substitute every `<TO FILL: ...>` placeholder with the detected value.
2. **Mandatory sections**, always present: `Stack`, `Verification command`, `What NOT to do`. `Typing rules` is included for typed languages (strict variant by default; loose variant only when the existing CLAUDE.md or lint config says so — see [Typing rule variants](#typing-rule-variants)) and dropped for untyped ones.
3. **Optional sections** (`Error handling philosophy`, `Logging & observability`, `Naming and structure`, `Async control flow`) are included **only when detection found a real signal** — a logger library in the dependencies, an established file-naming pattern, an async-heavy stack. No signal → omitted; the user can request them via the Adjust loop.
4. Render in the dominant language of the existing CLAUDE.md (translate headings per [Section translation hints](#section-translation-hints)); match its voice, heading case, and bullet density. Default with no existing file: English, terse imperative.
5. **Preserve user edits**: if a managed region or legacy block exists and one of its lines conflicts with a freshly detected value, keep the user's line and list the conflict in the Step 5 summary. Detection refreshes facts; it does not overrule deliberate choices.

### Step 3 — Confirm (single round)

Show, in this order:

1. The unified diff of `CLAUDE.md` (creation diff if the file is absent; diff limited to the managed region otherwise), wrapped in a ```` ```diff ```` block.
2. One line per detected value with its source, e.g. `verification command: yarn check — from .github/workflows/ci.yml`.

Then ask exactly **one** `AskUserQuestion` call:

- **`Apply changes`** — `Apply (Recommended)` / `Adjust — describe what to change` / `Cancel`.
- Add to the **same call** one question per essential value that could not be detected (typically the verification command) — max 4 questions total. Never ask about a value that was detected: it is visible in the diff and fixable via `Adjust`.
- Answers collected in this round are substituted into the block before the Step 4 write; no second preview is needed unless the user picked `Adjust`.

If `Adjust`: regenerate per the user's notes, show the new diff, ask again. Cap at 3 loops.
If `Cancel`: exit without writing anything.

### Step 4 — Write

One write, no partial states:

- **No `CLAUDE.md`** — create it: `# <project-name>` (from the manifest, else the directory name), blank line, the marked block.
- **Markers present** — replace strictly between `<!-- rocket:conventions:start -->` and `<!-- rocket:conventions:end -->`.
- **Legacy block, no markers** — replace from the `## Project conventions` heading to the next `##` heading or EOF with the marked block.
- **Neither** — insert the marked block per the [Insertion point rules](#insertion-point-rules).

If the write fails midway, abort with a clear error; never leave a half-updated file.

### Step 5 — Summary

Under 10 lines, no emojis: path written; action (created / updated / no-op); output language; sections included and omitted (with why); each detected value with its source; user lines preserved over detection; any `<TO FILL: ...>` placeholder remaining for manual review.

## Rules

1. **Do NOT** execute any project command during detection. Read files only.
2. **Do NOT** invent values. Undetectable essentials are asked in the single Step 3 round; anything else stays as a `<TO FILL: ...>` placeholder flagged in the summary.
3. **Do NOT** modify anything outside the managed region (except creating the file and inserting the marker pair on first run).
4. **Do NOT** write before the user has approved the diff.
5. The nominal flow costs exactly **one** `AskUserQuestion` call.

## Template

The text between `=== TEMPLATE START ===` and `=== TEMPLATE END ===` is the literal English block to compose internally, markers included. Substitute every `<TO FILL: ...>` placeholder. Triple backticks inside the template are part of the output. Translate at Step 2.4 if the target language is not English.

=== TEMPLATE START ===
<!-- rocket:conventions:start -->
## Project conventions

<!-- Read by rocket:spec-maker, rocket:spec-writer -->

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
<!-- rocket:conventions:end -->
=== TEMPLATE END ===

## Typing rule variants

Loose variant (when the existing CLAUDE.md or the lint config explicitly allows `any`-like escapes):

- The `any` type (or equivalent) is allowed only at boundaries that are explicitly typed at the next layer. No inline lint disables.
- All identifiers, comments, and strings are written in English regardless of conversation language.

Untyped language: drop the entire `### Typing rules` section.

## Style adaptation guidelines

When an existing CLAUDE.md is present, the rendered block must blend in. Detect and match:

- **Voice**: imperative ("Use X."), second person ("You should use X."), or declarative ("X is used."). Match the dominant pattern of the existing content sections; default to imperative.
- **Sentence length and bullet density**: terse stays terse, verbose may elaborate. Match within reason.
- **Heading case**: title case (`Verification Command`) vs sentence case (`Verification command`). Match the existing convention.
- **Typography**: dashes (`-` vs `—`), quote style, spacing around colons. Match.

If signals disagree, follow the dominant pattern of **content** sections (Stack, Tests, Conventions) rather than **meta** sections (License, Contributing).

## Section translation hints

Composed in English internally; rendered in the target language. Code blocks, file paths, command lines, library names, and proper nouns stay untranslated.

| English                   | French                     |
| :------------------------ | :------------------------- |
| Project conventions       | Conventions du projet      |
| Stack                     | Stack                      |
| Verification command      | Commande de vérification   |
| Typing rules              | Règles de typage           |
| Error handling philosophy | Gestion des erreurs        |
| Logging & observability   | Logging & observabilité    |
| Naming and structure      | Nommage et structure       |
| Async control flow        | Asynchrone et concurrence  |
| What NOT to do            | Ce qu'il ne faut PAS faire |

For other languages, translate naturally — do not transliterate. The marker comments stay in English verbatim.

## Insertion point rules

Used at Step 4 when the file exists with neither markers nor a legacy block:

1. Look for a "metadata" `##` section near the end of the file (semantic match, any language: License, References, See also, Contributing, Credits, Acknowledgments, Authors).
2. If found within the last 5 H2 sections → insert the marked block **before** the first such section, with a blank line on each side.
3. Otherwise → append at the end of the file with a blank line before it.
