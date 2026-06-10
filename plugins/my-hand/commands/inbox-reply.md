---
description: Finalize a Gmail draft inside an existing thread, in the user's voice, never sending. Use this command whenever the user invokes "/my-hand:inbox-reply", says "reply to <name>", "draft a reply to <name>", "prepare a draft", "draft a response to <subject>", "répond à", "réponds à", "rédige une réponse pour", "prépare une réponse à", "fais un brouillon pour", or any similar request to author a reply draft to a Gmail thread.
argument-hint: <sender or subject keyword>
allowed-tools:
  - mcp__*__search_threads
  - mcp__*__get_thread
  - mcp__*__create_draft
  - Read
---

You are drafting a Gmail reply in the user's own voice and saving it as a draft inside the existing thread. The argument from the user is `$ARGUMENTS`, free-form (sender name, company, subject keyword, or any combination).

## No-send guarantee — read this first

**Use `create_draft` only. Never send. Sending is forbidden.**

The `allowed-tools` list deliberately excludes any tool capable of sending mail, archiving, trashing, modifying labels, or otherwise mutating the thread beyond writing a draft attached to it. If you find yourself reaching for any tool not in `allowed-tools`, stop and report the limitation instead.

## Workflow

1. `Read` `~/.roc/my-hand/tone.md`. If the file does not exist, print exactly `Voice profile missing. Run /my-hand:tone-profile first.` and stop. Do not call any Gmail tool.
2. Call `search_threads` with `$ARGUMENTS` as the free-text query, capped at the most recent ~20 results. If 0 results, print exactly `No matching thread for "<args>".` and stop.
3. If more than 1 plausible candidate, list them as a markdown bullet list:

```
- <sender> (<company>) — <subject> — <thread_id>
```

   Drop the `(<company>)` parenthetical for entries where company is unknown. Then ask the user to disambiguate by re-running the command with a more specific keyword. Do not call `create_draft`.
4. If exactly 1 candidate, call `get_thread` for the full thread to confirm context (latest message, full subject, direction).
5. If the latest inbound message asks questions or requests decisions whose answers you do not have from the conversation, ask the user for those answers first — one short message listing the questions, or a single `AskUserQuestion` call. Do not invent answers, do not draft around them.
6. Author a polished email body, 2-4 sentences, in the language of the original message (FR or EN as appropriate), grounded in `tone.md` and in the user's answers from step 5.
7. Call `create_draft` with the message body and the matching `thread_id` so the draft is attached to the existing conversation. Do not create a new thread.
8. Confirm to the user with exactly: `Draft created in thread <thread_id>. Nothing was sent. Open Gmail to review and send manually.`

## Failure handling

- Any Gmail MCP error during `search_threads`, `get_thread`, or `create_draft`: surface a single English line describing the failure and stop. Do not retry, do not fall back to a different tool.
- If `tone.md` is present but empty or smaller than 100 bytes, treat the voice profile as missing and direct the user to `/my-hand:tone-profile`.
