# `Done means` section in spec-writer output

## Problem

- Specs produced by `spec-writer` state a solution but no acceptance oracle: nothing in the document lets a human or agent decide, binarily, whether the shipped work is done.
- `spec-maker` declares completion after the consumer `CLAUDE.md` verification command passes — a universal gate that says the code is healthy, not that the feature works.
- Misalignment on intent is discovered after the full ~80-line spec is written, wasting a full drafting cycle when 3 lines would have caught it.

## Done means

- Every spec `spec-writer` produces contains a `Done means` section immediately after `Problem`.
- `spec-writer` never writes any other spec section before the user has explicitly approved `Done means`.
- `spec-maker` reports per-bullet pass/fail against `Done means` before declaring completion.
- `/rocket:review` reports `Done means` conformance as its first criterion when a related spec exists.
- `rocket` plugin version is bumped.

## Solution

Add a `Done means` section to the spec template enforced by `spec-writer`, gate spec drafting behind explicit user approval of that section (Kiro-style phase approval), and make both downstream consumers (`spec-maker`, `review`) use it as the per-feature acceptance oracle. Four files change:

1. `plugins/rocket/agents/spec-writer.md` — template gains the section; workflow gains the approval gate.
2. `plugins/rocket/agents/spec-maker.md` — completion requires every `Done means` bullet to pass, in addition to the verification command.
3. `plugins/rocket/skills/review/SKILL.md` — new first review criterion confronting the diff against the spec's `Done means`.
4. `plugins/rocket/.claude-plugin/plugin.json` — version bump (behavioral change).

Rationale carried from research:

- A verifiable goal is an observable state confirmable without the judgment of the agent that produced the work; self-grading is the degenerate case.
- If two people could disagree on whether a bullet is met, it is not specific enough.
- The name is `Done means`, not "Definition of Done": the agile DoD sense (universal checklist) is already covered by the consumer `CLAUDE.md` verification command; this section is per-feature acceptance criteria.

NOT built: no EARS or user-story format (too heavy for the ~80-line spec philosophy), no numeric cap on bullet count (numeric budgets erode — structure constrains), no machine-parseable checklist format, no change to `my-hand`.

## Alternatives considered

- Reuse `Contracts` as the oracle → rejected: `Contracts` is the exhaustive map (every invariant), not the destination; verifying dozens of invariants is not a completion check a human scans in seconds.
- Name it "Definition of Done" → rejected: collides with the agile universal-checklist sense already served by the verification command.
- Post-hoc approval (write spec, then confirm `Done means`) → rejected: the gate exists to align on 3 lines before investing 80; retroactive approval is worthless.
- EARS / GitHub Spec Kit user-story format → rejected: validates the approval-loop idea, but the format is too heavy for this repo's spec style.
- Cheapest circumvention — ask the user to state acceptance criteria in the prompt → rejected: unenforced, evaporates by the time `spec-maker` or `review` runs; the spec is the durable carrier.

## Contracts

### `Done means` section (spec template)

| Property | Rule |
|---|---|
| Position | Immediately after `Problem`, before `Solution` |
| Form | Bullets only; no prose, no tables, no numbering |
| Bullet content | One user-observable outcome, binary pass/fail |
| Forbidden | Vague words ("properly", "gracefully", "correctly"), implementation detail, references to internal code structure |
| Expression | Radically minimal: each bullet reduced to its essence, instantly readable — a hard criterion equal in weight to verifiability |
| Count | No numeric cap; structure constrains, not budgets |
| Relation to `Contracts` | Must not paraphrase or summarize it — `Done means` is the highest-level oracle (destination), `Contracts` the exhaustive map |

### Behavior invariants

- `spec-writer`: elicitation questions complete → the proposed `Done means` is submitted alone for approval; nothing else of the spec exists yet.
- `spec-writer`: explicit user approval of `Done means` → drafting of the remaining sections may start; absence of approval blocks all spec writing.
- `spec-writer`: later feedback changes scope → revised `Done means` is re-submitted for approval before any other spec modification.
- `spec-writer` polish pass: a bullet that self-grades (only the producing agent can judge it), uses a vague word, or restates a `Contracts` invariant → rewritten or cut.
- `spec-maker`: before declaring completion → every `Done means` bullet is checked and reported pass/fail; any fail blocks the completion claim. The consumer `CLAUDE.md` verification command remains mandatory — `Done means` adds to it, never replaces it.
- `review`: a related spec is found → `Done means` conformance becomes Criterion 1 (existing criteria shift by one, report template updated); each bullet is confronted against the diff and reported met / not met / not assessable from the diff. No spec found → the criterion reports "No related spec." and the review proceeds.
- `review` spec discovery: a spec referenced in the conversation or diff wins; otherwise scan the project's `specs/` directory (when present) for a spec whose topic matches the changed files; ambiguity → ask the user, never guess.
- Plugin manifest: `plugins/rocket/.claude-plugin/plugin.json` version `2.2.0` → `2.3.0`.

## Implementation notes

- `spec-writer.md` template list: insert the `Done means` entry between `Problem` and `Solution` with the rules from the table above, compressed to the style of the existing entries. Add the approval gate as explicit numbered steps in `## Workflow` (between current steps 3 and 4) and extend the polish pass and `## Quality criteria` with the bullet-quality checks.
- `spec-maker.md`: extend `## Implementation Process` Phase B and `## Workflow` step 7 — completion report includes the per-bullet pass/fail list. Wording must state the two-gate model: verification command = universal DoD, `Done means` = per-feature acceptance.
- `review/SKILL.md`: add the criterion, renumber Criteria 1-8 to 2-9, update the `Code Review Report` template section list accordingly. Keep the criterion stack-agnostic — no hardcoded spec path beyond the optional `specs/` scan.
- All three edits are prose-only; follow each file's existing section structure and tone. No new files.
