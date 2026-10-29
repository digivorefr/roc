# Studio: interface design with a frame, distinct sources and the operator's eye

## What

When Claude designs a web interface, the result looks like a generic SaaS kit: no guiding intent, no consistency across screens or sessions, and weak judgment of its own renders.
`/rocket:studio` gives Claude a frame of interface craft, distinct sources of inspiration, agents that confront each other once, and the operator's eye at the moments where it is cheap to change course.
It founds a product's language, declines new screens within it, critiques screens, and compares a built screen with the proposal it came from.
Each declined screen ends as a proposal the operator validates; rocket:spec-writer turns it into a spec, and prototype code never ships.
Cost: six new agents and several rounds of agents per run, three or four checkpoints of the operator's time, a preview recipe discovered once per project, and a second exception to the repo's English rule.

## Where

| Part | What changes |
|---|---|
| `/rocket:studio` skill (new) | Picks the entry, talks to the operator, restates decisions, dispatches the agents, writes what the operator validates, manages the preview tooling. Pipeline mode for critique and fidelity. Ships the frame and the catalog as reference files. |
| Six `studio-` agents (new) | Lexicon, archivist, intent, prototyper, critic, end-user agent. Dispatched by studio only. |
| Product language and proposals (new, per project) | Committable documents in a `design/` folder at the repository root. |
| Critique corpus and taste rules (new, per operator) | Kept in the operator's home folder, shared across projects. |
| Disposable work (new, per project) | Prototypes and unchosen key images, kept out of the repository's history. |
| Preview recipe (new, per project) | How to show a screen or a story, discovered by studio on first contact and replayed afterwards; kept out of the repository's history. |
| Repo CLAUDE.md | The English rule names studio's prototype copy next to condense. |
| Rocket README and plugin manifest | Document the skill, its agents and its pipeline slots; minor version bump. |

Unchanged: spec-writer, spec-maker, review and its pipeline contract, rebase-prs, my-hand, the project's design system (studio never edits it), `/rocket:setup` and every conventions block (studio neither needs nor writes them).

## Decisions

- `/rocket:studio` is a new rocket skill with six worker agents prefixed `studio-`, dispatched by it only, as rebase-prs does with its worker. It runs in the main conversation and is the only part that talks to the operator, because agents cannot ask questions. The name avoids a clash with Anthropic's `design` skills.
- The frame (universal rules of interface craft) and the catalog (ways to solve interface problems) ship as reference files of the skill, the same for every project. What is specific to a project goes in its language; what is specific to the operator goes in the taste rules.
- Three creative entries: found a product's language from scratch, found it from an existing product, decline a new screen within an existing language.
- Two check entries sit beside them: critique a screen, and compare a built screen with its proposal. Both run interactively or in pipeline mode.
- Studio picks the entry from what it finds (a language, interface code without a language, or neither) and states it in one line the operator can refuse. The operator never has to name the entry.
- A decline run covers one screen or one flow; two screens are two runs. Model critique catches layout problems but misses the ones that span screens.
- Founding produces one artifact, the product's language: lexicon (objects, relations, actions, events in plain words), the intent in one sentence, visual signature (stroke, spacing rhythm, typography, color roles), motion language (what moves, how, duration, easing, when nothing moves), references, do/avoid.
- Founding prototypes one representative screen the operator names, to judge the language in use. The language's signature and motion take the values that validated prototype actually uses, not the intent note's, so the language describes what the operator saw. Developing that screen is a later decline run.
- Declining reads the language and never contradicts it. Without a language it stops before any agent runs and proposes founding from the existing product.
- Each role is fed a distinct source, because agents on the same model share blind spots and personas do not fix that: lexicon (domain docs, code, the operator's words; every creative entry), archivist (design system, existing screens, vocabulary; found-from-existing only), three intent instances, prototyper, critic, and the end-user agent (walks the tasks, gives one comparative report across variants).
- The three intent instances each see one source only: the subject's world or a metaphor from it, the operator's references, or a deliberate counterpoint. On top of it, each sees the brief, the validated words and the frame, plus the language when declining. In founding they address the whole product; in declining, the screen's composition.
- One `studio-intent` agent is dispatched three times in parallel, and each instance renders its own key image. Diversity survives up to the image, at the cost of three throwaway builds.
- When the operator gives no references, the references instance works from the operator's taste rules and the language's references. When neither exists, studio runs two intents and says so.
- The prototyper receives the chosen intent, the validated words, the language, the frame, the catalog and the taste rules. Before fixing a solution, it names three different ways to carry the intent's interactions; the ways not taken become candidate variants.
- The critic receives the frame, the catalog, the language, the taste rules, the intent note, and only the past remarks made on screens of the same type.
- The critic operates the rendered prototype itself (tabs through it, triggers actions, turns on reduced motion) and watches it move. Some breaches of the frame show only in use, never on a still capture.
- Every critic finding names the rule it rests on: a frame rule by its title, a language entry, a taste rule or a past remark. A finding without one is labelled "opinion", so the operator and an orchestrator can weigh it.
- The end-user agent receives only the prototype and the tasks in plain words; it never sees the language, the intent or the critic's report. Otherwise it would judge the intent instead of the use.
- One confrontation round: the critic and the end-user agent report, the prototyper corrects once, and the result goes to the operator. No debate between agents. Studio never designs: it talks to the operator, carries validations, dispatches and synthesizes.
- Words checkpoint: a table of each word, what it designates in plain words, its actions and its events. In declining it shows only what the screen adds and is skipped when the screen adds nothing. In found-from-existing it is shown together with the deduced language, as one checkpoint.
- A lexicon word that differs from the word the product already uses is shown as a rename at the words checkpoint, never applied silently. A rename reaches beyond the screen.
- Intents checkpoint: three key images, each with its intent note. The operator picks one, mixes them, or rejects all and adds input for a new round. Found-from-existing runs intents only when the operator wants to evolve the language; just writing it down costs two agents and one checkpoint.
- Prototype checkpoint: the prototype after the confrontation round, with what was raised, what was fixed, and what is left to the operator's eye.
- The operator answers freely. Studio restates each decision as one refusable line and continues only on the operator's go, because a misread decision costs a full round of agents.
- Every validated line is written where it belongs (the language, the proposal, the corpus) as soon as it is validated. A run interrupted after a checkpoint resumes from that checkpoint at the next invocation.
- Hypothesis variants: one hypothesis per variant, stated plainly, everything else shared, compared in one prototype with a switch. Separate prototypes only when the hypothesis changes the whole structure.
- Studio proposes a variant at the prototype checkpoint when it sees a serious alternative. The operator can ask for one at any time ("test X against Y").
- A validated hypothesis amends the language (one refusable line). A refuted one is recorded under avoid and never proposed again. Screens built earlier are not revisited.
- At each checkpoint, a remark is captured as: the capture, the targeted zone, the verbatim remark, and the rule it reveals in one line. Studio deduces the level (this product goes to the language's do/avoid; everywhere goes to the operator's taste) and shows it in the restatement for correction.
- Taste is dated: a remark that contradicts an older one supersedes it, restated as "replaces: …". The corpus lives in the operator's home folder, shared across projects, classified by screen type and aspect. A remark that recurs across projects is promoted to a taste rule, shown in the restatement and refusable.
- Screen types and aspects form a closed list kept with the corpus, extended only when the operator confirms a new one. A free list drifts ("list" vs "table"), and matching then fails without anyone noticing.
- Pipeline mode reads the corpus and never writes to it or to the language. Only the operator's own remarks teach studio.
- Precedence: a firm frame rule beats everything; on the tokens and components it carries, the design system beats the language, and a firm rule it breaks is listed as a gap for the designer; the language beats the taste rules; a default frame rule yields only to a reason stated in the language or in a taste rule.
- A remark that contradicts a firm frame rule is restated with that rule's title and not recorded; only a version the rule allows, restated by the operator, is.
- With a design system, the language never redefines its tokens or components; it adds intent, motion, lexicon and composition. Each conflict is listed as a gap for the designer, in the proposal or, when founding, in the language.
- Prototype material: self-contained HTML, CSS and JavaScript when founding from scratch; for found-from-existing and declining, the project's real design-system components shown through its own preview tooling, falling back to self-contained HTML with the gap stated. Key images follow the same rule. Prototype code never ships.
- Studio depends on no setup step, because none is ever run. On first contact it discovers the preview recipe from the project itself (its dependencies, its preview tooling configuration, its scripts): where the design system lives, how to show a screen or a story, how to check the preview is up. It states the recipe in one refusable line before the first dispatch and records it on the operator's go. Later runs replay it without asking and rediscover only when the replay fails.
- A project with no design system and no preview tool gets a recipe that reads "self-contained", recorded the same way, so the question is never asked twice.
- The recipe lives in the main checkout's `.roc/rocket/studio/`, never committed. From a worktree, studio reaches the main checkout through git's list of worktrees, so a worktree replays the recipe instead of rediscovering it.
- Studio checks the preview once per run, before any dispatch, and agents never start it, because parallel agents would collide on ports. Studio starts a preview tool the project runs on its own (a story server, a dev server). When the preview needs a whole environment that the project's own scripts bring up, studio asks the operator to start it and never starts it itself.
- The language and the proposals, with their captures, are product documents in a visible `design/` folder at the repository root, one language per repository. A project that ignores `.roc/` could not commit them there.
- Disposable work (self-contained prototypes, unchosen key images) lives in the project's `.roc/rocket/studio/`. Design-system prototypes live where the preview tooling needs them. They are listed in the proposal and removed after the fidelity comparison, and any leftover is listed at the next start. Risk: one gets committed by mistake on the working branch in the meantime.
- A decline ends with a proposal: decisions one line each, lexicon additions, states (empty, loading, error, success), transitions (trigger, what moves, duration, easing), accessibility points, hypotheses validated or refuted, one capture per key state, and where the prototype is.
- The proposal separates settled decisions from measurable outcomes: a state exists, an action triggers a transition, a keyboard path, AA contrast. spec-writer, given the proposal as settled decisions, takes its `Done means` from the measurable part and stays unchanged; its polish pass already cuts bullets that are not pass/fail.
- The fidelity comparison is studio's last step: built screen against prototype, state by state, side by side. The critic lists the gaps and the operator judges. Motion is compared by its declared values on both sides, plus a recording only when the browser tooling can make one.
- In the fidelity comparison, a state the session cannot reach is listed as not compared, never assumed equal. When the prototype is gone, the proposal's captures and transitions are the reference.
- Studio is model-invocable. Turning that off would also stop Claude from starting it on its own and from preloading it into agents.
- Its description triggers on explicit requests to design, found, decline or critique an interface, and on orchestrator briefs. It excludes CSS and component bug fixes, and sets studio apart from Anthropic's `design` skills and `frontend-design`. Risk: on a vague request, Claude picks one in place of the other.
- Pipeline mode (first line `MODE: pipeline`, flat `KEY: value` brief, structured return, as in spec-writer and review) exposes critique of a screen and the fidelity comparison to orchestrators such as the-dude. An orchestrator's worker can run studio and its agents, since agents may nest three layers deep by default.
- A pipeline brief that asks for a creative entry gets back a blocker naming the interactive command. Creative entries need the operator at every checkpoint.
- A pipeline run shows the screen through the brief's `SCREEN`, since the orchestrator brings up its own environment. It never discovers or records a preview recipe, which needs the operator's go. When `SCREEN` is unreachable, the critic works from code and `CONFIDENCE` reads reduced.
- Browser access is not guaranteed, so agents use whatever browser tooling the session has. Without one, studio says so at the start, the operator opens prototypes and key images from the paths given, captures are missing from the proposal and the corpus, and the critic works from code and states its reduced confidence.
- Interface copy in prototypes is in the product's language; studio's own prose is in English. The repo's English rule names studio next to condense.
- The human is called "the operator" and the agent that walks the tasks "the end-user agent", so "user" never means two things.
- Settled: cost and model per agent, the-dude's side of the integration, and seeding the corpus with past corrections are out of this spec.

## Alternatives rejected

- Keep using `frontend-design` and `design:design-critique` as today — one pass by one hand, nothing kept between sessions.
- One agent playing every role in turn — it sees every source, so the three intents converge.
- Personas instead of distinct sources — same model, same blind spots.
- A debate loop until the agents agree — agents on the same model conform, and debate can end worse than one agent alone.
- Critique against the frame alone, with no past remarks — without comparable examples, model critique stays far below a designer's.
- Similarity search over the corpus — the plugin would have to ship an index, and the screen type is enough to pick comparable remarks.
- One corpus per project — the taste belongs to the operator and follows them across projects.
- The language inside CLAUDE.md — it would load into every session, mixed with stack rules.
- The language under `.roc/` — a project that ignores `.roc/` cannot commit it.
- Prototypes in Figma through its connector — needs a per-user connector, and development reads code, not frames.
- A preview section in the conventions block, written by `/rocket:setup` — setup is never run, so studio would ask at every run.
- The preview recipe committed in `design/` — it would travel with branches, but puts a technical recipe among product documents.
- Rediscovering the preview at every run — slower, and the result can differ from one run to the next.
- A protocol for orchestrators to drive the creative entries now — the-dude's side of the integration is parked.
- Studio building the screen itself — prototype code is throwaway; development restarts from the proposal through spec-writer.

## Done means

- Studio states the entry in one line before anything runs: a new screen in a project with a language starts a decline, interface code without a language gets an offer to found from the existing product, an empty project starts a founding from scratch.
- A decline request in a project without a language stops before any agent runs and offers founding from the existing product.
- A request to fix a button's alignment or a CSS bug does not start studio.
- A founding from scratch ends with a language holding the lexicon, the intent sentence, the signature, the motion, the references and the do/avoid. A found-from-existing run that does not evolve the language ends after its first checkpoint, with the language written.
- The words checkpoint shows each word, what it designates, its actions and its events. A word that differs from the one the product uses appears as a rename. A decline whose screen adds no word goes straight to intents.
- The intents checkpoint shows three key images, each with a one-sentence note. Rejecting all of them with a remark produces three new ones.
- The prototype checkpoint shows the corrected prototype with three lists: raised, fixed, left to the operator's eye.
- After each free-text answer, every decision appears as one line, and nothing is dispatched before the operator's go.
- The first run in a project states the discovered preview recipe in one line before any dispatch; the next run replays it without asking. A run from a worktree replays the recipe recorded in the main checkout.
- In a project with a design system, the prototype opens in the project's own preview tooling and uses its components. When that fails, a self-contained prototype opens, with the gap stated.
- When the preview needs an environment the project's scripts bring up and it is down, studio asks the operator to start it and starts nothing.
- The language holds no color, spacing value or component that the design system defines. Each conflict appears as a gap for the designer.
- A checkpoint remark appears in the corpus with its capture, zone, verbatim words and rule, unless it contradicts a firm frame rule. A product-level remark also appears in the language's do/avoid.
- A remark that contradicts an older one is restated with "replaces: <older rule>", and later critiques never cite the older one.
- A remark that contradicts a firm frame rule is restated with that rule's title, and later critiques still apply the firm rule.
- A critique of a table cites only past remarks made on tables. Every finding names its rule (frame rules by their title) or reads "opinion".
- A remark matching one from another project is offered as a taste rule in the restatement.
- "Test X against Y" gives one prototype with a switch and one comparative report from the end-user agent. The validated variant appears in the language and the refuted one under avoid, and the refuted one is not proposed again in a later run.
- A validated decline leaves a proposal with one-line decisions, lexicon additions, the four states, the transitions (trigger, what moves, duration, easing), accessibility points, hypotheses, one capture per key state, and where the prototype is.
- A spec written by spec-writer from a proposal has no `Done means` bullet that judges aesthetics.
- The fidelity comparison shows built and prototype side by side for each state, with the critic's gaps. A state the session cannot reach is listed as not compared.
- Without browser tooling, studio says so at the start, gives the paths to open, and every critique states reduced confidence.
- After quitting following a validated checkpoint, the next invocation offers to resume from that checkpoint.
- A pipeline critique returns a structured report without asking anything, and leaves the corpus, the language and the preview recipe unchanged. A pipeline brief for a creative entry returns a blocker.
- Prototype copy is in the product's language; studio's own messages are in English.
- Every entry runs in a project where `/rocket:setup` never ran, and no run writes to a conventions block.
- After the fidelity comparison, no studio prototype file remains in the project's source tree.

## Reference

### Agents

| Agent | Receives | Never receives | Returns |
|---|---|---|---|
| Lexicon | The brief, domain docs, code, the operator's words; the language when declining | The taste rules | Words with what each designates, relations, actions, events; renames against the product's current words |
| Archivist | The design system, existing screens, the interface's current vocabulary | The taste rules | The deduced language: intent observed, signature, motion observed, words in use, inconsistencies, design system gaps |
| Intent (three instances) | The brief, the validated words, the frame, its one source; the language when declining | The other two sources, the catalog, the taste rules | An intent note in one sentence, with what it implies for signature, motion and composition; one key image |
| Prototyper | The chosen intent, the validated words, the language, the frame, the catalog, the taste rules, the preview recipe; for its one correction, the critic's and end-user agent's reports | — | The prototype and where it is; one capture per state; the three ways considered and the one kept; transitions as built; the signature and motion values used; design system gaps |
| Critic | The frame, the catalog, the language, the taste rules, past remarks on the same screen type, the intent note, the running prototype | Past remarks on other screen types | Findings, each citing its rule or marked opinion; accessibility points; confidence |
| End-user agent | The running prototype, the tasks in plain words | The language, the intent, the critic's report | Per task: done, hesitated or stuck, where, and which word misled; one comparative report across variants |

### Checkpoints by entry

| Entry | Checkpoints, in order |
|---|---|
| Found from scratch | Words; intents; prototype of the representative screen |
| Found from existing | Deduced language with the words; then, only to evolve the language, intents and prototype |
| Decline | Words (skipped when the screen adds none); intents; prototype, with variants when proposed or asked |
| Critique | The critic's findings; the operator's remarks |
| Fidelity | Built and prototype side by side per state, with the critic's gaps; the operator's judgment |

### Product language

| Section | Content |
|---|---|
| Intent | One sentence |
| Lexicon | Word (in the product's language), what it designates, relations, actions, events |
| Visual signature | Stroke, spacing rhythm, typography, color roles; never a value the design system defines |
| Motion | What moves, how, duration, easing, when nothing moves |
| References | What the operator gave or validated |
| Do / avoid | Product-level rules from remarks, validated hypotheses, refuted hypotheses under avoid; each dated |
| Departures from default frame rules | The rule's title and the stated reason |
| Design system gaps | Each conflict, for the designer |

### Proposal

| Part | Content |
|---|---|
| Settled decisions | Decisions one line each, lexicon additions, hypotheses validated or refuted, accessibility points, design system gaps |
| Measurable outcomes | States (empty, loading, error, success) and what each shows; transitions (trigger, what moves, duration, easing); keyboard path; AA contrast |
| Evidence | One capture per key state; where the prototype is |

### Critique corpus

| Item | Fields |
|---|---|
| Remark | Date, project, screen type, aspect, capture (or "missing"), zone, verbatim remark in the operator's words, rule in one English line, level (this product or everywhere), what it replaces, status (active, superseded, promoted) |
| Taste rule | Rule, date, the remarks it came from and their projects, what it replaces |
| Screen types and aspects | The closed list; extended only on the operator's confirmation |

### Storage

| What | Where | Committed |
|---|---|---|
| Product language, proposals and their captures | `design/` at the repository root | Yes |
| Critique corpus and taste rules | `~/.roc/rocket/studio/` | Outside every repository |
| Self-contained prototypes, unchosen key images, run state | The project's `.roc/rocket/studio/` | No |
| Preview recipe | The main checkout's `.roc/rocket/studio/` | No |
| Design-system prototypes | Where the preview tooling needs them, as the preview recipe states | No; removed after the fidelity comparison |

### Preview recipe

| Field | Content |
|---|---|
| Design system | Where it lives, or `none` |
| Screen | How to show a screen: an address or a command |
| Story | How to show one component in isolation, or `none` |
| Kind | `tool` (studio may start it), `environment` (the operator starts it), or `self-contained` |
| Check | How to tell the preview is up |
| Discovered | Date, and the files it was deduced from |

### Pipeline brief and return

| Slot or key | Definition |
|---|---|
| `CHECK` | `critique` or `fidelity`; mandatory. Anything else, a creative entry included, gets back `BLOCKERS` only |
| `SCREEN` | How to show the screen: an address, a story, or a file; mandatory |
| `PROPOSAL` | The proposal to compare against; mandatory for `fidelity` |
| `SCREEN_TYPE` | Optional; otherwise deduced from the closed list |
| `TASKS` | Optional; tasks in plain words for the end-user agent; absent means no walk |
| `FINDINGS` | `<zone> · <rule: frame firm "<title>" \| frame default "<title>" \| language \| taste \| past remark \| opinion> · <what> · fix: <intent>` |
| `GAPS` | Fidelity only: `<state> · <what differs> · seen by: capture \| operation \| recording \| code` |
| `NOT_COMPARED` | Fidelity only: states the session could not reach, or `none` |
| `CONFIDENCE` | `full`, or `reduced · <why>` |
| `QUESTIONS`, `BLOCKERS` | Bullets, or `none` |

## Risks and rollback

- Claude Code documents that agents inherit the session's tools, but not whether a plugin's agents get the session's browser tools. If they do not, the critic and the end-user agent work from code, and every report says its confidence is reduced.
- A nesting limit lowered in the operator's settings stops an orchestrator's worker from dispatching studio's agents. The pipeline run then returns a blocker instead of a critique.
- Model critique stays below a designer's even with past remarks as examples. The operator's eye at each checkpoint remains the guard.
- In a repository with several preview tools, discovery can pick the wrong one. The refusable line before the first dispatch is the guard.
- Captures of real screens may show real data. The corpus keeps them in the operator's home folder, outside every repository.
- Rollback: reverting the rocket version removes the skill and its agents. The language, proposals, corpus and preview recipes stay as plain files that nothing else reads.
