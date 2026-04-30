---
name: pr-writer
description: Generate a structured, English, product-focused PR description organised by topic. Use this skill whenever the user invokes "/roc:pr-writer", asks for a pull request description, a PR summary, a PR body, says "write a PR description", "rédige une description de PR", "prépare un descriptif de PR", "PR body", "pull request body", or any similar request. The skill either scans the current git changes or accepts context provided by the user.
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

- Maximum **2 short sentences**.
- Follow the chain `situation → action → consequence → problem`. Sentence 1 captures situation + action (what we were doing and why). Sentence 2 captures consequence + problem (what broke or what was missing because of it).
- Product framing — describe what was happening to users, operators, or the system as a whole. Do not describe the code.
- No file paths, no symbol names, no library names.

### Intent bullets (block 2)

- **Exhaustive** on the strategic intent of the change: cover every dimension of *what we decided to do* and *why it solves the problem*.
- Each bullet is a **logical decision**, phrased in product/functional terms. Not a code change.
- Vocabulary stays close to the user/operator/system perspective. No file paths, no function names, no library specifics.
- One bullet per distinct decision. No padding, no bullets that just rephrase a previous one.

### Change bullets (block 3)

- List the **important technical changes** applied to the project: mechanisms added, libraries introduced, switches flipped, structural moves, contracts changed.
- Each bullet is concrete and technical. May reference module-level concepts (e.g. "the queue worker", "the webhook handler") but **not** individual file paths.
- Skip incidental edits (typos, formatting, dependency bumps unless they matter). One bullet per significant change.
- If the PR is purely a refactor with no observable change, this block can still describe what moved and why the new structure is better.

## Hard rules — what NOT to include

- Do NOT include a "Test plan" section. Ever.
- Do NOT add any heading other than `### <Topic>`. No `## Summary`, no sub-headings, no labels like `**Context:**` or `**How:**`.
- Do NOT list every touched file or produce a file-by-file changelog.
- Do NOT include "Out of scope / follow-ups" unless the user explicitly asks for it.
- Do NOT include emojis.
- Do NOT include boilerplate like "this PR does X, Y, Z" — go straight into the first topic.
- Do NOT merge unrelated changes into a single topic, and do NOT split one logical change across multiple topics.

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

1. **Context** — apply the `situation → action → consequence → problem` chain in 2 sentences max. Stop the moment the reader understands why the change matters.
2. **Intent bullets** — list every strategic decision behind the change. Each bullet is a sentence about *what we now do* (or no longer do), phrased in product/operator terms.
3. **Change bullets** — list the concrete technical changes. Each bullet names a mechanism, a switch, a dependency, a structural move. Group small tweaks under a single bullet; do not pad.

If you have genuine doubt about the product angle of a topic (e.g. the diff is purely internal refactoring with no user-visible impact), ask the user one short clarifying question before writing that block. Do NOT invent a product framing.

### Step 4 — Output

Return **only** the markdown code block. No preamble, no commentary around it. The user copy-pastes it as-is.

## Good example

Input: connector was creating duplicate cases on Fasap when MerciYanis retried outbound webhooks against a slow target; implementation added idempotence check and switched to async HTTP response.

Output:

````md
```md
### Outbound webhook idempotence on Fasap

Outbound webhooks were retried whenever the Fasap target took too long to respond. The retry sometimes arrived after the original request had succeeded, creating duplicate cases on Fasap and forcing the operations team to deduplicate by hand each morning.

- Each outbound case is now processed at most once on the Fasap side, regardless of how many retries MerciYanis issues
- The HTTP handler acknowledges the request immediately, so the upstream sender stops retrying as soon as the message is accepted
- Operators no longer have to deduplicate Fasap cases manually

- Added an idempotence key check inside the queued job, scoped per `(case_id, target_system)` and persisted in Redis with a 7-day TTL
- Switched the webhook handler to respond 200 synchronously and enqueue processing as a background job
- Surfaced an idempotence-skip log entry so support can confirm which retries were absorbed

### File upload queue isolation

The shared sequential queue was being blocked for up to 90 seconds per retry cycle whenever a file upload stalled. Other case events queued behind the upload were delayed by the same amount, breaking the SLA for time-sensitive notifications.

- File uploads no longer share the case-event queue, so a slow upload cannot delay unrelated events
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
- Padding bullets to look more thorough. If two intent bullets cover everything, ship two.
