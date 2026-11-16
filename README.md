# Roc — Claude Code marketplace

A Claude Code marketplace bundling AI-assisted development plugins. Currently ships two plugins:

- **Rocket 🚀** — stack-agnostic skills and agents that help a senior developer write specs, implement them, review changes, and produce commit and PR messages.
- **my-hand 🖐** — personal-expression toolkit: reMarkable page capture, email voice profile, and voice-grounded Gmail reply drafts. macOS-arm64 only; sanctioned non-portability exception per the repo's authoring rules.

Rocket is opinionated: each project that uses it should declare its own test command, stack conventions, and quality gates in its `CLAUDE.md` so the agents read them instead of carrying hardcoded assumptions. Run [`/rocket:setup`](#rocketsetup) to bootstrap that block interactively.

## Installation

From inside Claude Code:

```text
/plugin marketplace add digivorefr/roc
/plugin install rocket@roc
/plugin install my-hand@roc      # optional, macOS-arm64 only — useful with a reMarkable 2 and/or a Gmail MCP server
```

From Claude Desktop: open **Customize → Plugins personnels**, click **Ajouter une marketplace**, paste `digivorefr/roc` in the URL field, then install the desired plugin from the marketplace listing.

## Rocket 🚀

### Agents

Agents are invoked via the `Task` tool (or by asking Claude to "use the spec-writer agent").

#### `rocket:spec-writer`

Writes a functional specification for a topic, anchored on existing patterns of the target codebase: what changes, where, the decisions a reader can refuse, the alternatives rejected, `Done means` (acceptance criteria), risks and rollback — no file references. Submits its `Decisions` and `Done means` alone for approval before drafting the spec.

- Trigger: `write a spec with rocket:spec-writer about ...`
- Refine: `relaunch spec-writer with these details: ...`
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `ARTIFACT_PATH:` (optional `EVIDENCE_PATH:` for the sources of platform facts) — first dispatch returns `POINTS` / `DELIVERABLE` / `COST`, a resume with `FRAMING: done` writes the spec to the path; questions come back as `QUESTIONS` (product, cost or taste points prefixed `Tier P:` with a recommended default) / `BLOCKERS`, never as a live question.

#### `rocket:spec-maker`

Implements a specification, plan, or detailed instructions autonomously, then runs the project's verification commands.

- Trigger: `implement with rocket:spec-maker from specs/<file>.md`
- Pipeline (orchestrators): prompt starting with `MODE: pipeline`, optional `COVERAGE_CMD:` / `SELF_CHECK_CMD:` / `CONVENTIONS:` / `SCOPE_LOCK:` slots — returns `SUMMARY`, `DEVIATIONS`, `CHANGED_FILES`, `COVERAGE`, `SELF_CHECK`, `EVIDENCE` (each new test with the mutation that made it fail), `QUESTIONS`, `BLOCKERS`. Tests cover what the spec promises; coverage gaps are reported, not filled for their own sake; infrastructure files change only when the spec says so.

The agent expects project-specific conventions (test command, lint rules, error-handling style) to be declared in the project's `CLAUDE.md`. Run [`/rocket:setup`](#rocketsetup) to generate that block.

#### `rocket:pr-rebaser`

Worker of [`/rocket:rebase-prs`](#rocketrebase-prs), dispatched by it only: rebases one PR in its own worktree, reconciles it with what was merged meanwhile, validates the result and returns a structured report. Never pushes.

#### Studio workers

Seven workers of [`/rocket:studio`](#rocketstudio), dispatched by it only, each fed a distinct source so their blind spots do not overlap:

- `rocket:studio-scout` — equips studio for a craft it has not practised: drafts a medium's sheet from recognised references, each rule cited; researches the tool a need calls for, installs it under your bench after your go, checks it and drafts its tool sheet.
- `rocket:studio-lexicon` — the product's words (objects, relations, actions, events) from its domain docs, code and your words; renames flagged, never applied.
- `rocket:studio-archivist` — the language an existing product already speaks: observed intent, signature, motion, words in use, inconsistencies, design system gaps.
- `rocket:studio-intent` — one intent and its key image from one source: the subject's world, your references, or a deliberate counterpoint. Three instances run in parallel.
- `rocket:studio-maker` — the piece in its medium's material: a throwaway prototype of one screen or flow, or another medium's real deliverable, every state and transition, three ways considered before one is kept; corrects once, adds variant switches; also makes the probe, the raw materials and the study page.
- `rocket:studio-critic` — operates the piece and critiques it against its medium sheet (for the web, the frame and the catalog), the language, your taste rules and your past remarks on the same piece type; every finding names its rule or reads `opinion`, and what it could not perceive is said. Also compares a built screen with its prototype.
- `rocket:studio-audience` — the audience agent: sees only the piece and the tasks, meets the piece the way its public does (operates a screen, reads a page, listens when a tool lets it), reports where it hesitated, got stuck or was misled by a word, across variants, and what it could not perceive.

### Skills

Skills can be invoked explicitly with `/rocket:<name>` or auto-triggered when the description matches the request.

#### `/rocket:commit-writer`

Proposes 3 inline commit messages from the current diff.

- `/rocket:commit-writer`
- `/rocket:commit-writer only for these files: ...`
- `/rocket:commit-writer rebase` — pick which commits since the default branch (plus uncommitted changes) define the scope; useful before a squash or rebase.

#### `/rocket:pr-writer`

Proposes a structured, product-focused PR description organised by topic, ready to copy-paste. Capped at 1-3 topics and ~30 lines.

- `/rocket:pr-writer`
- `/rocket:pr-writer rebase` — same commit picker as commit-writer.

#### `/rocket:review`

Reviews uncommitted/unpushed changes against nine criteria: `Done means` conformance when a related spec exists, solution challenge, DRY, contiguous patterns, integration with existing conventions, test coverage, dead code, documentation drift, UI coherence. Produces a structured report.

- `/rocket:review`
- `/rocket:review rebase` — same commit picker as commit-writer.
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `BASE:` follows the self-contained [`pipeline.md`](plugins/rocket/skills/review/pipeline.md) contract — fixed scope, four criteria plus caller `DEFECT_CLASSES` and `CONVENTIONS`, later rounds graded by `PRIOR_FINDINGS` / `DELTA`, every finding with severity and confidence, no interaction; read-only but free to run the tests, mutate a guard or open a local browser.

#### `/rocket:rebase-prs`

After a PR is merged, rebases the other open PRs of a GitHub repository onto their moved base. You pick the PRs; a `rocket:pr-rebaser` worker per PR rebases it in its own worktree, reconciles it with everything merged since it branched (the merged side wins on what it changed, the goal is the benefit of both), checks the result against the PR's spec (`specs/` file or Notion link) and the project's verification command, and hands every uncertain resolution back to you. Each push waits for your yes. Stacked PRs are handled parents first; an interrupted run can be resumed.

- `/rocket:rebase-prs`

Manual-only — never auto-triggered.

Prerequisites:

- **GitHub access**: the GitHub connector (official server) or the `gh` CLI logged in; each operation uses the connector when it has the tool, `gh` otherwise.
- Optional: the **Notion connector**, for PRs whose spec is a Notion page.
- Gitignored files the tests need (`.env`, …) must be listed in the project's `.worktreeinclude`, or the workers' worktrees will not have them.
- Rebased commits are created unsigned; a repository that requires signed commits refuses them or blocks the merge.
- Workers run the project's install and verification commands in each worktree; their commands prompt for permission unless your permission mode or rules allow them.

#### `/rocket:studio`

Designs a piece in any medium — a web interface, a typeface, a logo, a printed page, a deck, an image, a sound — with the rules of its craft, distinct sources of inspiration, and your eye at three or four checkpoints. The medium is a parameter, carried by one medium sheet: the web sheet ships with the skill (a frame of interface craft, `references/frame.md`, and a catalog of ways to solve interface problems, `references/catalog.md`); any other is drafted from cited references the first time studio meets the medium, shown to you once, and yours to amend — until you do, none of its rules is firm. Entries are picked from what it finds and stated in one line you can refuse, next to the medium: found a product's language from scratch, found it from the existing product, decline one piece within the language, make a piece for a product that has no language, critique a piece, compare a built screen with its proposal. Every decision you give in free text comes back as one refusable line, the opening one naming the deliverable and its tool, and nothing runs before your go. Your checkpoint remarks build a critique corpus that later critiques cite. A web decline ends with a proposal for `rocket:spec-writer`, and prototype code never ships; elsewhere the run ends on the deliverable files and their proposal.

Studio equips itself: each tool a medium needs (compile a font, render a sound, export a page, capture motion) is researched once, stated in one line you can refuse, installed only under your bench, proven on a real file before anything is designed, recorded as a tool sheet with the pitfalls met, then replayed without asking. What no tool lets an agent perceive is said at the checkpoint as `judged by you alone`.

- `/rocket:studio`, "design the settings screen", "draw a logo", "critique this screen", "conçois l'écran …", "dessine une typo"
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `CHECK: critique | fidelity` + `SCREEN:` (plus `PROPOSAL:` for fidelity, optional `SCREEN_TYPE:` and `TASKS:`) follows the self-contained [`pipeline.md`](plugins/rocket/skills/studio/references/pipeline.md) contract — returns `FINDINGS`, `GAPS`, `NOT_COMPARED`, `WALK`, `CONFIDENCE`, `QUESTIONS`, `BLOCKERS`, asks nothing, writes nothing (no medium sheet, no tool sheet, no corpus); a creative entry returns a blocker. Web medium only.

Files:

- `design/` at the repository root — the product language, the proposals with their captures and deliverable files, and the product's validated raw materials (`design/materials/`); committed.
- `~/.roc/rocket/studio/` — your critique corpus, taste rules and the closed list of piece types and aspects, each tied to a medium (screen types recorded earlier are the web medium's), shared across projects.
- `~/.roc/rocket/studio/media/` — the medium sheets studio drafted and you amended, one per medium.
- `~/.roc/rocket/studio/bench/` — one tool sheet per tool, and every tool studio installed, each in its own folder. Nothing is installed globally or in a project; deleting a tool's folder and its sheet uninstalls it.
- `<project>/.roc/rocket/studio/` — run state, self-contained prototypes, unchosen key images and the run's raw materials; the main checkout's copy also holds the preview recipe, which worktrees replay. Keep `.roc/` gitignored.

Notes:

- No setup step: on first contact studio discovers how to show a screen or a story from the project itself, states it in one line, and records it on your go. It starts a story or dev server on its own; an environment the project's scripts bring up is yours to start.
- No tool is required: a run completes with HTML, SVG and scripts. A connector to a design application, when the session has one, is optional: studio discovers it from the session's tools and records it on the bench like any other tool, never as the mandatory path. An application you must start is never started by studio: it asks and waits.
- A raw material the piece uses (a logo, a texture, a font, a sound) is made once per run; one that carries identity gets its own checkpoint. Ask to share a round's intents or variants and you get one page holding all of them.
- Browser tooling in the session is optional: without it, you open prototypes and key images from the paths given, captures are missing, and critiques state reduced confidence.
- Writes happen after your go, in a later turn, so each one prompts unless your permission rules allow it: add `Edit(design/**)`, `Edit(.roc/rocket/studio/**)` and `Edit(~/.roc/rocket/studio/**)` to your allow rules; the last one covers the medium sheets and the bench. Installing a tool and running its check are commands, prompted the same way. From a worktree, the preview recipe is written to the main checkout's `.roc/`, outside these patterns.
- Each creative run costs several rounds of agents.

#### `/rocket:condense`

Condenses a text, file, or conversation element into its essence without information loss: a few lines of essence, then bullets grouped by concept with causal links spelled out, then a set-apart loss-check block comparing input and output. Output in the language of the source. Auto-triggers on "shorten", "synthesize", "TL;DR", "fais plus court", "synthétise", "résume".

- `/rocket:condense specs/<file>.md`
- `/rocket:condense your last answer`
- `/rocket:condense` — the last substantial output
- `/rocket:condense --no-check <target>` — same, without the loss-check block (the check still gates delivery)

#### `/rocket:ensemble`

Session mode for thinking a problem through together, starting from an observation, a feeling, or an objective. Each round: the objective restated in substance, the developer's intuitions confirmed or **disconfirmed** against the real code with `file:line` anchors, synthetic leads (ideas, recommendations, opinions, challenges, details to absorb), then the open choice handed back. The agent never validates an orientation and modifies nothing before an explicit go — the developer arbitrates, brings the macro context, orients the architecture. One subject per round. Auto-triggers when a request reads as an intention rather than an instruction ("j'ai l'impression que", "je me demande si", "how could we") or asks to think before coding.

- `/rocket:ensemble`
- Stays active until the developer lifts it ("sors du mode ensemble", "prends la main").

#### `/rocket:myself`

The user wants to write the code themselves. The agent stops editing files and produces a precise change plan (`file:line` + short prose + why) instead.

- `/rocket:myself`

Manual-only — never auto-triggered.

#### `/rocket:no-code`

Forces a chat-only response. The agent will not create, edit, or delete any file for the rest of the turn.

- `/rocket:no-code`

Manual-only — never auto-triggered.

#### `/rocket:setup`

Initializes or refreshes the `## Project conventions` block in the current project's `CLAUDE.md`. Detects stack signals from manifests, lockfiles, CI workflows, and lint configs, composes the complete block, then asks for a single confirmation before writing. The block is delimited by `<!-- rocket:conventions:start/end -->` markers, so re-running anytime is safe: only the managed region is ever touched. Creates `CLAUDE.md` if it does not exist.

- `/rocket:setup`

Manual-only — never auto-triggered. The block it writes is consumed by `rocket:spec-maker` and `rocket:spec-writer`.

## my-hand 🖐

A personal-expression toolkit. Two independent feature sets, both **macOS-arm64 only**:

- **reMarkable page capture** — pull the current page of a reMarkable 2 notebook over USB into the model as a 1404×1872 multimodal image.
- **Voice-grounded Gmail reply drafts** — distill the user's email voice from sent Gmail, then on demand finalize a Gmail draft inside an existing thread, in that voice. Drafts are never sent.

### Slash commands

- `/my-hand:remarkable-grab [notebook-name]` — capture a notebook page (list mode if no name).
- `/my-hand:tone-profile` — distill the user's email voice into `~/.roc/my-hand/tone.md`.
- `/my-hand:inbox-reply <sender or subject keyword>` — finalize a Gmail draft inside the existing thread, asking you first for the answers the reply needs.

### Prerequisites

- **macOS-arm64.** Linux, Intel Mac, and Windows are out of scope.
- For the reMarkable feature: a **reMarkable 2** tablet (firmware 3.x+), plugged in over USB, screen unlocked, and **USB web interface** enabled (`Settings → Storage → USB web interface`). The device must answer at `http://10.11.99.1`.
- For the Gmail feature: a **Gmail MCP server** installed and bound on the host, exposing `search_threads`, `get_thread`, `create_draft`.
- **No runtime dependencies.** Ships a self-contained binary (~17 MB for the reMarkable pipeline); no Python or Homebrew needed at runtime.

See [`plugins/my-hand/README.md`](plugins/my-hand/README.md) for the rendering pipeline, troubleshooting, and what is intentionally deferred.

## Trigger language

Skill descriptions accept triggers in both English and French (`"write a commit message"` and `"redige un message de commit"` both fire `commit-writer`). Outputs are always in English, per the project quality rule.
