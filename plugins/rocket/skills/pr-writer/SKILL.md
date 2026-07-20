---
name: pr-writer
description: Generate a structured, English, product-focused PR description organised by topic. Use this skill whenever the user invokes "/rocket:pr-writer", "/rocket:pr-writer rebase" (pick which commits since the default branch define the scope), asks for a pull request description, a PR summary, a PR body, says "write a PR description", "rédige une description de PR", "prépare un descriptif de PR", "PR body", "pull request body", or any similar request. The skill scans the current git changes, the selected commits, or accepts context provided by the user.
---

# PR Description Writer

Produce a **structured, English, product-focused** PR description organised by topic. The reviewer must understand what problem each change solves and how, in under a minute.

## Output contract

- **Format**: a single markdown code block, ready to paste into a GitHub PR body. No preamble, no commentary around it.
- **Language**: English. Product-first for context and intent, technical for changes.
- **Budget**: 1-2 topics for a typical PR; more only when the PR genuinely ships independent features. Whole description ≤ **15 lines** including blanks. When in doubt, merge topics.
- **Headings**: only `### <Topic>`, one per topic — a short noun phrase (4-7 words) naming the area or behaviour.
- **Block shape**: three parts separated by single blank lines — context sentence, intent bullet(s), change bullet(s). No labels; the reader infers from position.

## Topic block shape

```
### <Topic>
<context sentence>

- <intent bullet>

- <change bullet>
```

- **Context** — one sentence: what was happening, to whom, why it mattered. Product framing; no file paths, symbols, or library names.
- **Intent** — one bullet: the decision in product/operator terms. A second only if dropping it loses a reviewer-relevant decision.
- **Change** — one dense bullet naming the mechanism: merge related facts with parentheses instead of adding bullets. A second only if dropping it loses a reviewer-relevant mechanism. Module-level concepts allowed ("the webhook handler"); file paths not.

## Hard rules

- Density beats enumeration: one dense bullet over two sparse ones.
- No "Test plan", ever. No emojis. No heading other than `### <Topic>`, no labels like `**Context:**`.
- No file-by-file changelog; skip incidental edits (typos, formatting, irrelevant bumps).
- No "Out of scope / follow-ups" unless explicitly asked.
- One topic per independent concern: never merge unrelated changes, never split one concern. Two changes belong together if removing one forces reworking the other.

## Workflow

### Step 1 — Gather context

**Case A — the argument is `rebase`**: resolve the scope with the [scope selection procedure](#scope-selection--rebase-mode) below, then continue at Step 2 with the resulting diff.

**Case B — context provided by the user** (a diff, a description, a spec, previous session content): use it directly. Do NOT run git commands.

**Case C — no argument, no context**: run in order, use whichever yields content:

1. `git diff HEAD` (staged + unstaged vs HEAD)
2. `git diff --cached` (staged only)
3. `git diff @{upstream}..HEAD` (commits ahead of remote)

Also run `git log --oneline @{upstream}..HEAD 2>/dev/null || git log --oneline -5` for commit context. If nothing yields output, tell the user no changes are detected and ask for context.

### Scope selection — `rebase` mode

1. Detect the base branch: `git symbolic-ref refs/remotes/origin/HEAD --short` (strip the `origin/` prefix); if unset, use `main`, then `master`, whichever exists.
2. List the commits ahead of the base with `git log <base>..HEAD --oneline`, and check for uncommitted changes with `git status --porcelain`.
3. If there are no commits ahead and no uncommitted changes, inform the user and stop.
4. Print the commit list numbered from 1 (oldest first) so entries can be referenced by number.
5. Ask exactly **one** `AskUserQuestion` (`multiSelect: true`, header `Scope`):
   - With 1-2 commits ahead: one option per commit, plus `Uncommitted changes` if any exist.
   - With 3+ commits ahead: `All commits since <base>`, plus `Uncommitted changes` if any exist.
   - The automatic `Other` option lets the user type specific numbers (e.g. `1, 3`); resolve them against the printed list.
6. Build the scope: concatenate `git show <sha>` for each selected commit; append `git diff HEAD` when uncommitted changes are selected.

### Step 2 — Write

1. Group the changes into topics, one per independent concern.
2. For each topic: context sentence, intent bullet, change bullet — per the contract above.
3. If the product angle of a topic is genuinely unclear, ask one short question instead of inventing a framing. For a pure refactor, describe what moved and why the new structure is better.
4. Return **only** the markdown code block.

## Good example

````md
```md
### Read depth for nested relations

Read endpoints capped expansion at depth 1, forcing extra calls to resolve nested resources.

- Nested relations come back populated in a single call

- Raised `maximumDepth` per route (2-4 depending on the resource), tests aligned

### Per-request overrides in the Postman collection

Overriding one request's id meant editing a shared collection variable, impacting every request.

- Any request can target a different id without touching shared variables

- Path segments use Postman path variables, each defaulting to the matching collection variable
```
````

(The outer fences make the example readable here; the actual output is a single ```md...``` block.)

## Bad examples (do not produce these)

- Two or three sparse bullets where one dense bullet carries the facts.
- A `## Summary` heading, labels like `**Context:**`, or a "Test plan" section.
- A context sentence or intent bullet naming file paths, function names, or library specifics.
- An intent bullet like `Refactored X to use Y` — that is a change, not an intent.
- Padding a block to look thorough: if one bullet covers it, ship one.
