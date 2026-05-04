---
description: Manage the Gmail mail-session loop or force a single poll. Use this command whenever the user invokes "/my-hand:inbox-watch", "/my-hand:inbox-watch start", "/my-hand:inbox-watch stop", "/my-hand:inbox-watch tick", says "inbox watch", "start inbox watcher", "watch my inbox", "check inbox", "force poll", "stop the inbox watcher", "surveille ma boite", "surveille mes mails", "regarde mes mails", "lance la veille mail", "force un poll", "arrete la veille mail", or any similar request to start, stop, or trigger a Gmail inbox poll.
argument-hint: start | stop | tick
allowed-tools:
  - Bash(pwd:*)
  - Bash(realpath:*)
  - Bash(mkdir:*)
  - Bash(cat:*)
  - Bash(rm:*)
  - Bash(osascript:*)
  - mcp__*__search_threads
  - mcp__*__get_thread
  - Read
  - Write
  - Edit
  - Skill
---

You are the dispatcher for the my-hand Gmail mail-session loop. The user's argument is `$ARGUMENTS` (whitespace-trimmed).

## No-send guarantee

This command never sends mail. The `allowed-tools` list does not include any send-capable Gmail tool, and explicitly omits `create_draft`. Drafts are the exclusive responsibility of `/my-hand:inbox-reply`. Do not call any draft-creation or send tool from this command's flows.

## Routing

Inspect `$ARGUMENTS` after trimming whitespace and route to one of four paths.

### Empty argument — print state and help

1. Run `mkdir -p ~/.roc/my-hand/` to ensure the directory exists.
2. If `~/.roc/my-hand/mail-session.path` exists, `Read` it and report `Auto-restart: enabled, mail-session at <path>`.
3. Otherwise, report `Auto-restart: disabled`.
4. Append the line `Run /my-hand:inbox-watch start | stop | tick`.
5. Stop. Do not invoke any tool beyond the read.

### `start`

Issue every Bash call as a single atomic command. Do not chain with `&&`, `||`, or `;`. The harness's permission matcher inspects the literal command string and rejects compound forms.

1. Run `mkdir -p ~/.roc/my-hand/` as one Bash call.
2. As a separate Bash call, resolve the current working directory via `realpath .` (or `pwd` as fallback). Strip any trailing newline. Call this `MAIL_SESSION_PATH`.
3. `Write` `MAIL_SESSION_PATH` to `~/.roc/my-hand/mail-session.path` as a single line, no surrounding whitespace.
4. Check `~/.roc/my-hand/tone.md`. If absent, print: `Voice profile missing. Run /my-hand:tone-profile to enable reply suggestions.` Continue regardless.
5. Invoke the `loop` skill via the `Skill` tool with the argument `10m /my-hand:inbox-watch tick`. The loop runs in the background of this conversation.
6. Confirm to the user: `Mail session configured at <MAIL_SESSION_PATH>. Polling every 10 minutes.`

### `stop`

1. Run `rm -f ~/.roc/my-hand/mail-session.path` to remove the auto-restart sentinel.
2. Print exactly:

```
Auto-restart disabled. The current loop is still running in this conversation; in V1, /my-hand:inbox-watch stop only removes the sentinel. To stop polling immediately, end this conversation. The next conversation in this project will not auto-resume.
```

3. Stop.

### `tick`

1. Invoke the `inbox-watch-tick` skill via the `Skill` tool with no argument.
2. Forward the skill's output verbatim to the user. Do not add a header, prefix, suffix, or restatement.
3. If the skill returns the empty string, this command produces no visible output. Do not say "no new mail", do not say "tick complete".

## Notes

- The `tick` subcommand is legal as a manual force-poll. The design assumes it is invoked from the `loop` skill set up by `start`.
- The `inbox-watch-tick` skill runs in a forked sub-agent (`context: fork`, `agent: general-purpose`), so per-tick context cost is bounded.
- All Gmail MCP and notification work happens inside that skill. This command does not call `search_threads`, `get_thread`, or `osascript` directly — those entries in `allowed-tools` exist solely so the forked sub-agent can use them if its inherited permissions require parent-level pre-approval.
