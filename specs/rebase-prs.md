# Rebase open PRs after a merge

## What

When a PR is merged on GitHub, the other open PRs fall behind their base, and rebasing each by hand risks losing either what the PR brings or what was just merged.
`/rocket:rebase-prs` lets the operator pick the PRs to rebase; a worker agent rebases each one in its own worktree, reconciles it with everything merged since it branched, checks that both sides still hold, and asks the operator whenever it cannot be sure.
Nothing is pushed without the operator's yes, PR by PR.
Cost: one dependency install and at least one verification run per PR, PRs handled one at a time, unsigned rebased commits, and a GitHub dependency in a plugin that had none.

## Where

| Part | What changes |
|---|---|
| `/rocket:rebase-prs` skill (new) | Manual-only. Lists the PRs, finds their specs, asks every question, confirms and performs each push, retargets stacked PRs, cleans up. |
| `rocket:pr-rebaser` agent (new) | Rebases one PR in its own worktree, classifies and resolves overlaps, validates the result, returns a structured report. Never pushes. |
| PR branches on GitHub | Force-pushed after the operator's yes; a stacked PR that GitHub did not retarget gets its base changed. |
| Run state (new) | One state file per run and one journal per PR, removed at the end of the run. |
| Rocket README and marketplace listing | Document the skill, the agent and the GitHub prerequisite. |
| Repo CLAUDE.md | One line naming this skill as rocket's first GitHub-dependent skill under Hard rule 4. |

Unchanged: `/rocket:review` and its pipeline contract (read, not modified), spec-writer, spec-maker, `/rocket:setup` and its conventions template, the my-hand plugin, the operator's checkout and the project's `.gitignore`.

## Decisions

- `/rocket:rebase-prs` is a manual-only skill that runs in the main conversation and handles every exchange with the operator: the PR list, the questions, the push confirmations; agents cannot ask the operator anything, so none of this can live in the worker.
- Each selected PR goes to a worker agent, `rocket:pr-rebaser`, shipped by rocket, which runs in its own temporary worktree created by Claude Code and returns a structured result; its description says only this skill dispatches it, since an agent cannot be made manual-only.
- Only the skill pushes, after the operator's yes; the worker never pushes. Risk: this rests on the worker's instructions, since an agent's tool list cannot drop `git push` without dropping its whole shell.
- Workers start from each PR's head on GitHub and never touch the operator's checkout; commits that exist only in the operator's local branch are left out, so the PR list flags those PRs, and the final report names the local branches to reset after the push.
- The worker replays commits with commit signing turned off, so a signing passphrase prompt can never block a rebase. Consequence: the rebased commits are unsigned; a repository that requires signed commits refuses the push or blocks the PR's merge, and the operator re-signs by hand or declines that PR. When the PR's commits were signed, its push confirmation says the rebased ones are not.
- Each GitHub operation goes through the GitHub connector when it exposes the needed tool — listing PRs (`list_pull_requests`), identifying the operator (`get_me`), changing a PR's base (`update_pull_request`) — and otherwise through `gh`; a connector missing a tool is not an error while `gh` covers it. The skill stops with a one-line prerequisite message only when an operation has neither, so it works with the official hosted GitHub server alone, with `gh` alone, or with both.
- The connector serves those three tools only; the rebase and the push are plain local git, and the connector's branch update is never used, since it merges instead of rebasing.
- The repo's CLAUDE.md gains one line naming this skill as rocket's first GitHub-dependent skill under Hard rule 4, and the README states the GitHub prerequisite; the rule is written for whole plugins, so rocket would otherwise break it.
- The PR list is numbered and answered by typing numbers, as review's commit picker does, since the question tool offers at most four choices.
- Selectable: open PRs whose base has moved, including PRs stacked on a merged PR. Shown but not selectable, with the reason: up-to-date PRs and PRs from forks. Flagged: PRs authored by someone other than the operator.
- The PR's spec, first match wins: a spec file in the PR's own changes (under `specs/` or the project's existing spec directory), a spec path or Notion link in the PR description, the same in its commit messages, then review's topic scan of the spec directory, leaving out the specs the merged side added or changed, which are the merged side's own. Several candidates: the operator picks. PR comments are not read.
- The skill, not the worker, fetches a Notion spec once through the Notion connector and saves it as a file the worker reads; without the connector, the operator pastes the spec or continues without one, never silently.
- The merged side's spec is looked up only in the spec directory of the new base, and only for the parts that overlap the PR; a merged PR whose spec lives elsewhere counts as having none, and its tests still guard it through the verification command.
- Without a spec, the reference is the PR description, the before/after comparison of the PR's changes and the verification command; the report calls this reference weaker.
- Two intents are reconciled: the PR's, and the merged side's, meaning everything that landed on the base since the PR branched off, possibly several PRs. Where both change the same behavior the merged side wins by default; the aim is the benefit of both, not a winner.
- Overlaps are found by contract, not by file: what the merged side changed (signatures, data shapes, rules, tests) and where the PR relies on it, even in files the merged side did not touch; a rebase without a textual conflict can still break.
- Each overlap gets one class, defined in Reference, which fixes its resolution: orthogonal, keep both; mechanical, adapt the PR to the new contract; redundant, keep the merged version plus only what the PR adds; composable, apply the PR's behavior on top of the merged one, asking the operator only when the validation fails; contradictory, always ask the operator, with the merged version proposed.
- Merge commits that brought the base into the PR are dropped, their content being on the new base already; the conflicts they had resolved are resolved again, and the PR's history becomes linear.
- A stacked PR replays only its own commits, not its parent's, whatever strategy merged the parent (squash, rebase or merge commit).
- Guard: after resolution, the before/after comparison of the PR's changes must show every part of the PR present, adapted with a reason, or dropped as redundant with a reason. An unexplained drop blocks the push; it is the only hard block.
- The benefit of both holds when the verification command passes (it includes the merged side's tests), the tests the PR added are still there, and each `Done means` bullet of the PR's spec is met or marked not assessable. For the merged side's spec, only that its bullets still hold is checked. "Not assessable" never counts as met and is listed in the report.
- The worker grades each `Done means` bullet itself with review's three verdicts (met, not met, not assessable) and runs no full review; the report stays about the rebase, with no extra pass per PR.
- The skill finds the verification command once, the way spec-maker does, and passes it to every worker; when nothing credible is found, it asks the operator once.
- Each worktree installs dependencies first; the skill finds the install command once — the project's CLAUDE.md, else the CI install step, else the manifest and lockfile — and passes it to the workers; when nothing credible is found, it asks the operator once.
- Gitignored files such as `.env` reach the worktrees only through the project's `.worktreeinclude`; the skill copies nothing, and the report hints when a missing file is the likely cause of a failure.
- When verification fails, the worker runs it on the new base alone. Red there too: a problem of the base or the environment, not blamed on the rebase. Green there: the resolution broke something, so the worker reworks it, then asks the operator.
- A PR whose validation still fails reaches the push confirmation marked failed, with "do not push" as the default; the operator keeps the last word.
- One question per incompatibility, stating what the merged side does, what the PR does, why both cannot hold, and what each answer changes, including the specs and tests of either side it rewrites or drops. Answers: keep the merged version (default), keep the PR version, or free text. A spec an answer contradicts is rewritten as a whole, not only its bullet. Up to four questions at a time per PR; after the answers, the same worker continues with its context intact.
- A question that closes unanswered, through Claude Code's optional question timeout, is not an answer: the PR keeps waiting, and a push confirmation closed this way means "do not push"; otherwise the timeout would let Claude go on alone.
- One push confirmation per PR, one at a time, showing the status and the reference used, what was done for each overlap and its class, the `Done means` results, the verification result, a warning that the push may dismiss approvals depending on the repository's rules, and a flag when the author is someone else. No comment is posted on the PR.
- The push refuses to overwrite a PR branch that changed since the run started, checked against the head recorded at the start; that PR then restarts from its new head. A push GitHub refuses for another reason is not retried: the PR is abandoned with GitHub's reason.
- PRs are handled one at a time, stacks included; two verification runs at once could collide on ports, databases or containers, and the failure would be wrongly blamed on the environment.
- Parents go before children: a child starts once its parent's push is confirmed, on the parent's pushed head; a parent the operator declines or GitHub refuses skips its children for this run, and the report says so.
- A child of the merged PR that GitHub did not retarget (the merged branch was not deleted) is retargeted to the merged PR's base as part of its own push confirmation.
- The run keeps its state in the project's `.roc/rocket/rebase-prs/` directory, per the repo's state convention: one state file for the run and one journal per PR, added to after each resolved commit.
- After an interrupted session, the next start offers to resume the run. On yes, each PR resumes where its rebase stopped — replayed commits kept, the commit it stopped on resolved again from its conflicted state — when its worktree still exists, its head and base have not moved and its journal matches the replayed commits; otherwise it restarts, and the report says which. On no, everything the run left is removed.
- After a resume, the final validation always re-runs on the whole PR.
- A PR's worktree is removed once the PR is pushed or abandoned, and kept while it waits for an answer. At the end, every worktree and worker branch the run created and the whole run directory, Notion exports included, are removed in a single command to limit permission prompts.
- If the project's `.gitignore` does not exclude `.claude/worktrees/` or `.roc/`, the skill warns once per missing entry and edits nothing.
- Settled: GitHub is the only forge; unsigned rebased commits and one PR at a time are accepted costs.

## Alternatives rejected

- Rebase by hand, as today — slow, and nothing checks that both sides survived.
- GitHub's "update branch" with rebase, from the PR page or `gh` — stops at the first conflict and checks no intent.
- GitHub's stacked PRs extension for `gh` (public preview) — leaves conflicts and intent to the operator.
- `gh` only — shuts out operators who only have the GitHub connector.
- Replay with signing on — an agent cannot type the passphrase.
- Look up the merged side's spec the way the PR's is found — a round trip through the skill for each overlap.
- A full review pass per PR to check `Done means` — an extra pass per PR for findings unrelated to the rebase.
- Independent stacks in parallel — simultaneous verification runs can collide.
- Restart every PR after an interruption — loses resolved commits and given answers.
- An install command slot in `/rocket:setup`'s template — changes every consumer's CLAUDE.md for one skill.
- A separate plugin for this skill — a second install for rocket's own audience.

## Done means

- `/rocket:rebase-prs` in a GitHub repository shows a numbered list of its open PRs: PRs behind their base, stacked ones included, are selectable; up-to-date PRs and fork PRs appear with the reason they are not; PRs by someone else, and PRs whose local branch holds commits not on GitHub, are flagged.
- A request in plain words such as "rebase my PRs" does not start the skill.
- With neither a usable GitHub connector nor `gh`, the skill prints one line naming the prerequisite and changes nothing.
- A full run, retargeting a stacked PR included, completes with the official GitHub connector alone, and with `gh` alone.
- After a run, the operator's checkout is unchanged: same current branch, same files, same local branches.
- With commit signing on in the operator's git setup, no rebase waits for a passphrase.
- A PR with no overlap is offered for push with a passing verification; after the push, GitHub shows it on the new base with the same changes as before.
- A PR that calls something the merged side renamed, with no textual conflict, is offered for push using the new name, with a passing verification.
- A PR that repeats a change the merged side already shipped keeps only what it adds on top; its confirmation names the dropped part and why.
- When the PR and the merged side change the same behavior in compatible ways, both behaviors are present after the rebase and the tests of both pass.
- When the PR and the merged side define the same behavior differently, the operator gets a question stating both behaviors and why they cannot both hold, with the merged version as default; that PR is not offered for push before the answer.
- After an answer, the PR continues without asking again the questions already answered.
- A resolution in which part of the PR disappears without a stated reason is never offered for push, and the report names the missing part.
- A verification failure that also happens on the new base alone is reported as older than the rebase.
- A PR whose verification fails only after the rebase is never offered for push unless marked failed, with "do not push" as the default.
- For a PR whose description links a Notion spec, the confirmation lists that spec's `Done means` bullets as met, not met or not assessable.
- With the Notion connector unavailable, the operator is asked to paste the spec or continue without it.
- Each push confirmation shows the status and the reference used, what was done for each overlap, the `Done means` results, the verification result, the approval warning, the other-author flag when it applies, and a note that the rebased commits are unsigned when the originals were signed.
- A question or confirmation left unanswered until it closes never leads to a push.
- A PR branch that someone else pushes to during the run is not overwritten, and that PR is redone from its new head.
- With A squash-merged and B stacked on A, after its push B holds only its own commits on top of A's base and targets A's base on GitHub.
- Declining A's push skips the PRs stacked on A for this run.
- No comment is added to any PR.
- At the end of a run, no worktree, worker branch or run file created by the run remains.
- After an interrupted run, the next start offers to resume it; on yes, it resumes the PRs that can be resumed, restarts the others, and says which.
- Declining that resume removes everything the interrupted run left.
- The final report lists each PR's outcome (pushed, declined, skipped, abandoned) and the local branches to reset.

## Reference

### Overlap classes

| Class | When it applies |
|---|---|
| Orthogonal | Neither side touches what the other relies on |
| Mechanical | The merged side changed a contract the PR uses: a renamed call, a new field, a moved rule |
| Redundant | Both sides make the same change |
| Composable | Both change the same behavior in compatible ways |
| Contradictory | Both define the same behavior differently |

### PR status

| Status | Meaning | Next |
|---|---|---|
| pending | Selected, not started | resolving |
| resolving | The worker replays and resolves commits | awaiting arbitration, resolved, abandoned |
| awaiting arbitration | Questions sent to the operator; worktree kept | resolving |
| resolved | Validated; push confirmation queued | pushed, abandoned, or pending when the branch changed on GitHub |
| pushed | On GitHub | — |
| abandoned | Declined by the operator, skipped because its parent was not pushed, or refused by GitHub; the reason is recorded | — |

The final report names the outcome from the recorded reason: pushed, declined, skipped or abandoned.

### Run state and journal

| Item | Content |
|---|---|
| PR number and branch | As on GitHub |
| Starting head | The PR's head on GitHub when the run started; the push overwrites nothing else |
| Starting base | The base head when the run started; for a stacked PR, its parent's old head |
| Worktree and worker branch | As reported by the worker |
| Status and reason | See PR status |
| Pending questions | Asked, not yet answered |
| Spec file | The spec the worker reads, or none |
| Journal entry, one per resolved commit | The commit, the overlap, its class, what was kept from each side, and why |

### Worker brief and result

| Direction | Content |
|---|---|
| Brief | PR number and branch; starting head; the new base (for a stacked PR, its parent's pushed head); for a stacked PR, its parent's old head; the spec file or none; the install and verification commands; answers to its questions |
| Result | Status; its own worktree path and branch; the rebased head; each overlap with its class, what was kept and why; the guard verdict for each part of the PR; the verification result, and the result on the base alone when run; each `Done means` verdict; questions for the operator |

## Risks and rollback

- Claude Code does not document that a resumed isolated worker keeps its worktree as its working directory; if it does not, the worker cannot find its rebase in progress, and that PR restarts from its head on GitHub.
- Branch rules may refuse the force push to a PR branch; it shows as an abandoned PR with GitHub's reason, the PR stays as it was on GitHub, and the operator handles it by hand.
- Claude Code treats `.claude/` as sensitive and may prompt when removing worktrees despite the single command; it shows as permission prompts at the end of the run, and anything a denied prompt leaves behind is offered for removal at the next start.
- Rollback of a pushed PR: GitHub's PR timeline shows the head before each force push, and pushing that head back restores the PR; a retargeted base is changed back on the PR page. The feature itself is removed by reverting the rocket version; it stores nothing outside the run directory.
