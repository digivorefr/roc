---
name: inbox-watch-tick
description: Run a single Gmail inbox poll for the my-hand mail-session loop and emit a markdown summary table when new threads are found. Use this skill whenever the user invokes "/my-hand:inbox-watch tick", asks to "tick the inbox watcher", "force a poll now", "fais un tick", "force un poll", "regarde maintenant si j'ai du mail", or any similar request. Auto-invoke when the `loop` skill fires the registered `/my-hand:inbox-watch tick` command on its 10-minute schedule.
context: fork
agent: general-purpose
model: haiku
allowed-tools:
  - Bash("${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll":*)
  - mcp__*__search_threads
  - mcp__*__get_thread
  - Read(~/.roc/my-hand/tone.md)
---

# Mode

Single-tick Gmail inbox poller. Runs in a forked Haiku sub-agent. All non-LLM work (state I/O, ID comparison, table rendering, locking, notifications) is delegated to the `inbox-poll` binary. The LLM handles only MCP calls and judgment (classification, reply generation).

## Output contract

- **Empty poll**: return the empty string. No prose, no whitespace.
- **Non-empty poll**: return the markdown table produced by `inbox-poll render`, verbatim. Nothing else.
- **Error during MCP**: return `inbox-watch-tick: <short reason>`. Always unlock before returning.
- Never return conversational prose.

## Workflow

Execute these steps in order. Every `inbox-poll` call is a Bash invocation of `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll"`.

### 1. Lock

Run: `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" lock`

If output is `held`, return the empty string. Stop.

### 2. Get last poll date

Run: `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" last-poll --state ~/.roc/my-hand/inbox-state.json`

If output is `null` (first run): use `in:inbox` as the search query in the next step.
Otherwise: parse the ISO-8601 date and use `in:inbox after:YYYY/MM/DD` (Gmail date format).

### 3. Search Gmail

Call `search_threads` (MCP) with the query from step 2. Cap results at 50.

Extract all thread IDs into a JSON array of strings.

If MCP fails: run `inbox-poll unlock`, return `inbox-watch-tick: <reason>`. Stop.

### 4. Check for new threads

Run: `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" check --state ~/.roc/my-hand/inbox-state.json --ids '<ids_json>'`

If output is `empty`: run `inbox-poll unlock`, return the empty string. Stop.

Parse the JSON output to get `new_ids`.

### 5. Fetch new threads

For each ID in `new_ids`, call `get_thread` (MCP). Extract: sender, company (best-effort from domain/signature), subject, message body.

### 6. Read tone profile (only if needed)

If any thread looks like it needs a reply, `Read` `~/.roc/my-hand/tone.md`. If missing or under 100 bytes, set `tone_missing = true`.

### 7. Classify and generate

For each thread, produce a JSON object:

```json
{"reply": true, "sender": "Name", "company": "Acme", "subject": "...", "suggestion": "..."}
```

- `reply`: true if the user owes a reply (direct address, question, action item). False for newsletters, promotions, automated mail.
- `suggestion`: 2-4 sentence reply grounded in `tone.md`, in the language of the source message. If `tone_missing`: `(profile missing — run /my-hand:tone-profile)`. Null if `reply` is false.

Collect all objects into a JSON array.

### 8. Render table

Pipe the JSON array to stdin: `echo '<analysis_json>' | "${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" render`

Capture stdout as TABLE.

### 9. Update state

Build a patch JSON and pipe to stdin:

`echo '<patch_json>' | "${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" update --state ~/.roc/my-hand/inbox-state.json`

Patch format: `{"add_seen_ids": [...], "pending_replies": {...}}` where `pending_replies` maps thread ID to `{"sender", "company", "subject", "short_suggestion"}` for threads where `reply` is true.

### 10. Notify

Run: `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" notify --count N --senders "Name1, Name2"`

Pass a comma-separated list of up to 3 sender names. If N > 3, append `, +M more` where M = N - 3.

### 11. Unlock

Run: `"${CLAUDE_PLUGIN_ROOT}/bin/darwin-arm64/inbox-poll" unlock`

### 12. Return

Return TABLE verbatim. Nothing else.

## What NOT to do

- Do NOT call `create_draft` or any send/label/archive/trash tool.
- Do NOT emit conversational prose.
- Do NOT translate the notification title (French is intentional).
- Do NOT request more than 50 threads from Gmail.
- Do NOT skip unlocking on any exit path.
