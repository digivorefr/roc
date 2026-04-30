---
name: no-code
disable-model-invocation: true
description: Force a chat-only response with no code writing, no file edits, no tool use that modifies the filesystem. Manual-only — invoked by the user via "/rocket:no-code" or "/no-code".
---

# No-Code Mode

The user has explicitly requested a conversation-only response. This overrides all default behavior.

## Rules

1. **Do NOT** create, edit, write, or delete any file
2. **Do NOT** use the Edit, Write, or NotebookEdit tools
3. **Do NOT** generate code blocks intended as file changes — if you show code, it is strictly illustrative within the chat
4. You may still **read** files and **run commands** (git, ls, grep, etc.) to gather context needed to answer
5. Respond entirely in the chat. Be direct, structured, and concise.

## What to do instead

- Explain, analyze, suggest, compare, critique — in prose
- Use code snippets inline only as illustrations, not as proposed edits
- If the user's question would normally result in a file change, describe what you *would* do and where, but do not do it
