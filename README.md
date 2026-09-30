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
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `ARTIFACT_PATH:` — first dispatch returns `POINTS` / `DELIVERABLE`, a resume with `FRAMING: done` writes the spec to the path; questions come back as `QUESTIONS` / `BLOCKERS`, never as a live question.

#### `rocket:spec-maker`

Implements a specification, plan, or detailed instructions autonomously, then runs the project's verification commands.

- Trigger: `implement with rocket:spec-maker from specs/<file>.md`
- Pipeline (orchestrators): prompt starting with `MODE: pipeline`, optional `COVERAGE_CMD:` / `SELF_CHECK_CMD:` slots — returns `SUMMARY`, `DEVIATIONS`, `CHANGED_FILES`, `COVERAGE`, `SELF_CHECK`, `EVIDENCE`, `QUESTIONS`, `BLOCKERS`. Tests cover what the spec promises; coverage gaps are reported, not filled for their own sake.

The agent expects project-specific conventions (test command, lint rules, error-handling style) to be declared in the project's `CLAUDE.md`. Run [`/rocket:setup`](#rocketsetup) to generate that block.

#### `rocket:pr-rebaser`

Worker of [`/rocket:rebase-prs`](#rocketrebase-prs), dispatched by it only: rebases one PR in its own worktree, reconciles it with what was merged meanwhile, validates the result and returns a structured report. Never pushes.

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
- Pipeline (orchestrators): prompt starting with `MODE: pipeline` + `BASE:` follows the self-contained [`pipeline.md`](plugins/rocket/skills/review/pipeline.md) contract — fixed scope, four criteria plus caller `DEFECT_CLASSES`, every finding with severity and confidence, no interaction.

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
