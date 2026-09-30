---
name: rebase-prs
disable-model-invocation: true
description: Rebase open GitHub pull requests onto their moved base after another pull request was merged, keeping each PR's intent and the benefit of what was merged, with the operator arbitrating every uncertain resolution and confirming each push. Manual-only — invoked by the user via "/rocket:rebase-prs".
allowed-tools:
  - mcp__*__list_pull_requests
  - mcp__*__get_me
  - mcp__*__notion-fetch
  - Bash(git fetch *)
  - Bash(git remote *)
  - Bash(git rev-parse *)
  - Bash(git rev-list *)
  - Bash(git merge-base *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git ls-tree *)
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git symbolic-ref *)
  - Bash(git show-ref *)
  - Bash(git check-ignore *)
  - Bash(git worktree list *)
  - Bash(gh auth status *)
  - Bash(gh pr list *)
  - Bash(gh api user *)
  - Edit(.roc/rocket/rebase-prs/**)
  - Read
  - Grep
  - Glob
---

# Rebase PRs

A PR was merged and other open PRs fell behind their base. You orchestrate their rebase: the operator picks the PRs, one `rocket:pr-rebaser` worker per PR rebases it in its own worktree and reconciles it with everything merged since it branched, and you carry every question, every confirmation and every push. The operator arbitrates; nothing reaches GitHub without their yes, PR by PR.

## Rules

- **The operator's checkout is never modified.** In the main checkout you only read, `git fetch`, push commit SHAs to `origin`, and remove the worktrees this run created. No checkout, reset, rebase, commit or branch change there.
- **Only you push, and only after the operator's yes for that PR.** Workers never push.
- **One PR at a time**, stacks included: two verification runs at once can collide on ports, databases or containers.
- **Rebased commits are unsigned by design.** Never ask the operator about signing. A worker reporting a signing failure forgot its flag: send it back to re-run with signing off.
- **A PR moves only on its worker's final result.** Workers never message you; act on nothing else.
- **A question closed by the idle timeout is not an answer**, whatever options it carries: the PR keeps waiting, and a push confirmation closed that way means "do not push".
- Fork PRs are out of scope. No comment is ever posted on a PR. GitHub's branch update (connector or `gh pr update-branch`) is never used: it merges instead of rebasing.
- Never call `EnterWorktree` yourself; only workers enter worktrees.
- Everything you print to the operator is in English.

## Forge access

Each operation uses the GitHub connector when it exposes the tool, otherwise `gh`. A connector lacking a tool is not an error while `gh` covers it. An operation with neither → print exactly `GitHub access missing: connect the GitHub connector or install and log in gh (gh auth login).` and stop without changing anything.

| Operation | Connector tool | `gh` fallback |
|---|---|---|
| List PRs | `list_pull_requests` | `gh pr list --state <open\|merged> --json number,title,author,headRefName,headRefOid,baseRefName,isCrossRepository,body --limit 100` |
| Identify the operator | `get_me` | `gh api user --jq .login` |
| Change a PR's base | `update_pull_request` | `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -f base=<branch>` (not `gh pr edit`, which fails before gh 2.78 on the retired Projects classic query) |

Owner and repo come from `git remote get-url origin`. The rebase and the push are plain local git.

## Run state

Directory: `<project>/.roc/rocket/rebase-prs/`.

- `run.json` — written by you after every status change. Per PR: `number`, `head_ref`, `start_head`, `new_base_ref`, `new_base`, `old_upstream`, `parent`, `worktree`, `branch`, `worker_id`, `status` (`pending` | `resolving` | `awaiting-arbitration` | `resolved` | `pushed` | `abandoned`), `reason`, `pending_questions`, `spec_path`, `retarget_to`.
- `specs/pr-<n>.md` — the spec each worker reads, materialized by you.
- The per-PR journal lives inside each worker's worktree (`.roc/rocket/rebase-prs/journal.md`), because an isolated worker cannot write to the main checkout. A worktree holding that file is a worktree of this skill.

## Workflow

### Step 1 — Preflight

1. The repo's `origin` must be on GitHub; otherwise print `origin is not a GitHub repository.` and stop.
2. Resolve forge access per operation (table above).
3. For `.claude/worktrees/` and `.roc/`: when `git check-ignore -q <path>/x` fails, warn once: `.gitignore does not exclude <path>; run files may show as untracked.` Edit nothing.
4. Leftovers — `run.json` exists, or `git worktree list --porcelain` shows worktrees holding the journal file → ask one question (header `Resume`): `Resume the interrupted run` / `Discard it`. Resume → [Resume](#resume). Discard → run [Cleanup](#cleanup), then continue.

### Step 2 — Commands

Find both once, never again during the run:

- **Verification command**: the `### Verification command` block of the project's `CLAUDE.md`; else one read-only pass over manifest scripts, Makefile targets and CI workflows (read, never execute).
- **Install command**: the project's `CLAUDE.md`; else the install step of the CI workflow; else the manifest and its lockfile.

State each in one line. When nothing credible is found for one, ask the operator once (the automatic `Other` option takes the command).

### Step 3 — List and pick

1. `git fetch origin`. Default branch: `git symbolic-ref refs/remotes/origin/HEAD --short` without `origin/`.
2. Identify the operator. List open PRs. List merged PRs: one page of the most recently updated closed PRs, the API's maximum page size, keeping those with a merge date.
3. For each open PR:
   - **Parent**: an open PR whose head branch is its base branch; or a merged PR whose final head is an ancestor of its head and not of the default branch (`git merge-base --is-ancestor`). The merged PR's final head is `refs/pull/<n>/head`, fetched to a temporary ref under `refs/rocket/rebase-prs/` so its commits stay reachable during the run; fall back to its recorded head SHA.
   - **New base**: a child of a merged PR goes to the merged PR's base branch, and `retarget_to` is set when its base on GitHub is still the merged branch. Any other PR keeps its base branch.
   - **Old upstream**: the parent's head (final head for a merged parent, current head for an open one); `none` without a parent.
   - **Selectable** when its new base is not an ancestor of its head, or when it is stacked on a selectable PR.
   - **Excluded, shown with the reason**: `up to date`, `fork PR` (cross-repository).
   - **Flagged**: `author: <login>` when not the operator; `local branch ahead` when `refs/heads/<head_ref>` exists and holds commits not in its GitHub head.
4. Print the numbered list, parents before their children, one line per PR: number, `#<n>`, title, base → new base, flags or exclusion reason.
5. Ask one question (header `PRs`): `All selectable PRs` / `None`; the automatic `Other` takes numbers such as `1, 3`. A selected child whose selectable parent is not selected is skipped with the reason `parent not in this run`.

### Step 4 — Specs

For each selected PR, first match wins, then materialize it as `specs/pr-<n>.md`:

1. A spec file among the PR's own changes under the project's spec directory (`specs/` by default, or the location the project already uses): `git show <head>:<path>`.
2. A spec path or a Notion link in the PR description.
3. The same in its commit messages (`git log --format=%B <old upstream or merge-base>..<head>`).
4. A spec in the spec directory of the new base whose topic matches the files the PR changes — excluding the specs the merged side added or changed (`git diff --name-only <old upstream or merge-base> <new base> -- <spec dir>`). Those belong to the merged side: the worker checks them for non-regression, they are never the PR's own spec.

Several candidates → the operator picks. PR comments are never read. A Notion link is fetched once with `notion-fetch` and saved as markdown; without a Notion connector, ask (header `Spec`): `Paste the spec` (via `Other`) / `Continue without it` — never skip silently. No spec → `SPEC_PATH: none`.

### Step 5 — Process each PR

Order: parents before children, one PR at a time.

1. **Dispatch** a `rocket:pr-rebaser` agent as a plain subagent — foreground (`run_in_background: false`), no `name`, no team, never a teammate — and wait for its result before anything else, with its brief as flat `KEY: value` lines: `PR`, `HEAD_REF`, `START_HEAD`, `NEW_BASE` (the SHA; for a PR stacked on an open PR, the parent's pushed head), `OLD_UPSTREAM`, `SPEC_PATH` (absolute), `SPEC_DIR`, `INSTALL_CMD`, `VERIFY_CMD`, `RESUME_WORKTREE: none`. Set `resolving`; record `worker_id`, then `worktree` and `branch` from the result.
2. **Handle the result**:
   - `awaiting-arbitration` → [Questions](#questions).
   - `resolved` → check `REPLAYED`: for a stacked PR its upstream must be the `OLD_UPSTREAM` you sent, and its count must equal `git rev-list --count <OLD_UPSTREAM>..<start head>`. A mismatch means the worker replayed its parent's commits: restart the PR. Otherwise → [Push confirmation](#push-confirmation).
   - `blocked` → `abandoned`, reason: the parts listed `missing` in `GUARD`. Never offered for push.
   - `head-moved` → someone pushed to the PR: remove its worktree, refresh its head, restart it.
   - `restart` → remove its worktree, restart it from its head on GitHub.
3. A parent that ends `abandoned` for any reason (declined, blocked, refused by GitHub) skips its children for this run, reason `parent not pushed`.
4. Once a PR is `pushed` or `abandoned`, remove its worktree and worker branch (see [Cleanup](#cleanup)); keep it while the PR waits for an answer.

### Questions

- One question per worker `QUESTIONS` item, up to four per call, header `PR #<n>`. The question states what the merged side does, what the PR does and why both cannot hold. Options: `Merged version (Recommended)` / `PR version`, each with the item's `if merged` / `if PR` consequence as its description — every spec statement and test it rewrites or drops, on either side — so the operator decides knowing what changes. The automatic `Other` takes the operator's own resolution.
- Store the questions in `pending_questions` before asking. Send the answers to the same worker (`SendMessage` to `worker_id`), clear them once sent, and wait for its next final result: it is the only thing that moves the PR on.
- An answer from the idle timeout leaves the PR `awaiting-arbitration`: move on to PRs that do not depend on it and ask again before the run ends. Still unanswered then → the run ends with that PR waiting and its worktree kept; the next start offers to resume it.

### Push confirmation

Build the block below from the worker's result, complete — never summarized, every line that applies. Print it verbatim, then ask one question (header `Push #<n>`) whose `Push` option carries the same block as its `preview`, so it stays visible while the operator chooses; the other option is `Do not push`. When verification failed, or a `Done means` bullet is `not met`, the block is marked `FAILED` and `Do not push (Recommended)` comes first.

```
PR #42 — Add export retry · resolved · reference: spec (specs/export-retry.md)
Overlaps:
- mechanical · `fetchJob` now takes options → call site updated
- redundant · timeout constant already on main → PR's copy dropped
- contradictory · export cap → operator chose: merged version
Guard: 7 parts present, 1 adapted, 1 dropped (redundant)
Done means: 3 met, 1 not assessable ("export survives a network cut")
Verification: pass · pnpm check · "Tests 212 passed"
Retarget: base feature/export → main
Warnings:
- The push may dismiss approvals, depending on the repository's rules.
- Rebased commits are unsigned; the originals were signed.
- Author is @alice.
```

Omit a `Retarget` or `Warnings` line that does not apply; the approval warning is always present.

On `Push`:

1. `git push --force-with-lease=refs/heads/<head_ref>:<start_head> origin <rebased_head>:refs/heads/<head_ref>` from the main checkout. Refused because the branch changed → refresh the head and restart the PR. Refused for any other reason → `abandoned`, with GitHub's message as the reason; no retry.
2. When `retarget_to` is set: change the PR's base to it.
3. `pushed`. Its children now take its pushed head as `NEW_BASE`.

On `Do not push` → `abandoned`, reason `declined`.

## Resume

For each PR of `run.json` not `pushed` or `abandoned`:

1. Its worktree is the one listed in `run.json`, else the one whose journal names its `PR`. None → restart the PR from its head on GitHub.
2. `pending_questions` not empty → ask them first ([Questions](#questions)).
3. Dispatch a new worker with the recorded brief, `RESUME_WORKTREE: <path>`, and the answers. It resumes where the rebase stopped when it can, else returns `restart`.
4. Continue with [Step 5](#step-5--process-each-pr). The final report lists which PRs resumed and which restarted.

## Cleanup

One Bash command for everything, to limit permission prompts: for each worktree of this run (`run.json`, plus any worktree holding the journal file), `git worktree unlock <path>` when locked, `git worktree remove --force <path>`, `git branch -D <branch>`; then `git worktree prune`; then delete every ref under `refs/rocket/` (`git for-each-ref --format='%(refname)' refs/rocket/`, each with `git update-ref -d`); then remove `.roc/rocket/rebase-prs/`, then `.roc/rocket/` and `.roc/` when they are left empty (`rmdir`, which keeps a non-empty directory). At the end of a run nothing it created remains: no worktree, no worker branch, no temporary ref, no run file, no Notion export, no empty directory.

## Final report

```
Rebase run — 3 PRs
- #42 Add export retry · pushed · retargeted to main
- #45 Bulk export · abandoned · skipped: parent not pushed
- #47 Admin caps · abandoned · declined
Resumed: #42 · Restarted: none
Local branches to reset to their GitHub head: export-retry
```

The last line lists each local branch of a pushed PR that differs from what was pushed; `none` otherwise.
