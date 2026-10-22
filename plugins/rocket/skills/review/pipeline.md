# Review — pipeline contract

Non-interactive review for an orchestrator. Active when the first line of the prompt is `MODE: pipeline`. This file is self-contained: a caller may read it directly instead of loading `SKILL.md`. Never call `AskUserQuestion`, never end a turn on a question: open items go to `QUESTIONS` (the orchestrator can answer) or `BLOCKERS` (a human must decide), and the review proceeds on the most conservative reading.

Read-only, with teeth: never edit a file of the working tree, never `git fetch` or `pull`, no network traffic to any host but localhost. Allowed and expected, because they are what finds the defects a reading misses: run the project's tests through its verification command, mutate a guard to see whether a test fails, open a local browser on a change that touches layout or rendering — then restore everything you touched and leave the tree as you found it.

## Brief slots

- `BASE: <git ref>` — mandatory. Scope is exactly `git diff <BASE>`; no scope detection, no commit picker. Missing → return `BLOCKERS` only.
- `SPEC_PATH: <absolute path>` — optional. The approved spec. Absent → criterion (a) is reported as `spec-conformance · skipped · no spec supplied`; criterion (c) is bounded by the diff's evident intent instead.
- `DEFECT_CLASSES:` — optional. One class per bullet (name + one-line definition), swept in criterion (e).
- `CONVENTIONS: <paths>` — optional. The project's convention documents beyond `CLAUDE.md`, checked in criterion (f).
- `PRIOR_FINDINGS:` + `DELTA:` — optional, present from the second round on one change: the previous round's findings with their status (fixed, dismissed with a reason, open) and the diff since that round. See [Later rounds](#later-rounds).
- `ARTIFACT_PATH: <absolute path>` — optional. The return is also written there verbatim.

## Context

Before analysing, read: the full content of every changed file (not just the hunks), its sibling files, its import targets within the project, the project's `CLAUDE.md` (root and nested along the touched paths), the documents named in `CONVENTIONS`, the spec when supplied. Project conventions are law — flag the diff's divergence from them, never the project's own architecture.

## Criteria, in order

**(a) Spec conformance** — every `Done means` bullet and `Decisions` line implemented; every part listed under `Where` reached, no behavior change in a part listed as unchanged; every deviation declared in the diff or the brief; nothing built beyond the spec. Each gap is `CRITICAL`. Report per `Done means` bullet, `Decisions` line and `Where` row: met / not met / not assessable from the diff.

**(b) Tests** — each `Done means` bullet and each spec rule that changes observable behavior has a test that fails when that behavior breaks; a missing one is `WARNING`. Without a spec, the behavior the diff evidently adds is the reference. A test asserting a logging call, a query the code makes along the way, a constant value or internal structure — with no spec rule or project convention making it the behavior — is `WARNING`, fix: assert the observable outcome or delete the test. An uncovered line outside that behavior is not a finding, nor is the number of tests.

**(c) Correctness challenge, bounded to the spec** — do the diff's assumptions hold across callers, data flow, state transitions, migrations and the edge cases it touches without handling them; are rights and lifecycles complete for what it exposes. Propose a redesign only when it costs less code or less risk than what is written. A finding that would extend or contradict the approved spec is `SUGGESTION` with class `correctness beyond-spec`, never `CRITICAL`. The same applies to redesign ideas carried by the brief (a prior reviewer's note, an open discussion): assess each one and report it as `SUGGESTION · correctness beyond-spec` with a one-line verdict — never `CRITICAL`, never dropped, never turned into a `QUESTIONS` item.

**(d) Consistency** — duplication inside the diff or with existing code; divergence from sibling patterns (naming, structure, error handling, return shapes); vacuous assertions (a test that cannot fail); inline mocks where the project has fixtures or factories; dead code the diff introduces.

**(e) Defect classes** — when `DEFECT_CLASSES` is supplied, sweep the whole diff once per class, in the order given. Each class yields its findings or one explicit `<class> · no finding` line.

**(f) Conventions** — when `CONVENTIONS` is supplied, every divergence of the diff's own lines from a rule those documents state is a `WARNING` of class `conventions`, written `<file:line> — <rule as the document states it>`. A rule the project does not enforce on its pre-existing code, met by a line the diff only touches incidentally, is a `SUGGESTION`. Conformance to a decision the brief marks as settled is never a finding.

## Later rounds

With `PRIOR_FINDINGS` and `DELTA` in the brief, the review judges the change as a whole but grades by what moved: a `WARNING` or above rests on an unresolved prior finding or on a defect the delta introduced; a new observation on code the delta did not touch is a `SUGGESTION` unless it is a correctness defect; a prior finding dismissed with a reason is re-assessed against that reason, not re-opened as new. Prior notes the brief carries are returned as `correctness beyond-spec` with a verdict, never dropped.

## Reporting rules

- Every finding carries `severity` (`CRITICAL` | `WARNING` | `SUGGESTION`) and `confidence` (`high` | `medium` | `low`). Report everything, including low-confidence items: the caller filters, and self-filtering lowers recall.
- Every criterion and every defect class produces at least one line, `<class> · no finding` when clean.
- Concrete over vague: `file:line`, what is wrong, the fix as an intent (what to change, not a patch).
- `class` is one of `spec-conformance`, `tests`, `correctness`, `correctness beyond-spec`, `consistency`, `conventions`, or the defect class name as given in the brief.

## Return

Flat markdown: each key on its own line as `KEY:`, bullets under it, no code fences, no nested markup, nothing else.

- `FINDINGS` — one bullet per finding: `<severity> · <confidence> · <file:line> · <class> · <description> · fix: <intent>`; one bullet per clean criterion or class: `<class> · no finding`.
- `QUESTIONS` — bullets, or `none`.
- `BLOCKERS` — bullets, or `none`.

Example:

FINDINGS:
- CRITICAL · high · src/services/export-csv.ts:1 · spec-conformance · decision "exports are rate-limited per user" has no implementation and no declared deviation · fix: add the limiter or declare the deviation
- WARNING · high · src/services/export-csv.test.ts:42 · tests · Done means "an empty selection downloads an empty file" has no test · fix: add a test asserting the empty-file response for an empty selection
- SUGGESTION · medium · src/services/export-csv.ts:18 · correctness beyond-spec · streaming the rows would bound memory on large exports; the spec fixes an in-memory build · fix: raise as a follow-up card, not in this change
- WARNING · high · src/services/export-csv.test.ts:30 · consistency · inline mock of the repository while `test/factories/repository.ts` exists · fix: use the factory
- WARNING · high · src/services/export-csv.ts:27 · conventions · src/services/export-csv.ts:27 — "async retrieval functions are named fetch… or load…, never get…" (CONTRIBUTING.md) · fix: rename `getRows` to `fetchRows`
- correctness · no finding
- lint-disable · no finding
- fr-word · no finding
QUESTIONS: none
BLOCKERS: none
