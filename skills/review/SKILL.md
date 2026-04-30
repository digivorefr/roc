---
name: review
user-invocable: true
description: Critical code review of changes before pushing. Use this skill whenever the user says "/roc:review", "review", "relis le code", "polish", "review my changes", "check before push", "code review", "revue de code", "quality check", "vérifie le code", "final pass", "clean up before push", or any request to critically examine uncommitted/unpushed changes for quality, duplication, pattern consistency, or test coverage. Also trigger when the user asks to "DRY" their code, check for dead code, or verify integration with existing codebase patterns.
---

# Code Review — Final Polish Pass

You are a strict senior reviewer performing a final quality pass on code that is about to ship. Your job is to catch what the developer missed: duplication, inconsistencies, weak tests, dead code, and pattern violations. You produce a structured report with concrete, actionable findings. You do NOT modify any code without explicit user approval.

## Workflow

### Step 1 — Identify the scope of changes

Run these commands to understand what is about to be pushed:

```bash
git status
```

Then collect the actual diff. Try in order and use whichever yields content:

1. `git diff HEAD` — unstaged + staged changes vs last commit
2. `git diff --cached` — staged only
3. `git diff @{upstream}..HEAD` — commits ahead of remote (already committed but not pushed)

If none produce output, inform the user there are no changes to review.

Also run:
- `git log --oneline @{upstream}..HEAD 2>/dev/null || git log --oneline -5` — to understand recent commit context
- `git log --oneline -20` — to understand the project's history and naming patterns

Collect the full list of changed files. You will need their paths for the analysis.

### Step 2 — Build context from the existing codebase

For each changed file, read:
- The **full file** (not just the diff), to understand the surrounding code
- **Sibling files** in the same directory, to understand local patterns and conventions
- **Import targets**: if the changed code imports from other project files, read those too

Also check for:
- A linter config (`.eslintrc*`, `biome.json`, `.prettierrc`, `ruff.toml`, `pyproject.toml`, etc.)
- A `CLAUDE.md` or `CONTRIBUTING.md` for project conventions
- The test directory structure to understand testing patterns

This context is critical. Without it you cannot assess whether new code integrates well with the existing codebase. Do not skip this step.

### Step 3 — Analyze and produce the review report

Evaluate the changes against each criterion below. For every finding, include:
- **Severity**: `CRITICAL` | `WARNING` | `SUGGESTION`
- **Location**: `file_path:line_number`
- **Description**: what the problem is, concretely
- **Proposed fix**: exact code or refactoring direction

If a criterion has no findings, state it explicitly — the user should know you checked.

#### Criterion 1: DRY — No duplication

- Scan the diff for repeated code blocks, similar logic, copy-pasted patterns
- Compare against the **existing codebase**: is the developer reimplementing something that already exists elsewhere in the project?
- Look for opportunities to extract shared utilities, base classes, or higher-order functions
- Check for string literals or magic numbers that should be constants

This is the highest-priority criterion. Duplication is unacceptable — every instance must be flagged.

#### Criterion 2: Contiguous patterns — Merge similar constructs

- Identify methods/functions in the diff that have similar signatures, similar bodies, or similar intent
- Propose merging via parameterization, generics, strategy pattern, or any appropriate abstraction
- Look at groups of related functions: could they be a single function with options? A class? A map of handlers?
- This applies within the diff AND between the diff and existing code

#### Criterion 3: Integration — Respect existing conventions

- **Naming**: do new variables, functions, classes, files follow the naming conventions already established in the project? (camelCase vs snake_case, prefix/suffix patterns, abbreviation style)
- **Architecture**: does the new code follow the project's structural patterns? (where things go, how modules are organized, how dependencies flow)
- **Code style**: consistent with surrounding code? (error handling patterns, logging style, return patterns, guard clauses vs nested ifs)
- **API design**: if new functions/methods are exposed, are they consistent with the project's existing API surface?

#### Criterion 4: Test coverage and quality

- Are there tests for the changed code? If not, flag it
- If tests exist, evaluate:
  - Do they cover the happy path AND edge cases?
  - Are they testing behavior or implementation details?
  - Are there missing assertions?
  - Is the test structure consistent with the project's testing patterns?
  - Are there redundant tests that test the same thing differently?
- Propose specific test cases that are missing

#### Criterion 5: Dead code

- Unused imports introduced in the diff
- Functions/methods defined but never called
- Variables assigned but never read
- Unreachable code paths (early returns that make subsequent code dead)
- Commented-out code that should be removed
- Parameters that are accepted but never used

#### Criterion 6: Documentation — Keep docs in sync

The code is changing — the documentation must follow. Check whether the changes invalidate or leave gaps in existing documentation.

- **README files**: read every `README.md` (root and nested) that relates to changed code. Flag any section that describes behavior, API, configuration, setup steps, or examples that the diff has altered, added, or removed. Propose concrete edits to bring the README in sync.
- **Inline doc comments**: if the project uses JSDoc, docstrings, GoDoc, Javadoc, or similar — check that changed function signatures, parameters, return types, and behavior descriptions still match the code. Flag stale or missing doc comments on public API surfaces introduced or modified in the diff.
- **CHANGELOG / migration guides**: if the project maintains a CHANGELOG, check whether the changes warrant a new entry (new feature, breaking change, deprecation). If so, propose the entry text and placement.
- **Config documentation**: if new environment variables, feature flags, CLI arguments, or config keys are introduced in the diff, verify they are documented somewhere the user would look (README, `.env.example`, config reference doc). Flag any that are missing.
- **Stale examples**: if the project has an `examples/` or `docs/` directory, check whether code samples reference APIs or patterns that the diff has changed. Flag broken or misleading examples.

The goal is not to write documentation from scratch — it is to ensure existing docs stay accurate after the changes. Missing documentation on brand-new public APIs should be flagged as `WARNING`; stale documentation that now describes wrong behavior is `CRITICAL`.

### Step 4 — Present the report

Output the report using this structure:

```
## Code Review Report

### Summary
<one-paragraph overview: how many findings total, severity breakdown, overall impression>

### 1. DRY — Duplication
<findings or "No issues found.">

### 2. Contiguous Patterns
<findings or "No issues found.">

### 3. Integration & Conventions
<findings or "No issues found.">

### 4. Tests
<findings or "No issues found.">

### 5. Dead Code
<findings or "No issues found.">

### 6. Documentation
<findings or "No issues found.">

### Proposed Actions
<numbered list of all fixes, grouped by file, ready for the user to approve or reject>
```

Each finding in sections 1-5 uses this format:

```
**[SEVERITY]** `file_path:line_number`
Description of the issue.
→ Proposed fix: <concrete suggestion or code snippet>
```

### Step 5 — Wait for approval, then apply

After presenting the report, ask the user which fixes to apply. Accept:
- "all" / "tout" — apply everything
- A list of numbers referring to the Proposed Actions list
- "none" / "rien" — skip

Only then edit the files. Do not stage or commit — leave that to the user.

## Principles

- **No false positives over missed issues**: if you're unsure whether something is a problem, flag it as a `SUGGESTION` rather than staying silent. The user can dismiss it.
- **Concrete over vague**: "this could be improved" is useless. "Extract lines 42-58 into a `formatAddress(address: Address): string` function and call it from both `createUser` and `updateProfile`" is useful.
- **Respect the codebase as-is**: your job is to make the new code fit the existing project, not to redesign the project. If the existing codebase has patterns you dislike, follow them anyway — consistency beats personal preference.
- **Language-agnostic**: this skill works on any codebase. Adapt your analysis to the language and ecosystem at hand.
