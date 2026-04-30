---
name: context-update
disable-model-invocation: false
context: fork
agent: general-purpose
description: Update the project's semantic lexicon at .claude/lexicon.md from the current conversation. Use this skill whenever the user invokes "/rocket:context-update", asks to "update context", "refresh lexicon", "update the lexicon", "rebuild project vocabulary", "mets a jour le contexte", "mets a jour le lexique", "rafraichis le lexique", or any similar request. Auto-invoke when a major semantic shift just happened in the conversation (new domain concept, new architectural decision, redefinition of an existing term) and the lexicon should capture it before the next turn.
---

# Project lexicon updater

Maintain the project's semantic lexicon at `.claude/lexicon.md`: a compact, structured catalog of project-specific concepts, vocabulary, recurring patterns, roles, and decisions. The lexicon is read by `rocket:spec-writer`, `rocket:spec-maker`, and other agents to align their vocabulary with the user's. This skill is the only writer.

The skill runs in two modes:

- **Hook mode** — invoked by the `Stop` hook through the wrapper script `plugins/rocket/hooks/update-context.sh`. The transcript is provided on stdin. The summary is logged but not surfaced to the user.
- **Manual mode** — invoked by the user via `/rocket:context-update` or auto-invoked by Claude on a semantic shift. The forked context provides the conversation; the summary is surfaced to the user.

## Output contract

- Write `.claude/lexicon.md` (and only that file) atomically via `.claude/lexicon.md.tmp` + `mv`, protected by `flock` on `.claude/lexicon.md.lock`.
- The file conforms to the [Lexicon format](#lexicon-format) below. No deviation.
- Final output to the caller is a single short paragraph: counts of added / merged / flagged entries, names of flagged entries. No prose elaboration. No emojis.
- If the lexicon is unchanged after analysis, output "No update needed." and do not rewrite the file.

## Lexicon format

```markdown
<!-- Auto-maintained by rocket:context-update. Edits are preserved when consistent. -->

## <Area name>

### <Concept>
- **Definition**: <one-line definition>
- **Aliases**: <comma-separated synonyms, or "none">
- **Relations**: <comma-separated concept names, or "none">
- **Source**: <free-form citation>

### <Concept>
[...]

## <Other area>
[...]
```

Rules enforced on every write:

- Header comment is always the first line.
- Each entry has exactly the four bullet keys above, in that order. No additional bullets, no surrounding prose.
- Areas are sorted alphabetically. Concepts within each area are sorted alphabetically.
- No two entries share a concept name within the same area.
- No two areas share a name.
- Every value listed in `Relations` resolves to an existing concept name in the file.
- Total size cap: **300 lines OR 12 KB, whichever smaller**. If exceeded after merge, prune per Step 5.

Areas are project-defined groupings (e.g. `Domain`, `Architecture`, `Roles`, `Conventions`, `Decisions`). Create them on first need; merge them when their meaning overlaps.

## Workflow

### Step 1 — Load context

1. Read `.claude/lexicon.md`. If absent, treat the existing lexicon as empty.
2. Read the conversation transcript:
   - **Hook mode**: read from stdin (the wrapper pipes the transcript JSONL).
   - **Manual mode**: use the conversation context inherited by the fork.
3. Read the project's `CLAUDE.md` (root only) for tone and language conventions to match.

### Step 2 — Extract candidates

Identify nouns and noun phrases that name:

- Domain concepts specific to the project (not generic technical vocabulary).
- Architectural elements (services, modules, boundaries, named patterns).
- Recurring patterns the user has named or described.
- Roles (human or system) the project distinguishes.
- Decisions the user has stated explicitly ("we decided to...", "the rule is...").

Discard generic technical vocabulary (HTTP, SQL, REST, "webhook" in the abstract). Keep them only when the project gives them a specific local meaning.

### Step 3 — Deduplicate

For each candidate, compare against existing entries by **semantic match**, not string match:

- Existing entry covers the same concept and the candidate adds new information → merge into the existing entry, keep the existing concept name as the canonical label.
- Existing entry covers the same concept and the candidate restates the same info → skip.
- Existing entry covers the same concept under a different label → add the candidate's label to `Aliases`.
- No matching entry → new entry. Place it in the most appropriate existing area, or create a new area if none fits.

### Step 4 — Reconcile contradictions

If a candidate contradicts an existing definition (different meaning under the same concept name, or incompatible relations):

- Append `<!-- TODO: contradiction with <description> -->` to the affected entry's `Definition` line.
- Do NOT silently overwrite.
- Surface the flag in the Step 7 summary.

### Step 5 — Prune

After merging, render the lexicon and measure its size.

If the rendered file exceeds **300 lines OR 12 KB** (whichever smaller):

1. Sort entries by `Source` recency (oldest first; "inferred" counts as oldest).
2. Drop entries that are not referenced by any other entry's `Relations`.
3. Never drop an entry marked with a `<!-- TODO: contradiction ... -->` comment.
4. Stop pruning as soon as the rendered file fits the budget.

If the budget cannot be met without dropping flagged entries, stop pruning and emit a warning in the summary.

### Step 6 — Render and write

1. Compose the file with the header comment first, areas sorted alphabetically, concepts sorted alphabetically within each area, four bullets per entry in the order `Definition` / `Aliases` / `Relations` / `Source`.
2. Resolve the project root (use `$CLAUDE_PROJECT_DIR` if set, otherwise the cwd).
3. Acquire an exclusive `flock` on `.claude/lexicon.md.lock` for the duration of write.
4. Write the rendered content to `.claude/lexicon.md.tmp`.
5. `mv .claude/lexicon.md.tmp .claude/lexicon.md` (atomic on POSIX filesystems).
6. Release the lock.

If the rendered content equals the previous content byte-for-byte, skip the write (idempotent no-op).

### Step 7 — Summary

Emit a single short paragraph:

```
Lexicon updated: <N> added, <M> merged, <K> flagged. Flagged: <comma-separated names or "none">.
```

If nothing changed: `No update needed.`

In hook mode, the wrapper captures this summary via stderr; do not add formatting that would garble the log.
In manual mode, surface the summary directly to the user.

## Idempotency rules

- A second invocation on the same conversation must produce a byte-identical lexicon file.
- Sorting, normalization (whitespace, comma spacing, trailing newlines), and merge order must therefore be deterministic.
- Do not include timestamps or run counters in the file.

## Concurrency rules

- The `flock` on `.claude/lexicon.md.lock` is mandatory. Two simultaneous fires must serialize.
- The second invocation reads the freshly-updated lexicon (Step 1 re-runs after acquiring the lock) and only contributes incremental information.

## Edge cases

- **Lexicon does not exist**: Step 1 treats it as empty. Step 6 creates it.
- **Lexicon edited manually by the user**: respect the edits unless they violate invariants (duplicates, dangling relations, missing keys). On invariant violation, mark the offending entry with a `<!-- TODO: invariant ... -->` comment instead of rewriting it.
- **Transcript empty or trivial**: emit "No update needed." and skip the write.
- **`.claude/` directory missing**: create it before writing.

## What NOT to do

- Do NOT modify any file other than `.claude/lexicon.md` and the temp/lock siblings.
- Do NOT run shell commands beyond what is needed to acquire the lock and perform the atomic write.
- Do NOT include prose, examples, or commentary inside the lexicon file. Entries are definition + relationships only.
- Do NOT rename existing concept names unless merging duplicates. Stable names matter.
- Do NOT add entries for generic technical vocabulary that has no project-specific meaning.
- Do NOT surface the summary to the user when in hook mode (the wrapper handles logging).

## Good summary examples

```
Lexicon updated: 2 added, 1 merged, 0 flagged. Flagged: none.
```

```
Lexicon updated: 0 added, 3 merged, 1 flagged. Flagged: Outbound webhook.
```

```
No update needed.
```

## Bad summary examples

```
Hi! I added two new entries to the lexicon. The first one is about webhooks...
```

(Too verbose, friendly tone, restates content already in the file.)
