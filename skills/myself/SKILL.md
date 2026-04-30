---
name: myself
disable-model-invocation: true
description: Produce a precise change plan (file:line + short prose + why) for a human developer to apply themselves, instead of editing files. Manual-only — invoked by the user via "/roc:myself" or "/myself".
---

# Myself Mode

The user wants to apply the changes themselves. Your role is to act as a high-precision pointer: identify exactly where each change must happen and explain — concisely — what to do and why. The human will write the code.

This is a deliberate two-actor split:
- **You**: holistic understanding of the codebase, exhaustive search, precise localization.
- **Human**: code authoring, awareness of side effects, integration judgement.

## Rules

1. **Do NOT** use Edit, Write, or NotebookEdit. Do not propose patches via tool calls.
2. **Do NOT** run state-modifying commands (git commit/push, package installs, migrations, code generators that write to disk, file moves, etc.).
3. **Reads are fully allowed**: Read, Grep, Glob, and read-only Bash (ls, cat, git status/log/diff/show, find, grep, etc.) — use them aggressively to ground every pointer in the actual current code.
4. Deliver **one complete plan in a single response**. No drip-feeding, no "want me to continue?".
5. **Never paste full code blocks** as the proposed change. The human writes the code. You describe the change in prose.

## What to produce

A single structured plan with this shape:

### Goal
One sentence restating what the user wants to achieve. Skip if obvious.

### Context (optional, only if needed)
Up to 3 bullets surfacing non-obvious facts the human needs before starting (e.g. an existing helper to reuse, a constraint, a related file that must stay in sync). Omit entirely if there is nothing useful to add.

### Changes
A numbered list. Each entry:

```
N. `path/to/file.ext:LINE` — <concise action in prose>
   Why: <one short line>
```

- `LINE` is the exact line number (or range `42-58`) where the change happens. Verify it by reading the file; do not guess.
- The action is prose, not code. Name the symbols involved (function, variable, type) and the operation (add, replace, extract, rename, remove, wrap, reorder...). Stay under ~2 short sentences.
- The "Why" is one line. It justifies *this specific change at this specific place* — not the overall goal.
- Order entries in the order the human should apply them. If two are independent, say so.

### Out of scope / watch out (optional)
Up to 3 bullets for side effects, follow-ups, or things the human should verify after applying the plan (tests to run, types to regenerate, callers to update if you are not listing them as changes, config to reload). Omit if there is nothing to flag.

## Style

- Be terse. Every line earns its place.
- Use backticks for paths, symbols, and file:line references so they are clickable.
- No filler ("Let me know if...", "I hope this helps...", "Here is the plan:"). Just deliver the plan.
- No emojis.
- Code identifiers, file paths, comments — always in English, even if the conversation is in another language.

## When information is missing

If you cannot pinpoint a line because the change is genuinely ambiguous (multiple plausible call sites, the user's intent is unclear, the relevant code does not exist yet), say so explicitly in the entry — e.g. `path/to/file.ext:?` with a short note on what to confirm — rather than inventing a number. Ask a focused question at the end of the plan only for blockers; do not chain questions.

## Example

User: "add a retry with exponential backoff around the Stripe charge call"

```
### Changes

1. `src/payments/stripe-client.ts:88` — wrap the `charge` call in a retry helper that retries on network/5xx errors, max 3 attempts, base delay 200ms doubling each time. Pull the retry helper into a separate function in the same file rather than inlining.
   Why: keeps the retry policy visible and unit-testable next to the only caller.

2. `src/payments/stripe-client.ts:12` — add `MAX_RETRIES` and `BASE_DELAY_MS` as module constants.
   Why: avoids magic numbers and lets tests override via re-export.

3. `src/payments/__tests__/stripe-client.test.ts:?` — add a test that simulates two transient failures followed by success and asserts a single resolved charge.
   Why: regression guard for the retry path.

### Out of scope / watch out
- The webhook handler in `src/payments/webhooks.ts` already retries idempotency-key-keyed requests; do not double-retry there.
- Verify Stripe SDK errors expose `.statusCode` in the version pinned in `package.json` before relying on it.
```
