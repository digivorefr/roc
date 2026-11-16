# Studio: any medium, with a bench of tools it equips itself with

## What

`/rocket:studio` proved itself on web interfaces and stalls elsewhere.
Eight live runs (74 worker dispatches, 31.9 agent-hours, 22.2M worker tokens) show why: no entry covers a non-web piece, the frame only knows screens, and workers rebuild their tools at every run and keep none.
The type-design run spent 3.7 agent-hours and produced no font file; on the two runs with sound, no agent could hear the result; the same three tooling obstacles were rediscovered in 3 to 4 runs each.
This change keeps studio's method (distinct sources, restated decisions, the operator's eye, the corpus) and makes the medium a parameter: one sheet per medium, written by studio on first contact and amended by the operator.
It adds a bench where each tool studio needs is researched once, proven on a probe, recorded and replayed.
Web interface design stays as the first medium, unchanged in behaviour.
Cost: one new agent, two agents renamed, one more checkpoint the first time a medium or a tool is met, and tools installed in the operator's home folder.

## Where

| Part | What changes |
|---|---|
| `/rocket:studio` skill | The workflow speaks of a piece in a medium instead of a screen. Start gains the medium line and the bench check. Restatement gains the deliverable line. The description triggers on any design request, not only interfaces. |
| Medium sheets (new) | The web sheet ships with the skill and points to the existing frame and catalog. Every other sheet is written on first contact and kept in the operator's home folder. |
| Bench (new, per operator) | One tool sheet per tool, and the tools studio installed, in the operator's home folder. |
| `studio-scout` agent (new) | Researches a medium and drafts its sheet; researches a tool, proves it on a probe and drafts its tool sheet. |
| `studio-prototyper` → `studio-maker` | Makes the piece in the medium's material, and makes raw materials. Same confrontation round. |
| `studio-end-user` → `studio-audience` | Uses the piece the way its public does: operates a screen, reads a page, listens when it can. Says what it could not perceive. |
| Intent, critic, lexicon, archivist | Receive the medium sheet where they received the frame and the catalog. |
| Corpus | Screen types become piece types, each tied to a medium. Existing remarks keep their type under the web medium. |
| Rocket README and plugin manifest | Document the media, the bench and its install location; minor version bump. |

Unchanged: the frame and the catalog (they become the web sheet's rules), the product language's lexicon and intent, proposals, the preview recipe, pipeline mode and its slots, spec-writer, spec-maker, review.

## Decisions

Settled by the operator:

- Studio writes a medium sheet the first time it meets a medium; the operator amends it. No medium waits for a sheet written in advance.
- A design application reachable from the session (Affinity through its connector, on the operator's machine) is one tool of the bench, never a mandatory path. A worker builds in HTML, SVG or a script whenever that is simpler.
- Such an application serves two uses first: making a logo, and making raw materials for the final piece.

Proposed, each refusable:

- A medium is what the piece is made of and how its public meets it: web interface, type, identity mark, printed page, slide deck, image, sound. Studio names the medium in one line the operator can refuse, next to the entry line.
- A run makes one piece in one medium. A piece that needs another medium's output (a logo in a page, a sound in an interface) takes it as a raw material.
- A medium sheet states four things: the rules of the craft, the material a piece is built from, how the operator is shown the piece, and how agents judge it.
- Rules in a sheet have the frame's shape: a title, a source, a check for a violation, and a mark `firm` or `default`.
- A sheet studio just wrote is a draft. Every rule in a draft is `default`; only the operator's amendment makes a rule `firm`. A weak first sheet therefore never overrides the operator.
- The scout drafts a sheet from recognised references of the craft and cites each one. It is shown as a checkpoint before the first intents round in that medium.
- The web sheet is the existing frame and catalog. Its behaviour does not change, and it is the only sheet that ships.
- A piece type and an aspect belong to a medium. The closed list keeps growing only on the operator's confirmation.
- The product language keeps one lexicon, one intent sentence and one do/avoid for every medium. Signature and motion are written per medium, because stroke and timing do not transfer from a screen to a printed page.
- A piece can be made for a product that has no language (a typeface, a logo). The entry line says so, and the run ends on a proposal without founding a language.
- Every restatement that opens a run carries the line `deliverable: <what file or files> made with <tool>`. The two costliest misreads of the past runs were about what would be delivered.
- The bench holds one tool sheet per tool: what need it serves, how to call it, how to check it works, whether several workers may use it at once, what it cannot do, and the pitfalls met so far.
- When a need has no tool sheet, the scout researches a tool, and studio states it in one refusable line: the tool, where it installs, how it is checked. Nothing is installed before the go.
- Studio installs only under the bench in the operator's home folder. Never globally, never in the project.
- A tool the operator must start (an application, an environment) is never started by studio: it asks and waits, as for a preview environment.
- A tool that is a session capability (a connector, browser tooling) is discovered from the session's tools and recorded the same way. No skill or agent file names a specific application.
- A tool marked exclusive is held by one worker per dispatch; the brief names the holder. Workers dispatched together never share it.
- A pitfall met during a run (a frozen animation in a hidden pane, a local file the browser refuses) is added to the tool sheet when the run ends, so the next run reads it instead of meeting it again.
- A tool that keeps its own memory (a script library, recorded hints) is used for it; the tool sheet points there instead of copying.
- Probe: before the first intents round on a draft medium sheet or an unproven tool, the maker produces the smallest real deliverable end to end (one glyph compiled into a font file, two seconds of rendered sound, one exported page) and studio shows it. A probe that fails stops the run with what is missing.
- A proven tool is not probed again; its tool sheet records the date and the deliverable of the last successful check.
- Raw material: an image, a mark, a texture, a font, a sound that the piece uses. It is made once, kept with the run, and reused by the intents, the maker and the study page.
- A raw material that carries identity (a logo, a typeface) gets its own checkpoint. An accessory one (a background texture) is listed at the piece's checkpoint only.
- A validated raw material that belongs to the product is copied next to the proposals and committed; the others are removed with the run.
- Each medium sheet names its proof instruments: what an agent can measure or capture to judge the piece (frame sampling for motion, a compiled specimen for type, a rendered file and its measurements for sound, an export at final size for print).
- What no instrument covers is said at the checkpoint as `judged by you alone: <what>`. An agent never reports on something it could not perceive.
- The audience agent's report states per task how it met the piece: operated, read, heard, or not perceived.
- Study page: on request, the maker lays out a run's intents or variants as one page the operator can share for comments. It is a piece in the web medium made from the run's own returns, with no intents round.
- Pipeline mode stays limited to critique and fidelity, and never writes a medium sheet, a tool sheet or the corpus.

## Alternatives rejected

- A design application as the place where every non-web piece is built — refused by the operator; it is a tool, and HTML or SVG is often simpler.
- Opening a medium only on a sheet written in advance — refused by the operator; studio drafts, the operator amends.
- One skill per medium — the method is the same, and the corpus and the language would split.
- Leaving tools to each worker, as today — the same obstacles were rediscovered in 3 to 4 runs, and nothing produced a font file.
- Installing tools globally or in the project — a global install changes the operator's machine for good; a project install lands in a repository that did not ask for it.
- Running the three intents one after another inside an exclusive tool — triples a round that already has a 23-minute median, for a tool the intents rarely need.
- Firm rules in a sheet studio wrote itself — a wrong firm rule would refuse the operator's remarks.
- A raw-material agent of its own — the maker already builds in the medium's material.

## Done means

- A request for a typeface, a logo or a printed page starts studio and states its medium in one line before anything runs.
- A request for a web screen behaves as before this change: same entries, same checkpoints, same files.
- The first run in a medium without a sheet shows the drafted sheet, with a cited source per rule, before any intent is dispatched. The second run in that medium does not show it again.
- No rule of a drafted sheet is cited as firm until the operator has amended the sheet.
- The opening restatement of every run holds a `deliverable:` line naming the file type and the tool.
- A need with no tool sheet produces one refusable line naming the tool, its install location and its check. Refusing it installs nothing.
- After a go, the tool is found under the bench in the operator's home folder and nowhere else.
- The next run that has the same need calls the tool without asking and without researching it.
- On an unproven tool, the operator sees a real file of the deliverable's type before the intents round. When the tool cannot produce it, the run stops and says what is missing.
- With an application the operator must start and that is down, studio asks for it and starts nothing.
- Two workers dispatched together never both receive an exclusive tool.
- A pitfall reported by a worker in one run appears in that tool's sheet, and the next run's brief carries it.
- A logo made during a run is shown at its own checkpoint before the piece that uses it.
- After a validated run, a product's raw materials are next to its proposal; no other raw material remains in the project.
- A checkpoint on a piece with sound says which part was judged by the operator alone, and no agent report describes how it sounds unless an instrument measured it.
- A run on a machine without any design application completes, using HTML, SVG or scripts.
- Asking to share a run's intents gives one page holding all of them, and dispatches no intent worker.
- A pipeline critique leaves every medium sheet and tool sheet unchanged.

## Reference

### Medium sheet

| Section | Content |
|---|---|
| Medium | Its name, and `draft` or `amended` with the date |
| Rules | Title, source, violation check, `firm` or `default` |
| Material | What a key image and a final piece are built from, and the fallback |
| Show | How the operator sees or hears a key image and the piece |
| Judge | The proof instruments, and what stays with the operator |
| Deliverable | The file types a run ends on |
| Raw materials | The usual ones, and which carry identity |
| Piece types and aspects | The closed list for this medium |

### Tool sheet

| Field | Content |
|---|---|
| Need | What it is used for, in plain words |
| Kind | `installed` (by studio, under the bench), `session` (a connector or built-in tooling), `application` (the operator starts it) |
| Call | The command or the tool names |
| Check | How to tell it works |
| Concurrency | `parallel` or `exclusive` |
| Limits | What it cannot do, where it may read and write |
| Pitfalls | One line each, dated |
| Proven | Date and deliverable of the last successful probe |

### Storage

| What | Where | Committed |
|---|---|---|
| Web medium sheet | With the skill | Shipped |
| Other medium sheets | `~/.roc/rocket/studio/media/` | Outside every repository |
| Tool sheets and installed tools | `~/.roc/rocket/studio/bench/` | Outside every repository |
| Raw materials of a run | The checkout's `.roc/rocket/studio/materials/` | No |
| Validated product raw materials | `design/materials/` | Yes |

### What the past runs give as first tool sheets

| Need | Met in | Today |
|---|---|---|
| Capture a moving piece | 5 runs | Rebuilt each time: player, slow motion, state in the address, frame sampling |
| Open a local file in the browser | 3 runs | Refused; a local server or a scripted browser improvised |
| Several workers in one browser | 4 runs | Collisions; a private tab asked for in the brief |
| Compile a font | 1 run | No tool; outlines kept as data, no font file |
| Hear a sound | 2 runs | No tool; the operator was the only check |
| Vector, layout, retouching, image generation, export to print formats | 0 runs | Available on the operator's machine through a design application's connector; untested by studio |

## Open

- Generated sound needs an outside model and an account. Until the operator picks one, sound is synthesised by script.
- A sketch round before full key images would cut the intents' share of the cost (40% of worker tokens, the same idea returned twice in 3 runs). Left out of this change.
- The names `studio-maker`, `studio-audience` and `studio-scout` are proposals.

## Risks and rollback

- Whether a plugin's agents see the session's connectors is not established. If they do not, only the orchestrator can call such a tool, and raw materials made with it are made by studio on the maker's written instructions.
- A drafted medium sheet can be poor in a craft the operator cannot correct. The probe and the `default`-only rule limit the damage; they do not make the sheet good.
- A tool that installed correctly can stop working after a system update. Its check runs before each use, and a failed check sends it back to research.
- An application that restricts files to one folder forces a copy step; a failed copy must stop the run instead of leaving the deliverable outside it.
- Renaming two agents breaks any brief that names the old ones. Only studio dispatches them.
- Rollback: reverting the rocket version restores the web-only skill. Medium sheets, tool sheets and installed tools stay in the operator's home folder, unread.
