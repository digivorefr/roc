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

Six workers of [`/rocket:studio`](#rocketstudio), dispatched by it only, each fed a distinct source so their blind spots do not overlap:

- `rocket:studio-lexicon` — the product's words (objects, relations, actions, events) from its domain docs, code and your words; renames flagged, never applied.
- `rocket:studio-archivist` — the language an existing product already speaks: observed intent, signature, motion, words in use, inconsistencies, design system gaps.
- `rocket:studio-intent` — one intent and its key image from one source: the subject's world, your references, or a deliberate counterpoint. Three instances run in parallel.
- `rocket:studio-prototyper` — a throwaway prototype of one screen or flow, every state and transition, three ways considered before one is kept; corrects once, adds variant switches.
- `rocket:studio-critic` — operates the screen and critiques it against the frame, the catalog, the language, your taste rules and your past remarks on the same screen type; every finding names its rule or reads `opinion`. Also compares a built screen with its prototype.
- `rocket:studio-end-user` — the end-user agent: sees only the prototype and the tasks, reports where it hesitated, got stuck or was misled by a word, across variants.

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

Designs web interfaces with a frame of interface craft (`references/frame.md`), a catalog of ways to solve interface problems (`references/catalog.md`), distinct sources of inspiration, and your eye at three or four checkpoints. Five entries, picked from what it finds and stated in one line you can refuse: found a product's language from scratch, found it from the existing product, decline one new screen or flow within the language, critique a screen, compare a built screen with its proposal. Every decision you give in free text comes back as one refusable line, and nothing runs before your go. Your checkpoint remarks build a critique corpus that later critiques cite. A decline ends with a proposal for `rocket:spec-writer`; prototype code never ships.

- `/rocket:studio`, "design the settings screen", "critique this screen", "conçois l'écran …"
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `CHECK: critique | fidelity` + `SCREEN:` (plus `PROPOSAL:` for fidelity, optional `SCREEN_TYPE:` and `TASKS:`) follows the self-contained [`pipeline.md`](plugins/rocket/skills/studio/references/pipeline.md) contract — returns `FINDINGS`, `GAPS`, `NOT_COMPARED`, `WALK`, `CONFIDENCE`, `QUESTIONS`, `BLOCKERS`, asks nothing, writes nothing; a creative entry returns a blocker.

Files:

- `design/` at the repository root — the product language and the proposals with their captures; committed.
- `~/.roc/rocket/studio/` — your critique corpus, taste rules and the closed list of screen types and aspects, shared across projects.
- `<project>/.roc/rocket/studio/` — run state, self-contained prototypes and unchosen key images; the main checkout's copy also holds the preview recipe, which worktrees replay. Keep `.roc/` gitignored.

Notes:

- No setup step: on first contact studio discovers how to show a screen or a story from the project itself, states it in one line, and records it on your go. It starts a story or dev server on its own; an environment the project's scripts bring up is yours to start.
- Browser tooling in the session is optional: without it, you open prototypes and key images from the paths given, captures are missing, and critiques state reduced confidence.
- Writes happen after your go, in a later turn, so each one prompts unless your permission rules allow it: add `Edit(design/**)`, `Edit(.roc/rocket/studio/**)` and `Edit(~/.roc/rocket/studio/**)` to your allow rules. From a worktree, the preview recipe is written to the main checkout's `.roc/`, outside these patterns.
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
