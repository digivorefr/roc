# Pipeline-mode defaults learned from thirty orchestrated cards

## What

An orchestrator that drives spec-writer, spec-maker and review in pipeline mode had to re-brief the same behaviours at every dispatch: a writer that invents a guard for its own rule, platform facts without a source, tests that pin nothing, a reviewer that reached the network.
After this change those behaviours are the agents' own defaults, and three brief slots carry what an orchestrator used to paste as free text: the sources of a spec's facts, the project's convention documents, the previous review round.
Cost: a phase-0 `COST` key and an `EVIDENCE` return key every orchestrator must tolerate; each new test now costs its maker one mutation run.

## Where

| Part | What changes |
|---|---|
| spec-writer | Sibling sweep after a fix design; per-event cost and loops on a hot path; sourced platform facts kept outside the spec (`EVIDENCE_PATH`); no enforcement invented for a spec's own rule; "X is logged" never a proof; product, cost and taste points returned as `Tier P:` questions in phase 1; phase 0 returns `COST`. |
| spec-maker | Convention documents beyond `CLAUDE.md` read before the first edit (`CONVENTIONS`); each new test proven by a mutation and reported in `EVIDENCE`; infrastructure files locked to what the spec states (`SCOPE_LOCK`); foreign uncommitted changes reported, never absorbed or reverted; `SUMMARY` and `DEVIATIONS` re-read in the files before returning. |
| review (pipeline contract) | Read-only stated with what is allowed (tests, mutations, a local browser); `CONVENTIONS` checked as criterion (f) with a `conventions` finding class; later rounds graded on `PRIOR_FINDINGS` and `DELTA`. |
| README and plugin manifest | Slots and keys documented; version 2.9.0. |

Unchanged: interactive mode of the three, the spec template, `/rocket:setup` and its conventions block, commit-writer, pr-writer, rebase-prs, my-hand.

## Decisions

- Behaviours confirmed on at least two orchestrated cards become agent defaults, not orchestrator brief lines; otherwise every orchestrator rediscovers them.
- Generic rules land in the shared sections (they hold in interactive mode too); only the slots and return keys are pipeline-specific.
- Sources of platform facts go to a side file named by the orchestrator, never into the spec; the spec template's "no file paths" rule stays whole.
- A new test is evidence only with the mutation that made it fail; a maker that cannot break its test deletes or rewrites it.
- Conventions are passed as documents, not restated: the agents read what the project wrote, the plugin stays stack-agnostic.
- The review may run tests, mutate and open a local browser, and may not fetch, pull, reach the network or edit: both lists are written, since "read-only" alone was read as "no tests" by some and as "any probe" by others.
- Later review rounds grade by what moved: a prior finding dismissed with a reason is not re-opened as new, an observation on untouched code is a suggestion.
- Phase 0 returns `COST` even when `none`, so the orchestrator never guesses whether the key was forgotten.
- Settled: all three slots ship together (version 2.9.0, minor), the orchestrator switches its briefs once the version is installed.

## Alternatives rejected

- Keep briefing these rules from the orchestrator — every orchestrator pays the same lessons again.
- Put the conventions themselves into the agents — breaks the stack-agnostic rule of this marketplace.
- A single `CONTEXT:` slot holding sources, conventions and prior rounds — three unrelated things one key, none of them optional on its own.

## Done means

- A spec-writer pipeline run with `EVIDENCE_PATH` leaves a sources file at that path and a spec with no path in it; without the slot, the return says `EVIDENCE: none`.
- A phase-0 return always carries a `COST` key.
- A spec-maker pipeline return lists, for every test file it added, an `EVIDENCE` bullet naming the mutation and the failing result line.
- A spec-maker given `SCOPE_LOCK` returns a `QUESTIONS` item instead of editing a compose file, lockfile, ignore file or CI workflow outside it.
- A review given `CONVENTIONS` reports every divergence as a `conventions` finding with the rule's own words, and a review given `PRIOR_FINDINGS` never raises a dismissed finding again as new.
- The README lists every slot and return key an orchestrator can send or receive.
