---
name: commit-writer
description: Generate git commit messages from staged or unstaged changes. Use this skill whenever the user asks for a commit message, wants to describe their git changes, says "what should I commit?", "write a commit message", "redige un message de commit", "propose un commit", or any similar request involving summarizing git diffs or changes into a commit message.
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

Run in order until you get output:
1. `git diff HEAD`
2. `git diff --cached`
3. `git status` — if both empty, inform user no changes detected

Also run `git log --oneline -5` to understand the project's commit style.

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
