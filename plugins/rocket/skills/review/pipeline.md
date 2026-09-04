# Review — pipeline contract

Non-interactive review for an orchestrator. Active when the first line of the prompt is `MODE: pipeline`. This file is self-contained: a caller may read it directly instead of loading `SKILL.md`. Never call `AskUserQuestion`, never end a turn on a question, never edit a file: open items go to `QUESTIONS` (the orchestrator can answer) or `BLOCKERS` (a human must decide), and the review proceeds on the most conservative reading.

## Brief slots

- `BASE: <git ref>` — mandatory. Scope is exactly `git diff <BASE>`; no scope detection, no commit picker. Missing → return `BLOCKERS` only.
- `SPEC_PATH: <absolute path>` — optional. The approved spec. Absent → criterion (a) is reported as `spec-conformance · skipped · no spec supplied`; criterion (c) is bounded by the diff's evident intent instead.
- `DEFECT_CLASSES:` — optional. One class per bullet (name + one-line definition), swept in criterion (e).
- `ARTIFACT_PATH: <absolute path>` — optional. The return is also written there verbatim.

## Context

Before analysing, read: the full content of every changed file (not just the hunks), its sibling files, its import targets within the project, the project's `CLAUDE.md` (root and nested along the touched paths), the spec when supplied. Project conventions are law — flag the diff's divergence from them, never the project's own architecture.

## Criteria, in order

**(a) Spec conformance** — every spec section and `Done means` bullet implemented; every deviation declared in the diff or the brief; nothing built beyond the spec; every file the spec names present. Each gap is `CRITICAL`. Report per section: met / not met / not assessable from the diff.

**(b) Pinning** — for each guard, condition or branch the diff adds, name the mutation (inverted condition, deleted branch, swapped operand) that the tests would not detect. A mutation detectable by simply deleting the code with tests still green is `CRITICAL`; a weaker one is `WARNING`. A pinned guard is stated as such (`no finding`).

**(c) Correctness challenge, bounded to the spec** — do the diff's assumptions hold across callers, data flow, state transitions, migrations and the edge cases it touches without handling them; are rights and lifecycles complete for what it exposes. Propose a redesign only when it costs less code or less risk than what is written. A finding that would extend or contradict the approved spec is `SUGGESTION` with class `correctness beyond-spec`, never `CRITICAL`. The same applies to redesign ideas carried by the brief (a prior reviewer's note, an open discussion): assess each one and report it as `SUGGESTION · correctness beyond-spec` with a one-line verdict — never `CRITICAL`, never dropped, never turned into a `QUESTIONS` item.

**(d) Consistency** — duplication inside the diff or with existing code; divergence from sibling patterns (naming, structure, error handling, return shapes); vacuous assertions (a test that cannot fail); inline mocks where the project has fixtures or factories; dead code the diff introduces.

**(e) Defect classes** — when `DEFECT_CLASSES` is supplied, sweep the whole diff once per class, in the order given. Each class yields its findings or one explicit `<class> · no finding` line.

## Reporting rules

- Every finding carries `severity` (`CRITICAL` | `WARNING` | `SUGGESTION`) and `confidence` (`high` | `medium` | `low`). Report everything, including low-confidence items: the caller filters, and self-filtering lowers recall.
- Every criterion and every defect class produces at least one line, `<class> · no finding` when clean.
- Concrete over vague: `file:line`, what is wrong, the fix as an intent (what to change, not a patch).
- `class` is one of `spec-conformance`, `pinning`, `correctness`, `correctness beyond-spec`, `consistency`, or the defect class name as given in the brief.

## Return

Flat markdown: each key on its own line as `KEY:`, bullets under it, no code fences, no nested markup, nothing else.

- `FINDINGS` — one bullet per finding: `<severity> · <confidence> · <file:line> · <class> · <description> · fix: <intent>`; one bullet per clean criterion or class: `<class> · no finding`.
- `QUESTIONS` — bullets, or `none`.
- `BLOCKERS` — bullets, or `none`.

Example:

FINDINGS:
- CRITICAL · high · src/services/export-csv.ts:1 · spec-conformance · spec section "Rate limiting" has no implementation and no declared deviation · fix: add the limiter named in the spec or declare the deviation
- CRITICAL · high · src/services/export-csv.ts:42 · pinning · deleting the empty-selection guard keeps all tests green · fix: add a test asserting the empty-file response for an empty selection
- SUGGESTION · medium · src/services/export-csv.ts:18 · correctness beyond-spec · streaming the rows would bound memory on large exports; the spec fixes an in-memory build · fix: raise as a follow-up card, not in this change
- WARNING · high · src/services/export-csv.test.ts:30 · consistency · inline mock of the repository while `test/factories/repository.ts` exists · fix: use the factory
- correctness · no finding
- lint-disable · no finding
- fr-word · no finding
QUESTIONS: none
BLOCKERS: none
