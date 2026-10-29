# Studio — pipeline contract

Non-interactive critique of a screen, or comparison of a built screen with its proposal, for an orchestrator. Active when the first line of the prompt is `MODE: pipeline`. This file is self-contained: a caller may read it directly instead of loading `SKILL.md`. Never call `AskUserQuestion`, never end a turn on a question: open items go to `QUESTIONS` (the orchestrator can answer) or `BLOCKERS` (a human must decide), and the run proceeds on the most conservative reading.

Read-only. Read the critique corpus (`~/.roc/rocket/studio/`) and the product language (`design/language.md`) and the proposal; write to none of them, because only the operator's own remarks teach studio. Never discover, record or replay a preview recipe, which needs the operator's go; never start a preview or an environment — the orchestrator brings up its own and names the screen in `SCREEN`. Never read or write a conventions block in the project's `CLAUDE.md`. Every message and key is in English.

## Brief slots

- `CHECK: critique | fidelity` — mandatory. Missing, or anything else — a creative entry included (found, decline, evolve) → return `BLOCKERS` only: `creative entries need the operator at every checkpoint: run /rocket:studio interactively`.
- `SCREEN` — mandatory. How to show the screen: an address, a story, or a file. Missing → `BLOCKERS` only.
- `PROPOSAL` — the proposal to compare against; mandatory for `fidelity`, missing → `BLOCKERS` only.
- `SCREEN_TYPE` — optional; otherwise deduced from the closed list in `~/.roc/rocket/studio/types.md`. None fits, or no list → no past remarks, and a `QUESTIONS` bullet naming the type you would add.
- `TASKS` — optional; tasks in plain words for the end-user agent. Absent → no walk.

## Run

1. Check the slots.
2. No `Agent` tool (the subagent nesting limit is reached) → return `BLOCKERS` only: `studio's workers cannot be dispatched: the subagent nesting limit is reached`.
3. Browser tooling: whether your tools can open a page, operate it and capture it → `BROWSER: yes | no`.
4. Reach `SCREEN` once. Unreachable, or no browser tooling → the critic works from code and `CONFIDENCE` reads `reduced · <why>`.
5. Dispatch `rocket:studio-critic` as a plain subagent — foreground, no `name`, no team — with flat `KEY: value` lines: `MODE` (the `CHECK`), `SCREEN`, `FRAME` and `CATALOG` (`frame.md` and `catalog.md`, absolute paths, in the same directory as this file), `LANGUAGE` (path or `none`), `TASTE` (path of `~/.roc/rocket/studio/taste.md` or `none`), `PAST_REMARKS` (the `active` entries of `~/.roc/rocket/studio/remarks/<screen type>.md` as bullets; never another type's file), `INTENT` (the language's intent sentence or `none`), `PROPOSAL` (fidelity) and `PROTOTYPE` (the location in the proposal's Evidence, or `gone`), `OUT_DIR` (a temporary directory outside the repository), `COPY_LANGUAGE` (the language of the screen's interface copy, read from it), `BROWSER`. With `TASKS`, dispatch `rocket:studio-end-user` in the same message with `PROTOTYPE: <SCREEN>`, `TASKS`, `VARIANTS: none`, `BROWSER`.
6. Return the workers' results in the format below: the critic's `FINDINGS`, `GAPS`, `NOT_COMPARED` and `CONFIDENCE` as they are, each of its accessibility points as a finding `accessibility · <its rule or opinion> · <point> · fix: none`, and the end-user agent's `TASKS` as `WALK` without the variant field. Either worker's reduced confidence makes `CONFIDENCE` reduced.

## Return

Flat markdown: each key on its own line as `KEY:`, bullets under it, no code fences, no nested markup, nothing else. Every key present, `none` when empty.

- `FINDINGS` — `<zone> · <rule: frame firm "<title>" | frame default "<title>" | language | taste | past remark | opinion> · <what> · fix: <intent>`. A frame rule is cited by its exact title; a finding with no rule reads `opinion`.
- `GAPS` — fidelity only: `<state> · <what differs> · seen by: capture | operation | recording | code`.
- `NOT_COMPARED` — fidelity only: states the session could not reach, or `none`.
- `WALK` — with `TASKS` only: `<task> · done | hesitated | stuck · where: <zone> · misleading word: <word | none>`.
- `CONFIDENCE` — `full`, or `reduced · <why>`.
- `QUESTIONS` — bullets, or `none`.
- `BLOCKERS` — bullets, or `none`.

Example (the rule title is illustrative):

FINDINGS:
- row actions · frame firm "Make every action reachable by keyboard" · the row menu opens on hover only; tabbing skips it · fix: give the menu a focusable trigger in each row
- column headers · past remark · headers are bolder than the data they label ("les en-têtes crient") · fix: lower the headers' weight below the data's
- empty state · opinion · the illustration takes more room than the first action · fix: lead with the action
GAPS: none
NOT_COMPARED: none
WALK:
- archive a closed ticket · hesitated · where: row menu · misleading word: "Clore"
CONFIDENCE: full
QUESTIONS: none
BLOCKERS: none
