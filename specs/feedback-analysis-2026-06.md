# Roc — user feedback analysis and improvement plan (June 2026)

**Status**: approved with amendments (2026-06-10).

**Decisions (2026-06-10)**:
1. Contextualisation (§3): **deleted entirely** — no v2 rebuild. Hooks, `context-gate` binary, `context-update` and `context-clear` skills, lexicon references in agents/setup/docs all removed.
2. inbox-watch (§4): **deleted entirely** — the direct-Gmail-OAuth redesign is rejected. `inbox-watch` command, `inbox-watch-tick` skill, SessionStart bootstrap hook, `inbox-poll` binary all removed. `tone-profile` and `inbox-reply` remain, decoupled from the watcher.
3. `rebase` mode (§2.3–2.5): approved with the single multiSelect commit-picker question.
4. Batches 1–3 (§5): approved as proposed.

**Inputs**:
- User feedback after ~6 weeks of daily Roc usage (2026-06-10).
- Repository sources: every skill, agent, command, hook, and binary in `plugins/rocket/` and `plugins/my-hand/`.
- Runtime evidence: `.roc/rocket/` state and logs in three consumer projects (`merciyanis/dev`, `merciyanis/dev/professional-services`, `merciyanis/email`), `~/.roc/my-hand/` state.
- Session transcripts: 459 sessions mined across all merciyanis projects (March–June 2026), including a 6.2-day inbox-watch session with full token accounting.
- Web research: memory/glossary systems (Anthropic auto memory, Cline Memory Bank, Cursor Memories, Windsurf, Aider, claude-mem, compound engineering, Contextive) and email-triage systems (Inbox Zero, Superhuman, Fyxer, Jace), plus Claude Code primitives (hooks, scheduled tasks, channels, headless billing).

---

## 1. Executive summary

| Component | User verdict | Analysis verdict | Action |
| --- | --- | --- | --- |
| spec-writer | Works very well; wants polish pass, shorter specs, more critical stance | Sound; missing self-review step and volume budget | **Amend** (prompt) |
| spec-maker | Works well; too much time on lint/test discovery and interleaved runs | Two distinct problems: missing conventions block in consumers + no phase discipline | **Amend** (prompt) + setup adoption |
| commit-writer | Very good; wants a `rebase` scope mode | Healthy (45–67 uses/session observed) | **Extend** (scope mode) |
| pr-writer | Content good, too chatty; wants `rebase` mode | Output contract already strict; budget not global | **Tighten + extend** |
| review | Excellent; wants `rebase` mode | Only ever used on uncommitted scope | **Extend** (scope mode) |
| myself | Very good | No issue found | **Keep as is** |
| no-code | Very, very good; exit conditions ambiguous | Confirmed leak: implicit exits observed in transcripts | **Harden + spec carve-out** |
| setup | Barely used | Never adopted by any real consumer project; flow too heavy | **Redesign flow** |
| Contextualisation (hooks + skills) | Never produced anything tangible | Confirmed dead by design: 4 independent silent-failure layers | **Full redesign** |
| inbox-watch | Token-hungry, unreliable | Measured: ~$4.23/day potential, ~10% tick delivery; structural | **Full redesign** |

Two cross-cutting facts explain a disproportionate share of the pain:

1. **`/rocket:setup` was never successfully applied to the consumer projects.** Neither `merciyanis/dev` nor `professional-services` has a `## Project conventions` block in its `CLAUDE.md` (verified 2026-06-10). spec-maker therefore re-discovers the lint/test commands by trial and error in every session. The spec-maker complaint and the setup complaint are the same problem.
2. **Both background systems (context-update hook, inbox-watch loop) put a model inside a polling/firing loop.** Every reliable system surveyed does the opposite: deterministic machinery decides *when*, the model only decides *what*. Worse, the two systems compounded: in the email project, every 10-minute inbox tick ended an assistant turn, which fired the Stop hook, which spawned a 36–117 s Sonnet[1m] subprocess that always failed to write.

---

## 2. Component analyses

### 2.1 spec-writer

**Feedback**: efficient agent. Wants (a) a final polish/verification pass before delivery, (b) smaller specs — simple language, lists, boxes, short sentences, no long prose, (c) a sustained critical stance: hunt for flaws, vagueness, uncertainty; challenge the proposal.

**Current state** ([spec-writer.md](../plugins/rocket/agents/spec-writer.md)): the workflow ends at "Create the specification document" + "Ensure the spec references existing patterns". There is no self-review step. Style guidance says "be concise" but sets no budget. The critical stance exists only as "Ask probing questions" during elicitation — nothing requires the agent to challenge the request itself or to keep flagging residual uncertainty in the document.

**Proposed changes** (prompt-only, no structure change):

1. **Add a final pass step** (new last workflow step): re-read the whole spec and check — every requirement implementable without architectural decisions; no contradiction between sections; no orphan reference; vocabulary consistent with the lexicon; every remaining unknown listed in an `Open questions` section, never silently resolved by assumption. Fix in place, then deliver.
2. **Volume budget**: target the shortest spec that is complete. Concrete rules: short declarative sentences; bullets over paragraphs; one idea per bullet; tables/boxes for enumerable facts; hard ceiling (e.g. ~150 lines for a typical feature, justified overrun allowed for genuinely large scopes). Forbid restating CLAUDE.md rules and forbid prose introductions/conclusions (already partially there).
3. **Adversarial stance**: add a `Challenge the request` responsibility — before writing, the agent must look for: under-specified behaviors, hidden complexity, conflicts with existing patterns, simpler alternatives, and risks the user has not mentioned. Findings either become clarifying questions, or land in `Open questions` / a short `Risks` list. The agent is explicitly allowed to recommend *against* part of the proposal.

### 2.2 spec-maker

**Feedback**: works well, but (a) spends a long time finding how to run lint/tests, (b) spends a long time running them, (c) development phases are too fragmented by lint runs and intermediate fixes. Feature first, lint after. TDD is legitimate when the agent judges it fits — its call, stated explicitly. Analyze the intermediate steps the agent struggled with.

**Evidence**:
- Consumer `CLAUDE.md` files contain no `## Project conventions` block, hence no declared verification command (root cause of (a)).
- Transcripts (admiring-poincare session): 4 full `yarn run check` invocations clustered in one implementation run; checks passed. The pattern is batched-but-repeated full gates — the project's full gate (lint + types + all tests) is paid several times even when only one module changed.
- [spec-maker.md](../plugins/rocket/agents/spec-maker.md) already says "Make it work first, then satisfy lint/type checks" — but it is one bullet buried in step 4, and the verification section ("run the verification command, fix failures") sets no cap and no phase boundary.

**Proposed changes** (prompt-only):

1. **Phase discipline**: restructure the workflow into explicit phases with a hard boundary — Phase A: implement the complete feature; **no lint/type/format runs between edits**. Phase B: single verification pass (the declared command), fix all findings in batch, re-run once. Only persistent failures justify additional cycles, and each extra cycle must be announced with a reason.
2. **TDD as an explicit, declared choice**: before Phase A, the agent states its testing strategy in one line — either "tests after implementation" or "TDD on <scope> because <reason>". When TDD is chosen, the red-green cycle replaces the no-test rule for that scope; lint/typecheck still waits for Phase B.
3. **Bounded discovery of the verification command**: read `CLAUDE.md` conventions block first. If absent: one bounded discovery pass (manifest scripts, Makefile, CI workflow files — read, not executed), pick the best candidate, state it, and proceed. Never rediscover mid-run. At completion, recommend running `/rocket:setup` so the next run skips discovery entirely.
4. **Cheapest sufficient gate during iteration**: when extra verification cycles are needed, prefer the narrowest check the project offers (single test file, affected package) and keep the full gate for the final pass. Phrased stack-agnostically; the consumer's CLAUDE.md may name a narrow command.

### 2.3 commit-writer

**Feedback**: very good. Wants a mode where the agent lists all commits after `main` and the user picks which commits (plus uncommitted changes) define the analysis scope — e.g. `/rocket:commit-writer rebase`.

**Proposed change** — add a `rebase` argument:

1. `$ARGUMENTS` empty → current behavior, unchanged.
2. `$ARGUMENTS` = `rebase` → detect the default branch (`origin/HEAD`, fallback `main`/`master`), run `git log <base>..HEAD --oneline`, present a numbered list (+ a final entry for uncommitted changes). The user picks entries (numbers, ranges, `all`). Scope = concatenated diffs of the selected commits + working tree if selected. Then the normal 3-variant output applies. Use one `AskUserQuestion` (multiSelect) for the pick.
3. Use case to honor explicitly: writing the message for an upcoming squash/rebase of several WIP commits.

**Hygiene note**: transcripts show a personal copy of this skill at `~/.claude/skills/git-commit-writer` being invoked as `/git-commit-writer` alongside the plugin one. Two divergent copies will drift; the personal copy should be deleted once the plugin version covers its usage.

### 2.4 pr-writer

**Feedback**: content is right but too talkative. Wants the same `rebase` scope mode.

**Analysis**: the output contract ([pr-writer SKILL.md](../plugins/rocket/skills/pr-writer/SKILL.md)) is strict per block (≤3 bullets, ≤140 chars, 1-sentence context) but has **no global budget**: nothing bounds the number of topics, and "two only if essential" context sentences plus 3+3 bullets × N topics still yields a long page. Verbosity lives in topic proliferation and clause padding, not in any single rule violation.

**Proposed changes**:

1. **Global budget**: a typical PR description fits in 1–3 topics; >3 topics requires the PR to be genuinely multi-feature, and the total description stays under ~30 lines. When in doubt, merge topics — "two changes serving one reviewable intent" is one topic.
2. **Default to the floor, not the ceiling**: rephrase per-block rules so 2 bullets is the norm and 3 the justified exception (current text already "prefers 2" for intent but "prefers 2-3" for changes — tighten both to "2, 3 only when dropping one loses a reviewer-relevant fact").
3. **`rebase` mode**: same scope-selection mechanism as commit-writer (numbered commits since the default branch + uncommitted entry, one multiSelect question). Replaces the current Case B fallback chain when invoked with `rebase`.

### 2.5 review

**Feedback**: excellent skill. Wants the `rebase` mode too.

**Proposed change**: same scope selector as commit-writer/pr-writer. In `rebase` mode the diff under review = selected commits + optionally uncommitted changes; everything else (criteria, report format, approval gate) unchanged. Step 1's automatic fallback chain remains for argument-less invocations. The three skills should share identical wording for the scope-selection procedure so behavior is predictable across them (single source: write the procedure once and copy it verbatim into the three SKILL.md files — plugins have no include mechanism).

### 2.6 myself

No change requested, none proposed. Transcript evidence shows no friction.

### 2.7 no-code

**Feedback**: very good mode. But: exit must always be explicit — if the conversation drifts toward "do it", the agent must request permission to leave the mode and is forbidden to edit a single line of code while it is active. Exception wanted: the no-code-to-spec drift is a regular, healthy pattern; allow markdown writing in a dedicated `specs/` folder so knowledge capture is never blocked.

**Evidence of the leak** (cadrage session, transcripts): user invoked `/no-code` with UI feedback → assistant analyzed (correct) → assistant then **spawned `spec-to-implementation` subagents that edited and committed code, with no explicit exit approval** → user re-entered `/no-code` for the next batch. The current SKILL.md frames no-code as "a chat-only **response**" (singular), so the model treats the *next* turn as out of scope; and rule 1 ("do not create/edit files") says nothing about delegating edits to subagents.

**Proposed changes**:

1. **Mode semantics**: no-code is a session state, not a one-response modifier. It stays active until the user explicitly lifts it. State this in the first line.
2. **Explicit exit protocol**: if the user asks for something that requires modifying files, the agent must answer with a one-line request: state what it would do and ask for explicit confirmation to exit no-code. Only an unambiguous yes ("go", "sors du mode", "fais-le") lifts the mode. Acting on inferred intent is forbidden.
3. **Close the subagent loophole**: forbid spawning any agent/task that can edit files while the mode is active. Delegated edits are edits.
4. **Spec carve-out**: while in no-code, the agent MAY create/edit **markdown files only**, **inside the project's spec directory only** (`specs/` by default; honor an existing equivalent like `docs/specs/` if the project has one). Purpose: compile knowledge, needs, and decisions from the discussion — typically with spec-writer. Everything else on disk remains read-only. The carve-out does not auto-exit the mode.

### 2.8 setup

**Feedback**: barely used. Wants: safe to run on an existing codebase, safe to re-run anytime without destroying data, better stack analysis.

**Evidence**: zero adoption where it matters — both heavy-usage consumer projects lack the conventions block; the only populated lexicon was bootstrapped manually in the roc repo itself. The flow's weight is documented in its own SKILL.md: up to 2–4+ `AskUserQuestion` rounds (integration plan, Round 1, Round 2, apply confirmation) before anything is written.

**Diagnosis**:
- The interactive cost is front-loaded and high; nothing delivers value until the very end (single big diff).
- Re-run semantics exist on paper (Replace/Merge/Keep both) but are complex enough that the safest user behavior is "don't re-run" — and "Keep both side by side" is a data-corruption option dressed as a choice (two conventions blocks would confuse every reader, human or agent).
- Stack detection reads manifests only. It ignores the strongest signal available: CI workflows (`.github/workflows/*.yml` run the *real* verification commands), lint configs, and monorepo workspace layouts.
- Setup currently also bootstraps the lexicon and asks about "Background context" — coupling it to a system that does not work (see §3). This question should disappear in v2.

**Proposed redesign**:

1. **Detect → propose → confirm, one round**: run the full detection (manifests + lockfiles + CI workflows + lint/format configs + workspace globs + existing CLAUDE.md prose), compose the complete block, show the diff, and ask **one** question: Apply / Adjust / Cancel. All current Round-1/Round-2 questions become detected values shown in the diff; only genuinely undetectable values (e.g. no test command anywhere) get a question, batched into that same single round.
2. **Idempotent re-run by construction**: the block is delimited by stable markers (e.g. `<!-- rocket:conventions:start -->` / `:end -->`). Re-run = regenerate inside the markers, never touch anything outside, show the diff of the managed region only. User edits inside the region survive via merge (keep user line when it conflicts with a detected value, flag it in the summary). Drop "Keep both" entirely.
3. **CI as primary source for the verification command**: a command that CI actually runs outranks a `package.json` script name guess. Cite the source of each detected value in the preview ("from .github/workflows/ci.yml").
4. **Decouple from contextualisation**: remove the Background-context question and the lexicon bootstrap from setup until the v2 context system (§3) defines what, if anything, setup must create.

---

## 3. Contextualisation system — root-cause analysis and redesign

### 3.1 What was observed

The user has never seen the system produce anything. The forensic evidence agrees:

- **roc repo**: `lexicon-update.log` has 3 lines since creation; the last (2026-05-06) is `skip: heuristic rejected (content_lines=0, tool_only=true)` — the delta extractor misread a real session as empty. Nothing has fired in 5 weeks. The only populated lexicon was written during the manual "Setup Roc on Roc" session, not by the pipeline.
- **professional-services**: 3 hook fires on 2026-05-05, 80–205 s of Sonnet[1m] each, all three ending in `Permission denied. Please approve the write…` — a plea written to a log file no one reads, by a headless process no one can approve.
- **email project**: ~25 fires over two days (one per assistant turn — including after every inbox-watch tick), 36–117 s each, plus a stale lock that silently blocked everything for a full day. The hook and the inbox loop amplified each other.
- **Today**: the v2 toggle (`Background context: enabled`) is absent from every consumer CLAUDE.md (setup recommends `Disabled`), so the v2 pipeline never starts at all.

### 3.2 Root causes (all independent, all sufficient to kill it)

1. **Headless writes are impossible**: `claude -p` spawned by the hook cannot obtain Write permission interactively; every successful classification died at the write step (own commit `07a4b58` is prior evidence).
2. **Async hook output is discarded by spec**, so every failure was invisible by construction.
3. **Nested `claude` from a hook is a documented minefield** (`CLAUDE_CODE_*` env detection causes refusals/hangs across CLI versions — anthropics/claude-code#32618).
4. **The gate discards on skip**: the cursor advances on every debounce/heuristic/Haiku rejection, so deferred content is not deferred — it is lost forever.
5. **`context: fork` skills do not see conversation history** (documented), so the skill's core premise ("re-read the conversation") was invalid in fork mode; the shell wrapper grew to pipe transcripts around this.
6. **Default-off toggle** ensured that after the v2 cost fix, the system simply never ran.

### 3.3 What reliable systems do (survey result)

Every working system in the wild fits one of three shapes:
- **In-session, model-driven, visible writes** — Anthropic's own auto memory (the first-party answer to this exact problem: main session writes `MEMORY.md` + topic files in the foreground, hard 200-line/25KB load cap), Windsurf Memories.
- **Explicit trigger** — Cline Memory Bank ("update memory bank"), compound engineering (`/compound`), Contextive (fully manual committed glossary YAML), Aider conventions, Copilot instructions.
- **Real daemon infrastructure** — claude-mem (persistent worker + SQLite queue + SDK calls outside hooks).

No production system ships "hook-triggered headless model chain writing files silently". Cursor's background observer — the closest cousin — only *proposes*; a human approves every memory.

Design principles extracted: write in the foreground with the session's own permissions; deterministic triggers, model-judged content; visible writes; hard mechanical size cap; distill before context dies; never drop unprocessed input; plain committed markdown reviewed like code; the static file is the product, the updater is optional.

### 3.4 Proposed redesign (v2)

**Delete** (no replacement): the Stop hook + `update-context.sh`, the `context-gate` binary and its build, the Haiku gate, the cursor state, the per-project toggle, scoped/hook modes in the skill. The entire economic problem the hybrid gate solved disappears when there is no background model call to gate.

**Keep**: the lexicon file, its location (`.roc/rocket/lexicon.md`, committed), its format (areas → concepts → Definition/Aliases/Relations/Source — it is good), the size cap, `/rocket:context-update` as the single writer, `/rocket:context-clear`.

**New architecture — two deterministic nudges, one foreground writer**:

1. **The skill runs in the main session** (drop `context: fork`): it can see the live conversation (no transcript parsing), writes with the session's normal permissions (no headless cliff), and the user sees the edit happen (trust + git review). Manual `/rocket:context-update` works exactly as before, minus the failure modes.
2. **Staleness nudge (in-session)**: a sync `UserPromptSubmit` hook — pure bash, <50 ms, no model — maintains a turn counter in `.roc/rocket/` and compares it with the lexicon's mtime. When the lexicon is stale by ≥N substantive turns, it injects one line of `additionalContext`: "lexicon stale — if new domain terms or decisions emerged, run rocket:context-update now". Injected context is a far stronger trigger than description-based auto-invocation (measured ~coin-flip reliability in the ecosystem). The nudge fires at most once per session.
3. **Session-boundary queue (catch-up)**: a `SessionEnd` hook appends `{transcript_path, ts}` to `.roc/rocket/pending.jsonl` (pure bash, no model). A `SessionStart` hook injects "K sessions await lexicon distillation" when the queue is non-empty. The skill, when invoked, also drains this queue (reads the queued transcript tails directly — they are plain JSONL at known paths), then truncates it. Nothing is ever dropped; processing is deferred, not skipped.
4. **Cost profile**: zero background model calls. Nudges cost ~50–80 tokens when they fire. One foreground update ≈ 2–5k tokens, only when warranted. Compare: each v1 hook fire was a full headless session (~15–30k tokens of startup) ending in a failed write.

**Open question for the user**: with Claude Code's built-in auto memory now covering the *personal* slice, the lexicon's unique remaining value is being a **committed, team-shared, reviewable** artifact. If that team-sharing value is not real for the user, the honest recommendation is to delete the subsystem entirely and rely on built-in memory + CLAUDE.md.

---

## 4. inbox-watch — root-cause analysis and redesign

### 4.1 Measured behavior (6.2-day session, May 5–12)

- **~287k tokens per tick** (3.3 messages/tick; dominated by cache-missed context re-reads), ≈ $0.03/tick on Haiku → **$4.23/day at full cadence**; ~95% of it spent confirming "no new mail".
- **~10% tick delivery**: 87 ticks observed where ~900 were expected. Four start/stop cycles needed manual intervention in the first 8 hours; the loop died with the session (last poll ever: May 12).
- **Parent-session context grew 0 → 160k tokens** with no compaction; every tick re-sent it uncached because the 10-min interval exceeds the 5-min prompt-cache TTL — the dominant, structural cost.
- Stale state bug: `pending_replies` retained "(profile missing — run /my-hand:tone-profile)" suggestions even after `tone.md` existed.

### 4.2 Root causes

1. **A model sits inside the polling loop.** Gmail is reachable only via MCP, and MCP tools require a model. So every poll — even empty — pays a subagent spin-up plus parent-session turns. Production systems (Inbox Zero, Superhuman, Fyxer, Jace) all do the inverse: deterministic arrival detection and pre-filtering, one classification per *message*, never per *tick*.
2. **10-min cadence > 5-min cache TTL** guarantees a full cache miss on every tick, for both the subagent and the growing parent context.
3. **`/loop` is a session-scoped timer, not a daemon**: documented expiry, jitter, death-with-session. Reliability cannot exceed the session's lifetime.
4. **Day-granular Gmail query** (`after:YYYY/MM/DD`) re-downloads the whole day every tick; the binary dedupes after the tokens are already spent.

### 4.3 Realism check (user asked for honesty)

- **Achievable and cheap**: watch → notify on "awaits a reply" → on-demand interactive draft.
- **Not realistic**: "the agent asks me my answers in the background". An unattended watcher cannot hold a synchronous Q&A with an absent user; no product does this. The honest equivalent: the classifier extracts, per flagged thread, the 1–3 questions a reply would need answered, and stores them; `/my-hand:inbox-reply` asks those questions interactively (AskUserQuestion) when the user shows up, then drafts. Same outcome, expensive part on demand only.
- **Not 100% classification accuracy**: nobody ships it. Plan a feedback file ("this sender never needs replies") folded into the classifier prompt.

### 4.4 Proposed redesign (target architecture)

**Shape**: take the model out of the loop entirely.

1. **Trigger**: `launchd` (macOS) runs the extended `inbox-poll` binary every ~5 min. No Claude session, no `/loop`, no `claude -p`. Survives reboots; catch-up is free (next run covers the gap).
2. **Stage 0 — fetch (0 tokens)**: the binary calls the Gmail API directly (own OAuth client; pierre@ is a Workspace account, so an *internal* app skips Google's restricted-scope verification). Incremental fetch via `history.list`/message IDs, not day-granular queries.
3. **Stage 1 — deterministic funnel (0 tokens)**: drop automated mail via standard headers (`Auto-Submitted`, `Precedence: bulk|list`, `List-Unsubscribe`, `List-Id`), category filters, "user in To:", sender-in-sent-history. Removes 70–90% of volume.
4. **Stage 2 — one batched Haiku call via the Anthropic API** (the binary, not a Claude session): survivors classified in a single structured-output request — `{reply: bool, sender, company, subject, questions[]}` — bodies truncated. ≈ **$0.06/day** at 50 mails/day.
5. **Stage 3 — notify + state (0 tokens)**: existing `osascript` notification; `pending_replies` (now including `questions[]`) written to `~/.roc/my-hand/inbox-state.json`.
6. **Draft flow**: `/my-hand:inbox-reply` gains one step — if the matched thread carries stored `questions`, ask them via `AskUserQuestion` before drafting. No-send guarantee unchanged.
7. **Command surface**: `/my-hand:inbox-watch` becomes the manager — `install` (writes the launchd plist), `uninstall`, `status`, `tick` (runs the binary once, foreground). The `inbox-watch-tick` skill, the `loop` usage, and the SessionStart bootstrap hook are deleted.

**Cost comparison**: ~$4.23/day (measured potential) → ~$0.06/day classification + on-demand drafting. Reliability moves from "session lifetime" to "launchd".

**New prerequisites to document (Hard rule 4)**: a Google OAuth client (internal Workspace app) and an Anthropic API key available to the binary. Note: as of June 15, 2026, headless/SDK usage bills against a metered credit on subscriptions — another reason to keep the per-poll path off `claude -p` entirely.

**Interim option** (if direct Gmail OAuth is postponed): replace `/loop` with a Desktop scheduled task (fresh session per tick, Haiku, survives restarts). Fixes reliability, not cost (~$3–4/day, ~96 fresh headless runs). Worth doing only as a stopgap; the structural fix is the binary-first design.

---

## 5. Proposed implementation order

Each batch is independently shippable; versions bump per the manifest rules.

| Batch | Content | Risk |
| --- | --- | --- |
| 1. Prompt amendments | spec-writer (polish pass, budget, adversarial stance), spec-maker (phases, TDD declaration, bounded discovery), pr-writer global budget, no-code hardening + spec carve-out | None — text only |
| 2. Scope/`rebase` mode | Shared scope-selection procedure copied into commit-writer, pr-writer, review | Low |
| 3. setup redesign | One-round detect→diff→confirm flow, marker-delimited idempotent block, CI-aware detection, decouple from lexicon | Medium |
| 4. Contextualisation v2 | Delete hook pipeline + binary; main-context skill; UserPromptSubmit staleness nudge; SessionEnd/SessionStart queue *(superseded by Decision 1 — system deleted instead of rebuilt)* | — |
| 5. inbox-watch v2 | Extend `inbox-poll` (Gmail OAuth, funnel, Anthropic API call, launchd install); rewrite inbox-watch command; extend inbox-reply with stored questions; delete tick skill + bootstrap hook *(superseded by Decision 2 — system deleted instead of rebuilt)* | — |

Decisions needed from the user before implementation — all resolved 2026-06-10, see the Decisions header:

1. Contextualisation: **resolved — subsystem deleted** (Decision 1).
2. inbox-watch: **resolved — system deleted**; the direct-Gmail-OAuth path was rejected (Decision 2).
3. `rebase` mode UX: **resolved — one-multiSelect commit picker confirmed** (Decision 3).
