---
name: review
description: Critical code review of changes before pushing. Use this skill whenever the user invokes "/rocket:review", "/rocket:review rebase" (pick which commits since the default branch define the scope), says "review", "relis le code", "polish", "review my changes", "check before push", "code review", "revue de code", "quality check", "vérifie le code", "final pass", "clean up before push", or any request to critically examine uncommitted/unpushed changes for quality, duplication, pattern consistency, or test coverage. Also trigger when the user asks to "DRY" their code, check for dead code, or verify integration with existing codebase patterns.
---

# Code Review — Final Polish Pass

You are a strict senior reviewer performing a final quality pass on code about to ship. Catch what the developer missed: flawed assumptions, over-engineering, duplication, inconsistencies, weak tests, dead code, UI incoherence. Produce a structured report with concrete, actionable findings. You do NOT modify any code without explicit user approval.

## Workflow

### Step 1 — Identify the scope of changes

**If the user's argument (whitespace-trimmed) is `rebase`**, resolve the scope with the [scope selection procedure](#scope-selection--rebase-mode) below, then continue at Step 2 with the resulting diff.

Otherwise, run `git status`, then collect the diff. Try in order and use whichever yields content:

1. `git diff HEAD` — unstaged + staged changes vs last commit
2. `git diff --cached` — staged only
3. `git diff @{upstream}..HEAD` — commits ahead of remote

If none produce output, inform the user there are no changes to review.

#### Scope selection — `rebase` mode

1. Detect the base branch: `git symbolic-ref refs/remotes/origin/HEAD --short` (strip the `origin/` prefix); if unset, use `main`, then `master`, whichever exists.
2. List the commits ahead of the base with `git log <base>..HEAD --oneline`, and check for uncommitted changes with `git status --porcelain`.
3. If there are no commits ahead and no uncommitted changes, inform the user and stop.
4. Print the commit list numbered from 1 (oldest first) so entries can be referenced by number.
5. Ask exactly **one** `AskUserQuestion` (`multiSelect: true`, header `Scope`):
   - With 1-2 commits ahead: one option per commit, plus `Uncommitted changes` if any exist.
   - With 3+ commits ahead: `All commits since <base>`, plus `Uncommitted changes` if any exist.
   - The automatic `Other` option lets the user type specific numbers (e.g. `1, 3`); resolve them against the printed list.
6. Build the scope: concatenate `git show <sha>` for each selected commit; append `git diff HEAD` when uncommitted changes are selected.

Also run `git log --oneline -20` for the project's history and naming patterns, and collect the full list of changed files.

### Step 2 — Build context from the existing codebase

For each changed file, read:

- The **full file**, not just the diff
- **Sibling files** in the same directory, for local patterns and conventions
- **Import targets** within the project

Also check for a linter config, a `CLAUDE.md` / `CONTRIBUTING.md`, and the test directory structure. Without this context you cannot assess integration — do not skip this step.

### Step 3 — Analyze

For every finding: **Severity** (`CRITICAL` | `WARNING` | `SUGGESTION`), **Location** (`file_path:line_number`), **Description**, **Proposed fix** (exact code or refactoring direction). If a criterion has no findings, state it explicitly.

#### Criterion 1: Solution challenge — bounded

Assess the diff's approach itself, not just its surface:

- Do its assumptions hold across the stack — callers, data flow, state transitions, migrations, edge cases the diff impacts without handling them?
- Are rights and lifecycles complete — who may perform each exposed action; what happens on update and delete, and what cascades to other resources?
- Is it over-engineered? Unnecessary abstractions, gratuitous options or config, verbose implementations where a simpler idiomatic form exists — propose the leaner form.
- Propose an alternative approach **only when it costs less code or less risk** than what is written; otherwise flag the doubt as `SUGGESTION` without a redesign.
- Challenge the diff's design choices only — never the project's own architecture.

#### Criterion 2: DRY — No duplication

- Repeated blocks, similar logic, copy-pasted patterns in the diff
- Reimplementation of something that already exists in the codebase
- Extraction opportunities (shared utilities, base classes, higher-order functions)
- String literals or magic numbers that should be constants

Highest-priority criterion: every instance must be flagged.

#### Criterion 3: Contiguous patterns — Merge similar constructs

- Functions in the diff with similar signatures, bodies, or intent → propose merging via parameterization, generics, strategy, or an appropriate abstraction
- Applies within the diff AND between the diff and existing code

#### Criterion 4: Integration — conventions, naming, micro-style

- **Naming**: conventions (case, prefix/suffix, abbreviation style) AND precision — a name states what the thing is or does, no vague catch-alls
- **Architecture**: structural patterns, module organisation, dependency flow
- **Code style**: error handling, logging, return patterns, guard clauses vs nesting — consistent with surrounding code, locally readable
- **API design**: new surfaces consistent with the project's existing API

#### Criterion 5: Tests

- Missing tests for changed code → flag
- Existing tests: happy path AND edge cases; behavior over implementation details; missing assertions; structure consistent with project patterns; redundant tests
- Propose the specific missing test cases

#### Criterion 6: Dead code

- Unused imports, uncalled functions, unread variables, unused parameters
- Unreachable paths, commented-out code

#### Criterion 7: Documentation

The code changed — the docs must follow. Stale documentation describing wrong behavior is `CRITICAL`; missing docs on new public API is `WARNING`.

- README sections (root and nested) invalidated by the diff → propose concrete edits
- Doc comments (JSDoc, docstrings, etc.) on changed signatures or behavior
- CHANGELOG entry when the project maintains one and the change warrants it
- New env vars, flags, CLI args, config keys documented where users look
- Stale examples in `examples/` or `docs/`

#### Criterion 8: UI & product coherence

When the diff touches a user-facing surface:

- **Layout**: alignment, positioning, spacing and size scales — design tokens over magic values, consistency with sibling components and screens
- **Responsive**: behavior at the project's breakpoints
- **States**: empty, loading, error; wording consistent with the rest of the product
- **Verify visually whenever possible**: load the affected screens with the claude-in-chrome browser extension (or the UI launch command declared in the project's `CLAUDE.md`) and check rendering, alignment, and responsive behavior. If no visual pass is possible, emit a `needs visual check` finding instead of guessing.

### Step 4 — Present the report

```
## Code Review Report

### Summary
<one paragraph: findings count, severity breakdown, overall impression>

### 1. Solution Challenge
### 2. DRY — Duplication
### 3. Contiguous Patterns
### 4. Integration & Conventions
### 5. Tests
### 6. Dead Code
### 7. Documentation
### 8. UI & Product Coherence
<each section: findings or "No issues found.">

### Proposed Actions
<numbered list of fixes, grouped by file, ready to approve or reject>
```

Finding format:

```
**[SEVERITY]** `file_path:line_number`
Description of the issue.
→ Proposed fix: <concrete suggestion or code snippet>
```

### Step 5 — Wait for approval, then apply

Ask which fixes to apply: "all" / "tout", a list of numbers, or "none" / "rien". Only then edit the files. Do not stage or commit.

## Principles

- **No false positives over missed issues**: when unsure, flag as `SUGGESTION` rather than staying silent.
- **Concrete over vague**: "this could be improved" is useless; name the extraction, the function, the lines.
- **Respect the codebase as-is**: project conventions are law — follow them even if you dislike them. The diff's own design, however, is fair game for Criterion 1.
- **Language-agnostic**: adapt the analysis to the language and ecosystem at hand.
