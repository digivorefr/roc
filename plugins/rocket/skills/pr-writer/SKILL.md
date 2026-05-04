---
name: pr-writer
description: Generate a structured, English, product-focused PR description organised by topic. Use this skill whenever the user invokes "/rocket:pr-writer", asks for a pull request description, a PR summary, a PR body, says "write a PR description", "rédige une description de PR", "prépare un descriptif de PR", "PR body", "pull request body", or any similar request. The skill either scans the current git changes or accepts context provided by the user.
---

# PR Description Writer

Produce a **structured, English, product-focused** pull request description organised by topic. The audience is a reviewer who wants to understand what problem each change solves and how, in under a minute.

The description is composed of one or more `### <Topic>` blocks. Each block follows a fixed three-part shape: a short context paragraph, a list of intent bullets, and a list of technical-change bullets. Topics are independent — one per distinct concern in the PR.

## Output contract

- **Format**: a single markdown code block containing the description, ready to copy-paste into a GitHub PR body.
- **Language**: English.
- **Tone**: product-first for context and intent, technical for the change list.
- **Heading depth**: only `###` headings, one per topic. No `##` parent, no `####` children. Flat list of topics.
- **Block shape**: each topic block is exactly three parts separated by a single blank line — context paragraph, intent bullets, change bullets. No labels between them; the reader infers from position and content style.

## Topic block shape

```
### <Topic>
<context paragraph>

- <intent bullet>
- <intent bullet>

- <change bullet>
- <change bullet>
```

### Context paragraph

- **One sentence preferred**, two only if the second adds critical context the reviewer cannot infer.
- Follow the chain `situation → action → consequence → problem` compressed into the available sentence(s). The reader needs to know what was happening, what broke, and to whom.
- Product framing — describe what was happening to users, operators, or the system as a whole. Do not describe the code.
- No file paths, no symbol names, no library names.

### Intent bullets (block 2)

- **Maximum 3 bullets, prefer 2.** Pick the most important decisions; drop the rest.
- Each bullet is **one short clause** (≤140 chars), one logical decision, phrased in product/functional terms.
- No compound bullets: do not chain ideas with "and", semicolons, or em-dashes that hide a second decision. Split or drop.
- Vocabulary stays close to the user/operator/system perspective. No file paths, no function names, no library specifics.

### Change bullets (block 3)

- **Maximum 3 bullets, prefer 2-3.** Pick the most consequential technical changes; merge small ones under a single bullet rather than expanding.
- Each bullet is **one short clause** (≤140 chars) naming a single mechanism, switch, dependency, or contract change.
- May reference module-level concepts (e.g. "the queue worker", "the webhook handler") but **not** individual file paths.
- Skip incidental edits (typos, formatting, dependency bumps unless they matter).
- If the PR is purely a refactor with no observable change, describe what moved and why the new structure is better — still capped at 3 bullets.

## Hard rules — what NOT to include

- Do NOT include a "Test plan" section. Ever.
- Do NOT add any heading other than `### <Topic>`. No `## Summary`, no sub-headings, no labels like `**Context:**` or `**How:**`.
- Do NOT list every touched file or produce a file-by-file changelog.
- Do NOT include "Out of scope / follow-ups" unless the user explicitly asks for it.
- Do NOT include emojis.
- Do NOT include boilerplate like "this PR does X, Y, Z" — go straight into the first topic.
- Do NOT merge unrelated changes into a single topic, and do NOT split one logical change across multiple topics.
- Do NOT exceed 3 bullets in any single block. If you have more, you have not picked the most important — collapse or drop.
- Do NOT chain multiple ideas inside one bullet. One bullet, one idea, one short clause.

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

### Step 2 — Identify topics

Read the diff and group the changes into independent **topics**. A topic is a coherent concern that a reviewer can evaluate on its own merits.

- One topic per independent concern → one `### <Topic>` block.
- Two changes belong to the same topic if removing one would force the other to be reworked. Otherwise they are separate topics.
- Refactor PRs may be a single topic. Multi-feature PRs almost always split into several.
- The `<Topic>` title is a short noun phrase (4-7 words), naming the area or behaviour. Not a sentence, no verb in -ing form unless natural.

### Step 3 — Write each topic block

For each topic, produce the three parts in order:

1. **Context** — compress the `situation → action → consequence → problem` chain into one sentence (two only if essential). Stop the moment the reader understands why the change matters.
2. **Intent bullets** — at most 3, prefer 2. One short clause per bullet, one decision per bullet, product/operator perspective.
3. **Change bullets** — at most 3, prefer 2-3. One short clause per bullet naming one mechanism or contract change. Group small tweaks under a single bullet; never pad.

If you have genuine doubt about the product angle of a topic (e.g. the diff is purely internal refactoring with no user-visible impact), ask the user one short clarifying question before writing that block. Do NOT invent a product framing.

### Step 4 — Output

Return **only** the markdown code block. No preamble, no commentary around it. The user copy-pastes it as-is.

## Good example

Input: connector was creating duplicate cases on Fasap when MerciYanis retried outbound webhooks against a slow target; implementation added idempotence check and switched to async HTTP response.

Output:

````md
```md
### Outbound webhook idempotence on Fasap

Webhook retries on slow Fasap calls produced duplicate cases that operators had to deduplicate by hand every morning.

- Outbound cases are now processed at most once on Fasap, eliminating the daily manual deduplication
- The webhook handler stops the upstream retry storm by acking 200 as soon as the message is accepted

- Added an idempotence key per `(case_id, target_system)` in Redis, 7-day TTL
- Webhook handler now acks 200 synchronously and enqueues processing as a background job
- Logged an idempotence-skip line so support can confirm which retries were absorbed

### File upload queue isolation

A stalled upload could block the shared case-event queue for up to 90 seconds, breaking the SLA on unrelated time-sensitive events.

- A slow upload no longer delays unrelated events
- Upload ordering is preserved within the dedicated queue (FIFO per case)

- Introduced a dedicated upload worker fed by its own RabbitMQ queue
- The case-success handler now enqueues an upload job instead of running it inline
- Added per-queue depth metrics so the slowdown is visible before it impacts the SLA
```
````

(The outer ``` ```md ``` fences are just to make this example readable inside this skill file. The actual output is a single ```md...``` code block.)

## Bad examples (do not produce these)

- A description with a `## Summary` heading or any heading deeper than `###`.
- A description with labels like `**Context:**` / `**Solution:**` / `**Changes:**` between blocks.
- A context paragraph that lists file paths, function names, or library specifics.
- An intent bullet that says `Refactored X to use Y` — that's a change bullet, not an intent.
- A change bullet that says `Modified user.service.ts and updated user.controller.ts` — file paths leak into the description.
- A description with a "Test plan" section.
- A topic merging two unrelated concerns into one block, or splitting one concern across two blocks.
- Padding bullets to look more thorough. If one intent bullet covers everything, ship one.
- A bullet that runs to two or three lines because it joins multiple ideas with "and"/";"/em-dashes — the reader skims, the second idea is lost.
- Four or more bullets in a single block — that's a sign you have not picked the most important.
