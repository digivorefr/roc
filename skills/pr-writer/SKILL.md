---
name: pr-writer
description: Generate a short, product-focused PR description in English. Use this skill whenever the user asks for a pull request description, a PR summary, a PR body, says "write a PR description", "rédige une description de PR", "prépare un descriptif de PR", "PR body", "pull request body", or any similar request. The skill either scans the current git changes or accepts context provided by the user.
---

# PR Description Writer

Produce a **short, English, product-focused** pull request description. The audience is a reviewer who wants to know **what problem was solved** and **how**, in under 30 seconds.

## Output contract

- **Format**: a single markdown code block containing the description, ready to copy-paste into a GitHub PR body.
- **Length**: as many bullets as the PR genuinely warrants — one per distinct topic, no padding. Small PRs get 1-2 bullets, larger ones can have more. No heading inside the block other than `## Summary`.
- **Language**: English.
- **Tone**: product-first, technical when needed but not exhaustive.
- **Structure**: one top-level `## Summary` heading, bullets directly below. Each bullet names **the problem** and **the means** used to solve it, in one or two sentences.

## Hard rules — what NOT to include

- Do NOT include a "Test plan" section. Ever.
- Do NOT list every touched file.
- Do NOT include line-by-line changelog or exhaustive file-by-file descriptions.
- Do NOT include "Out of scope / follow-ups" unless the user explicitly asks for it.
- Do NOT include emojis.
- Do NOT include headings like "Files touched", "Verification", "Checklist".
- Do NOT include boilerplate like "this PR does X, Y, Z" — go straight to the point.

## Workflow

### Step 1 — Gather context

Two cases:

**Case A: context provided by the user** (they pasted a diff, a description, a spec, or previous session content)
- Use that context directly. Do NOT run git commands.

**Case B: no context provided**
- Run these in order, use whichever yields content:
  1. `git diff HEAD` (staged + unstaged vs HEAD)
  2. `git diff --cached` (staged only)
  3. `git diff @{upstream}..HEAD` (commits ahead of remote)
- Also run `git log --oneline @{upstream}..HEAD 2>/dev/null || git log --oneline -5` for commit context.
- If nothing yields output, tell the user no changes are detected and ask for context.

### Step 2 — Identify the product angle

For each change, answer:
- **What was broken or missing from the user/operator's perspective?** (not "we refactored X" — "feature Y didn't work because Z")
- **What concrete mechanism fixes it?** (one technical sentence — name the approach, not every file)

If the changes cover multiple independent topics, produce one bullet per topic. Don't merge unrelated changes into a single bullet, and don't split one change into several.

### Step 3 — Write the description

Apply this shape:

```md
## Summary

- <Problem from the product angle>. <Means: one short technical sentence>.
- <Problem from the product angle>. <Means: one short technical sentence>.
```

Each bullet must:
- Start with the symptom, user-facing behavior, or product need — NOT with the code change.
- Follow with a short sentence describing the technical solution (mechanism, data flow, config switch, not file paths).
- Stay under ~40 words per bullet.

### Step 4 — Output

Return **only** the markdown code block. No preamble, no commentary around it. The user copy-pastes it as-is.

If you have genuine doubt about the product angle (e.g. the diff is purely internal refactoring with no user-visible impact), ask the user one short clarifying question before writing. Do NOT invent a product framing.

## Good example

Input: connector was creating duplicate cases on third-party system when upstream retried webhooks; implementation added idempotence check and switched to async response.

Output:
```md
## Summary

- Duplicate cases were created on Fasap when MerciYanis retried outbound webhooks against a slow target. Added an idempotence check inside the queued job and made the HTTP handler respond 200 immediately while processing asynchronously.
- File uploads were blocking the sequential queue for up to 90 seconds per retry cycle. They now run as a dedicated follow-up job enqueued after the case succeeds, FIFO ordering preserved.
```

## Bad examples (do not produce these)

- A description with a "Test plan" section.
- A description listing every touched file.
- A bullet that starts with "Refactored X" or "Added Y" without saying **why** from the product angle.
- A wall of headings (Summary, Files, Tests, Follow-ups).
- Padding bullets to look more thorough. If one bullet is enough, ship one bullet.
