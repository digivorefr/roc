---
name: setup
disable-model-invocation: true
description: Initialize or update the project's CLAUDE.md with the conventions block consumed by rocket:spec-maker and rocket:spec-writer. Reads any existing CLAUDE.md to detect language, tone, and overlapping sections, then asks the user how to integrate before writing. Auto-detects stack signals from manifests and from the existing CLAUDE.md prose. Manual-only — invoked by the user via "/rocket:setup".
---

# Project conventions setup

The user wants to add (or refresh) a project conventions block in this project's `CLAUDE.md`. That block is read by `rocket:spec-maker` and `rocket:spec-writer` to follow project-specific stack rules.

The skill must integrate the block **harmoniously** into whatever exists already: matching language, tone, heading depth, and avoiding content duplication. Drive an interactive flow that surfaces every integration decision to the user before writing.

## Workflow

### Step 1 — Analyze existing CLAUDE.md

If `CLAUDE.md` does not exist at the repo root: skip to Step 2 with `existing = none`.

If it exists, **read the full file content** (not just one heading) and produce an internal analysis:

1. **Language** — the dominant language of the prose (FR / EN / other). Judge from the body, not from code blocks or headings alone.
2. **Heading structure** — list every `#`, `##`, `###` heading with its line number and depth. Note the deepest level used.
3. **Tone signals** — capture the prevailing voice, sentence length, and bullet density. See [Style adaptation guidelines](#style-adaptation-guidelines).
4. **Overlapping sections** — for every existing `##`/`###` section, judge semantically whether it covers the same ground as one of the template sections (Stack, Verification command, Typing rules, Error handling, Logging & observability, Naming and structure, Async control flow, What NOT to do). A section overlaps if a reasonable reader would expect to find that information in either place. Use semantic judgment, not keyword matching: `## Tests` and `## Quality gate` and `## How to validate` all overlap with "Verification command".
5. **Already-declared conventions** — extract any value the existing prose already states: test commands inside backtick blocks, package manager names mentioned, logger libraries cited, "no `any`" or similar typing rules. These will become Recommended values in Round 1.
6. **Existing instance of our block** — check for `## Project conventions` (new format) or `## Project conventions (read by` (legacy format from older skill versions).

Do not reveal the analysis to the user yet. Hold it for Step 3.

### Step 2 — Auto-detect signals from manifests

Read these in parallel. Do not run any command.

- `package.json` — language is JS/TS, capture `name`, `packageManager`, `engines.node`, key dependencies (`next`, `react`, `express`, `nestjs`, `fastify`, `vue`...)
- `pyproject.toml` — language is Python, capture `project.name`, `requires-python`, `[tool.poetry]` / `[tool.uv]` markers
- `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json` — capture language and version if present
- Lockfiles — `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`, `uv.lock`, `poetry.lock`, `Pipfile.lock` — infer the package manager
- `package.json#scripts.check`, `scripts.test`, `scripts.lint` — candidates for the verification command
- `pyproject.toml` task runners (`[tool.poe.tasks]`, `[tool.taskipy.tasks]`) — same
- `Makefile` — candidates if a `check` or `test` target exists

Merge these with the conventions extracted from the existing CLAUDE.md prose (Step 1.5). Manifests win on objective facts (package manager from lockfile); CLAUDE.md prose wins when it explicitly contradicts a manifest hint (the user's intent overrides the toolchain).

### Step 3 — Integration plan

Skip this step entirely if **all** of the following are true: no existing CLAUDE.md, OR (existing CLAUDE.md has no overlapping sections AND no instance of our block AND its language is unambiguously English).

Otherwise, run **one** `AskUserQuestion` call with up to 4 questions:

1. **`Output language`** — present the detected language as `(Recommended)`, plus `English`, `French` (skip whichever is the recommended one), and `Other` (auto). Phrase: "Render the conventions block in which language?"
2. **`Existing block`** (only if our block was detected at Step 1.6) — `Replace (Recommended)` / `Merge into existing` / `Keep both side by side` / `Skip — leave existing alone`.
3. **For each overlapping section detected at Step 1.4** (up to 2 in this call to leave room for Q1 and Q2) — phrase: "Existing `## <heading>` overlaps with our `<our-section>`. What should we do?". Options: `Merge content (Recommended)` / `Replace existing with ours` / `Keep both` / `Skip ours — keep existing only`.

If more than 2 overlapping sections were detected, run a **second** `AskUserQuestion` call right after the first to cover the rest. Group up to 4 overlap questions per call. Stop calling once all overlaps are addressed.

If the user picks `Skip` for the existing-block question, abort the skill with a one-line message.

If the user picks `Skip ours` for every overlap and there is no non-overlapping section to add, abort with: "All sections of the conventions block are already covered by your existing CLAUDE.md. Nothing to add."

### Step 4 — Round 1 essentials

One `AskUserQuestion` call with 4 questions. For each detected value, put it as the first option labelled `(Recommended)`. The free-text "Other" option is added automatically by the tool — do not add it manually.

1. **`Stack summary`** — present the detected language + framework as Recommended. Two-three alternatives covering common stacks.
2. **`Verify cmd`** — present detected `check`/`test` script(s) as Recommended. If multiple were detected, list each as a separate option (max 4).
3. **`Typing rules`** — `Strict (Recommended)` / `Loose` / `Not applicable` (untyped language).
4. **`Optional sections`** — `multiSelect: true`. Options: `Logging & observability` / `Error handling philosophy` / `Naming and structure` / `Async control flow`.

Mandatory sections (Stack, Verification command, What NOT to do) are always written and not listed in question 4. Sections marked `Skip ours` at Step 3 are dropped here too.

### Step 5 — Round 2 conditional

For each section the user ticked in Round 1.4 AND that was not marked `Skip ours` at Step 3, ask the corresponding question. Batch in one `AskUserQuestion` call (up to 4 questions). Skip the entire step if no questions accumulate.

- **Logging & observability** — `Logger`: ask for the logger library or wrapper file path. Use the value extracted from existing CLAUDE.md (Step 1.5) as Recommended if available.
- **Error handling philosophy** — `Error policy`: `Standard (Recommended)` (default rules) / `Custom` (user provides their own).
- **Naming and structure** — two questions: `File naming` (kebab/camel/snake/Pascal — pick stack-appropriate as Recommended) and `Tests location`.
- **Async control flow** — `Async rules`: `Standard (Recommended)` ("No `await` inside `for` loops...") / `Custom`.

If more than 4 questions accumulate, split into two calls.

### Step 6 — Compose and translate

Internal composition is in English using the [Template](#template) below. Then:

1. **Substitute placeholders** — replace every `<TO FILL: ...>` with the chosen answer or detected value.
2. **Drop sections** — remove `### <section>` blocks that the user did not select at Round 1.4 OR that were marked `Skip ours` at Step 3.
3. **Apply Loose / Not applicable typing variants** — see [Typing rule variants](#typing-rule-variants).
4. **Translate** — if the target language from Step 3 is not English, translate the entire block: prose, headings, bullets. Keep code blocks, file paths, command lines, and proper nouns untranslated. See [Section translation hints](#section-translation-hints) for canonical heading translations.
5. **Adapt tone** — match the existing CLAUDE.md's voice per [Style adaptation guidelines](#style-adaptation-guidelines). If no existing CLAUDE.md, use a terse imperative voice as default.
6. **Apply merges** — for any overlapping section marked `Merge content`, write a merged version that keeps the existing content's wording and adds the missing facts from our template, in the existing language and tone.

### Step 7 — Preview and confirm

Compute the unified diff of what will change in `CLAUDE.md`:

- For new files: a creation diff showing the full new file content.
- For existing files: a unified diff (3 lines of context) showing additions, replacements, and deletions across the file.

Show the diff to the user wrapped in a fenced ```` ```diff ```` block, then run **one** `AskUserQuestion` call with a single question:

- **`Apply changes`** — `Apply (Recommended)` / `Adjust — let me describe what to change` / `Cancel`.

If `Adjust`: ask the user (free-text via the auto-Other) what to change, regenerate the block per their notes, show the new diff, ask again. Cap at 3 adjustment loops to prevent runaway.

If `Cancel`: exit without writing.

### Step 8 — Write

Apply the changes the user approved. Insertion logic:

- **No `CLAUDE.md`** — create it with `# <project-name>` (from `package.json#name` / `pyproject.toml#project.name` / cwd directory name as fallback), one blank line, then the rendered block.
- **Existing block detected, action `Replace`** — replace from the heading line of `## Project conventions` (or legacy `## Project conventions (read by`) up to the next `##` heading or EOF.
- **Existing block detected, action `Merge into existing`** — replace as above with the merged content.
- **Existing block detected, action `Keep both`** — insert the new block right after the existing one with one blank line separator.
- **Per-section overlap actions** — apply each independently at the location of the existing overlapping section.
- **No overlap, no existing block** — pick the insertion point per [Insertion point rules](#insertion-point-rules).

### Step 9 — Summary

Output a short summary, under 12 lines, no emojis:

- Path written.
- Action taken (created / updated / merged).
- Output language used.
- Sections included, sections skipped (with why).
- Overlap resolutions applied.
- Detected values that were accepted as-is.
- Any `<TO FILL: ...>` placeholder still in the file that the user should review manually.

## Style adaptation guidelines

When an existing CLAUDE.md is present, the rendered block must blend in. Detect and match:

- **Voice**: imperative ("Use X."), second person ("You should use X."), or declarative ("X is used."). Extract the dominant pattern from the existing prose's H2 sections and match it. If absent, default to imperative.
- **Sentence length**: count average words per sentence in the existing prose. Match within ±25%. Existing terse → keep ours terse. Existing verbose → allow more elaboration.
- **Bullet density**: existing short bullets (5-12 words) → keep ours short. Existing long bullets (20+ words) → allow ours to be richer.
- **Heading case**: title case (`Verification Command`) vs sentence case (`Verification command`). Match the existing convention.
- **Technical density**: if the existing prose is plain-language and avoids jargon, soften ours. If it is dense and technical, keep ours dense.
- **Typography**: detect dashes (`-` vs `—`), quote style (`"` vs `“`), spacing around colons. Match.

If multiple signals disagree (e.g. some sections are imperative, others declarative), pick whichever is dominant in **content** sections (Tests, Stack, Conventions) rather than in **meta** sections (Contributing, License, Credits). When in doubt, ask: "Which voice should I match?" via a brief `AskUserQuestion` — but only if the disagreement is genuine, not for minor variation.

## Section translation hints

Canonical heading translations (composed in English internally; rendered in the target language):

| English                       | French                              |
| :---------------------------- | :---------------------------------- |
| Project conventions           | Conventions du projet               |
| Stack                         | Stack                               |
| Verification command          | Commande de vérification            |
| Typing rules                  | Règles de typage                    |
| Error handling philosophy     | Gestion des erreurs                 |
| Logging & observability       | Logging & observabilité             |
| Naming and structure          | Nommage et structure                |
| Async control flow            | Asynchrone et concurrence           |
| What NOT to do                | Ce qu'il ne faut PAS faire          |

For other languages, translate naturally — do not transliterate. Code blocks, file paths, command lines, library names, and proper nouns stay in their original form.

## Insertion point rules

Used at Step 8 when there is no existing block and no per-section overlap to honor.

1. Look for a "metadata" `##` section near the end of the file. Match by semantic intent (any language): License / Licence, References / Références, See also / Voir aussi, Contributing / Contribution, Credits / Crédits, Acknowledgments / Remerciements, Authors / Auteurs.
2. If found within the last 5 H2 sections of the file → insert the new block **before** the first such section, with a blank line separator on each side.
3. Otherwise → append at the end of the file with a blank line separator before it.

## Template

The text between `=== TEMPLATE START ===` and `=== TEMPLATE END ===` is the literal English block to compose internally. Substitute every `<TO FILL: ...>` placeholder. Triple backticks inside the template are part of the output. Translate at Step 6 if the target language is not English.

=== TEMPLATE START ===
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
=== TEMPLATE END ===

## Typing rule variants

If the user picks `Loose` typing in Round 1.3, replace the bullets of `### Typing rules` with:

- The `any` type (or equivalent) is allowed only at boundaries that are explicitly typed at the next layer. No inline lint disables.
- All identifiers, comments, and strings are written in English regardless of conversation language.

If the user picks `Not applicable`, drop the entire `### Typing rules` section.

## Rules

1. **Do NOT** run any command from `package.json#scripts` or other manifests during detection. Read files only.
2. **Do NOT** invent values. If a detection signal is missing, ask the user.
3. **Do NOT** add a section that the user did not request, or that was marked `Skip ours` at Step 3.
4. **Do NOT** modify any file other than `CLAUDE.md`.
5. **Do NOT** write to `CLAUDE.md` before the user has approved the diff at Step 7.
6. The whole flow should complete in 2 to 4 `AskUserQuestion` calls for typical cases. Do not chain unnecessary confirmations.
7. If `CLAUDE.md` resolution fails midway (file becomes unreadable, parsing breaks), abort with a clear error message rather than partial writes.
