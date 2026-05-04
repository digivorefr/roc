---
name: inbox-watch-tick
description: Run a single Gmail inbox poll for the my-hand mail-session loop and emit a markdown summary table when new threads are found. Use this skill whenever the user invokes "/my-hand:inbox-watch tick", asks to "tick the inbox watcher", "force a poll now", "fais un tick", "force un poll", "regarde maintenant si j'ai du mail", or any similar request. Auto-invoke when the `loop` skill fires the registered `/my-hand:inbox-watch tick` command on its 10-minute schedule.
context: fork
agent: general-purpose
allowed-tools:
  - Bash(mkdir:*)
  - Bash(rmdir:*)
  - Bash(rm:*)
  - Bash(stat:*)
  - Bash(date:*)
  - Bash(osascript:*)
  - mcp__*__search_threads
  - mcp__*__get_thread
  - Read(~/.roc/my-hand/**)
  - Write(~/.roc/my-hand/**)
  - Edit(~/.roc/my-hand/**)
---

# Mode

Single-tick Gmail inbox poller for the my-hand mail-session loop. Runs in a forked sub-agent with a clean context: this skill cannot see the parent conversation, and the only signal it returns to the parent is the string produced at step 14 of the workflow below. Per-tick context cost is therefore bounded regardless of conversation length in the parent.

This skill is intentionally narrow:

- It reads a small JSON state file, queries Gmail MCP, possibly writes the state file back, possibly fires a macOS notification, and returns either an empty string or a single short markdown table.
- It never calls `create_draft` or any send tool. Drafting is the exclusive responsibility of `/my-hand:inbox-reply`.
- It never produces conversational prose. The output is the table or nothing.

## Permissions note

Empirical finding (Claude Desktop, May 2026): forked sub-agents do **not** inherit `allowed-tools` from the parent slash command. Each tick was prompting the user for `Edit` on `inbox-state.json`, for the `trap` Bash command, and so on, breaking the silent-background contract of the loop. The skill therefore redeclares its own `allowed-tools` in the frontmatter above. Keep that list as the single source of truth for what this skill needs at runtime; the parent slash command can keep its own broader list, but it is not what the harness consults inside the fork.

# Output contract

- **Empty poll** (zero new threads after filtering): return the empty string. No prose. No leading or trailing whitespace. No notification.
- **Non-empty poll**: return a single markdown table followed by a blank line followed by a single English footer line. Nothing else.
- **Error during MCP**: return exactly one English line of the form `inbox-watch-tick: <short reason>`. Skip the macOS notification. Always release the lock before returning.
- Never return prose like `Here are the new emails:`, `Tick complete.`, `No new mail.`, or any conversational framing. The output is the table or nothing.

Markdown table shape:

| Reply? | From (company) | Subject | Suggested reply |
| --- | --- | --- | --- |
| ✅ | Marie Dupont (Acme) | Confirmation devis Q3 | Hello Marie, validé. ... |
| — | Newsletter Foo | Weekly digest |  |

Rules for the table:

- Column headers exactly as shown.
- `Reply?` is `✅` if the user owes a reply, `—` otherwise.
- Drop the `(company)` parenthetical when the company is not knowable from sender domain or signature.
- Strip pipes (`|` becomes `\|`) and newlines (line breaks become `; `) from any text rendered inside a cell.
- The `Suggested reply` cell is empty for rows where `Reply?` is `—`.
- If the tone profile is missing (see step 4), every `Suggested reply` cell becomes `(profile missing — run /my-hand:tone-profile)`.

Footer line, English, always identical:

```
Run /my-hand:inbox-reply <sender or subject> to draft a reply in the thread.
```

# Workflow

Each step below is a directive. Execute them in order.

## Bash discipline (read this once, apply at every Bash call below)

Issue every Bash command **as a single atomic invocation**. Do not chain commands with `&&`, `||`, or `;`. Do not pipe. Do not redirect into shell substitution (`$(...)`) inside the same call. Each Bash call must be one program with its arguments. The harness's permission matcher inspects the literal command string, and chained or composite forms do not match the prefix patterns declared in this skill's `allowed-tools` block. If you need two operations, run two separate Bash calls.

Also: this skill does **not** use a shell `trap` to release the lock. The harness flags `trap` as evaluating arbitrary shell code and refuses to permanently approve it. Instead, the workflow below releases the lock by an explicit `rmdir` at every exit point (success, empty-poll, error). Treat that explicit release as mandatory — every return path must run `rmdir ~/.roc/my-hand/mail-poll.lock.d/` before returning, except the lock-not-acquired path (where there is nothing to release).

## Step 1 — Acquire the lock

Run, as two separate Bash calls (do not chain):

1. `mkdir -p ~/.roc/my-hand/`
2. `mkdir ~/.roc/my-hand/mail-poll.lock.d/`

If the second `mkdir` returns non-zero (lock already held), perform a stale-lock check:

1. `stat -f %m ~/.roc/my-hand/mail-poll.lock.d/` — capture the mtime.
2. `date +%s` — current epoch seconds.
3. Compute `now - mtime` mentally.

If the lock's age `>= 600` seconds, reap it:

1. `rmdir ~/.roc/my-hand/mail-poll.lock.d/`
2. `mkdir ~/.roc/my-hand/mail-poll.lock.d/`

If the second `mkdir` still fails after that retry, return the empty string and exit immediately. There is no lock to release in this branch — you never acquired it. Do not loop further.

## Step 2 — Read state

`Read` `~/.roc/my-hand/inbox-state.json`. On absence or JSON parse failure, treat the state as fresh:

```json
{ "last_seen_thread_ids": [], "last_poll_at": null, "pending_replies": {} }
```

## Step 3 — Read the tone profile

`Read` `~/.roc/my-hand/tone.md`. If it is missing or smaller than 100 bytes, set an internal flag `tone_missing = true`. The table will still render in the non-empty case; only the `Suggested reply` cells will be replaced by `(profile missing — run /my-hand:tone-profile)`.

## Step 4 — Query Gmail

Use the Gmail MCP `search_threads` tool. Construct the query as follows:

- If `last_poll_at` is non-null, use a query equivalent to `in:inbox newer:<ISO date of last_poll_at>` (translate to the Gmail-recognized `after:` syntax: `in:inbox after:YYYY/MM/DD`).
- If `last_poll_at` is null (first run), use `in:inbox` with a result cap of 50 threads.

Cap the result set at 50 in either case. Do not request more.

## Step 5 — Filter

Drop any thread whose ID appears in `last_seen_thread_ids`.

## Step 6 — Empty case

If the filtered set is empty:

1. Update `last_poll_at` in the in-memory state to the current ISO-8601 UTC timestamp (e.g. `2026-05-04T10:30:00Z`).
2. Persist the state to disk via `Write` (full rewrite). `Edit` is also acceptable for a minimal patch when only `last_poll_at` changed.
3. Release the lock: run `rmdir ~/.roc/my-hand/mail-poll.lock.d/` as a single Bash call.
4. Return the empty string. Stop.

## Step 7 — Non-empty case

For each new thread:

1. Call `get_thread` to retrieve the full thread content.
2. Identify the most recent message. Extract sender display name and address.
3. Best-effort company: pull from a recognizable signature line, otherwise from the sender's email domain (e.g. `marie@acme.com` → `Acme`). When uncertain, leave company empty.
4. Truncate the subject to 60 characters, appending `…` if truncated.
5. Decide whether the user owes a reply. Heuristics: direct address to the user, an explicit question, an action item directed at the user, an awaited confirmation. Newsletters, promotions, automated notifications, and bulk mailings are `—` by default.
6. If `Reply?` is `✅` and `tone_missing` is false, generate a 2-4 sentence reply suggestion grounded in `tone.md`, in the language of the source message. If `tone_missing` is true, the suggestion is `(profile missing — run /my-hand:tone-profile)`.

## Step 8 — Build the markdown table

Render the table per the Output contract above. Strip `|` and newlines from cell content as specified. Emit the header row exactly as shown.

## Step 9 — Build the footer

Append a blank line, then exactly:

```
Run /my-hand:inbox-reply <sender or subject> to draft a reply in the thread.
```

## Step 10 — Update state

In-memory:

- Prepend the new thread IDs to `last_seen_thread_ids`. Cap the list at 200 entries; drop the oldest (tail) when over capacity.
- For each new thread where `Reply?` is `✅`, add an entry to `pending_replies` keyed by the thread ID:

  ```json
  {
    "sender": "Marie Dupont",
    "company": "Acme",
    "subject": "Confirmation devis Q3",
    "short_suggestion": "Hello Marie, validé. ..."
  }
  ```

  Drop empty fields rather than emitting null/empty strings if you prefer; a missing key is acceptable.

- Cap `pending_replies` at 200 entries by insertion order. When over capacity, drop the oldest keys first. Preserve insertion order when writing — render the JSON object with keys in insertion order so the eviction policy stays stable across runs.
- Update `last_poll_at` to the current ISO-8601 UTC timestamp.

Persist via `Write` (full rewrite is fine for V1; the lock serializes writers and the file stays well under the size that would benefit from atomic tmp+rename). Document this trade-off: V1 accepts a non-atomic write because writes happen at most every 10 minutes and the lock prevents concurrent writers. If real usage shows corruption, V2 reintroduces a Python helper for state I/O.

## Step 11 — macOS notification

Build a senders list of up to 3 names (use the display name extracted at step 7.2). If the new-thread count `N` exceeds 3, append `+M more` where `M = N - 3`.

Escape any embedded double quotes in sender names: `"` becomes `\"`. Then run:

```bash
osascript -e 'display notification "From: <senders>" with title "Claude — N nouveau(x) mail(s)" sound name "default"'
```

Substitute the real `N` (count of new threads, regardless of `Reply?` status) and the real `<senders>` string. The title is intentionally French — single recognized banner string. Do not translate.

## Step 12 — Release the lock

Run `rmdir ~/.roc/my-hand/mail-poll.lock.d/` as a single Bash call. This is the happy-path release. Step 6 (empty-poll path) and the Gmail-error edge case both also release the lock explicitly — this is mandatory because there is no shell trap.

## Step 13 — Return the result

Return the markdown table from step 8, a blank line, and the footer from step 9, as a single string. This is what the parent conversation sees. Do not prepend or append anything.

# Edge cases

- **`~/.roc/my-hand/` directory missing**: step 1 creates it via `mkdir -p`.
- **`inbox-state.json` malformed**: step 2 treats it as fresh (empty arrays / objects).
- **Lock held and not stale**: step 1 returns the empty string after the stale-reap retry. Do not retry beyond that, do not loop.
- **Gmail MCP returns 0 threads or 0 after filtering**: step 6 empty path. No notification.
- **Stale `pending_replies` entry** (thread deleted in Gmail): leave it in place. The 200-entry cap will eventually evict it. Do not preemptively garbage-collect.
- **Cell content contains `|`**: escape as `\|`. Cell content with newlines: replace each newline with `; `.
- **Sender name contains `"`**: escape to `\"` before passing into the `osascript` body string.
- **Gmail MCP raises an error** (auth failure, network, server error): release the lock via a single Bash call `rmdir ~/.roc/my-hand/mail-poll.lock.d/`, return `inbox-watch-tick: <short reason>`, skip the notification, do not write state.
- **Tone profile contains characters that would break the table**: escape pipes and strip newlines in the `Suggested reply` cell content, same rule as user-data cells.

# What NOT to do

- Do NOT call `create_draft`, any send tool, any label-mutation tool, or any archive/trash tool. This skill is read + state-update only.
- Do NOT translate the macOS notification title to English. `Claude — N nouveau(x) mail(s)` is intentional.
- Do NOT emit conversational prose to the parent. Return the table-or-nothing string only.
- Do NOT block waiting for a held lock. If `mkdir` fails after the stale-reap retry, exit with the empty string.
- Do NOT skip releasing the lock on the error path. Step 13's `rmdir` is mandatory before returning an error string.
- Do NOT re-read the parent conversation. The fork has its own clean context and the parent's content is not relevant to the tick.
- Do NOT request more than 50 threads from Gmail per tick.

# Good examples

## Empty tick

Return value (literal — empty string, zero characters):

```

```

(Nothing rendered to the parent. No notification fired. `last_poll_at` advanced.)

## Non-empty tick — 2 new threads, tone profile present

```
| Reply? | From (company) | Subject | Suggested reply |
| --- | --- | --- | --- |
| ✅ | Marie Dupont (Acme) | Confirmation devis Q3 | Hello Marie, validé. Je relance Patrick demain pour le détail technique. À mardi. |
| — | Newsletter ProductHunt | Weekly digest |  |

Run /my-hand:inbox-reply <sender or subject> to draft a reply in the thread.
```

(macOS banner: title `Claude — 2 nouveau(x) mail(s)`, body `From: Marie Dupont, Newsletter ProductHunt`.)

## Non-empty tick — tone profile missing

```
| Reply? | From (company) | Subject | Suggested reply |
| --- | --- | --- | --- |
| ✅ | Marie Dupont (Acme) | Confirmation devis Q3 | (profile missing — run /my-hand:tone-profile) |

Run /my-hand:inbox-reply <sender or subject> to draft a reply in the thread.
```

## Error path

```
inbox-watch-tick: gmail mcp unreachable
```

(Lock released. No notification. State not written.)

# Bad examples

## Conversational framing

```
Here are the 2 new emails I found in your inbox:

| Reply? | ...
```

(Forbidden. The output is the table only.)

## Empty-tick prose

```
No new mail since the last poll.
```

(Forbidden. Empty tick returns the empty string.)

## English notification title

```
osascript -e 'display notification "..." with title "Claude — 2 new email(s)" ...'
```

(Forbidden. Title stays French per the spec.)
