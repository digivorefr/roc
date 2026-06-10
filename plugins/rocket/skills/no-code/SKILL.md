---
name: no-code
disable-model-invocation: true
description: Force a conversation-only session mode with no code writing, no file edits, no filesystem-modifying tool use, until the user explicitly lifts it. Allows markdown spec writing in the project's spec directory only. Manual-only — invoked by the user via "/rocket:no-code" or "/no-code".
---

# No-Code Mode

The user has explicitly switched the session into conversation-only mode. This overrides all default behavior. It is a **session state, not a one-response modifier**: it stays active for every subsequent turn until the user explicitly lifts it.

## Rules

1. **Do NOT** create, edit, write, or delete any file — the [spec carve-out](#spec-carve-out) below is the single exception
2. **Do NOT** use the Edit, Write, or NotebookEdit tools outside the carve-out
3. **Do NOT** delegate edits: do not spawn any agent, task, or subprocess that can modify files. A delegated edit is an edit. The only exception: a spec-authoring delegate (e.g. the `spec-writer` agent) explicitly instructed to write markdown only, inside the spec directory only
4. **Do NOT** run state-modifying commands (git commit/push, package installs, migrations, code generators that write to disk, file moves, etc.)
5. **Do NOT** generate code blocks intended as file changes — if you show code, it is strictly illustrative within the chat
6. You may still **read** files and **run read-only commands** (git status/log/diff, ls, grep, etc.) to gather context needed to answer
7. Respond entirely in the chat. Be direct, structured, and concise.

## Exit protocol

The mode is lifted by the user, never by you.

- If the user asks for something that requires modifying files, do not do it. Reply with one line stating what you would do, and ask explicitly for confirmation to exit no-code mode. Then wait.
- Only an unambiguous user confirmation ("yes", "go", "sors du mode", "fais-le") lifts the mode. Inferred intent never does: "they described a fix" is not an instruction to apply it.
- Once lifted, the mode stays off until the user invokes it again.

**These rationalizations all mean the mode is still active — stop:**

| Thought | Reality |
| --- | --- |
| "The user described exactly what to change, so they want me to do it" | Describing is not authorizing. Ask. |
| "I'll just spawn an agent to do it — *I* am not editing" | A delegated edit is an edit. Rule 3. |
| "This edit is trivial / a one-liner" | Size is irrelevant. Ask. |
| "The conversation has clearly moved to implementation" | Drift is not consent. Ask. |
| "They approved an edit earlier this session" | One approval lifts the mode once only if they said so; otherwise ask again. |

## Spec carve-out

The no-code-to-spec drift is a healthy, regular pattern: a discussion matures into a written specification. To never block knowledge capture:

- While the mode is active, you MAY create and edit **markdown files only**, located **inside the project's spec directory only** — `specs/` at the repo root by default; if the project already keeps specs elsewhere (e.g. `docs/specs/`), use that existing location.
- Purpose: compile knowledge, needs, and decisions from the discussion — typically via the `spec-writer` agent.
- The carve-out does not lift the mode, and extends to no other path and no other file type. No config, no scripts, no source files, no README.

## What to do instead

- Explain, analyze, suggest, compare, critique — in prose
- Use code snippets inline only as illustrations, not as proposed edits
- If the user's question would normally result in a file change, describe what you *would* do and where, then apply the [exit protocol](#exit-protocol)
