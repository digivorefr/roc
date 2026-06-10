---
name: commit-writer
description: Generate git commit messages from staged or unstaged changes, or from selected commits since the default branch. Use this skill whenever the user invokes "/rocket:commit-writer", "/rocket:commit-writer rebase" (pick which commits define the scope, e.g. before a squash or rebase), asks for a commit message, a squash message, wants to describe their git changes, says "what should I commit?", "write a commit message", "redige un message de commit", "propose un commit", "message pour le squash", or any similar request involving summarizing git diffs into a commit message.
---

# Git Commit Message Generator

Generate 3 commit message variants from the current git diff.

## Rules

- Each message is a single line, max 80 characters
- Written in English
- Must grammatically complete the sentence "This commit..." but do NOT include "This commit" in the output
- The action verb must be in base form (infinitive), NOT conjugated: `Add`, `Fix`, `Refactor`, NOT `Adds`, `Fixes`, `Refactors`
- First letter must be capitalized
- No period at the end
- Present each variant in a code block ready to copy-paste

## Workflow

### Step 1 - Get the diff

**If the user's argument (whitespace-trimmed) is `rebase`**, resolve the scope with the [scope selection procedure](#scope-selection--rebase-mode) below instead of the default chain. The generated messages describe the **combined** selected scope — the typical use case is writing the message for an upcoming squash or rebase of several WIP commits.

Otherwise, run in order until you get output:
1. `git diff HEAD`
2. `git diff --cached`
3. `git status` — if both empty, inform user no changes detected

Also run `git log --oneline -5` to understand the project's commit style.

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

### Step 2 - Analyze the diff

Identify: which files changed, what was added/removed/modified, the apparent intent.

### Step 3 - Generate 3 variants

Propose 3 messages differing in detail level, angle, and wording.

### Output format

**Option 1** - *broad*
[code block]

**Option 2** - *specific*
[code block]

**Option 3** - *technical*
[code block]

Keep commentary minimal.

## Good examples

Add user authentication with JWT support
Fix null pointer error in invoice calculation
Refactor API response handler to reduce duplication

## Bad examples

- `Added login feature` — conjugated verb
- `This commit adds a new button` — includes "This commit" + conjugated
- `add user authentication` — no capital letter
- Any message over 80 characters
- `Update stuff` — too vague
