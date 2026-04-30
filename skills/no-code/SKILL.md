---
name: no-code
user-invocable: true
description: Force a chat-only response with no code writing, no file edits, no tool use that modifies the filesystem. Use this skill whenever the user says "/roc:no-code", "/no-code", "no code", "pas de code", "just explain", "explique juste", "don't write code", "don't touch the code", "réponds juste", "just answer", or any signal that the next request should be answered purely in conversation without creating or editing any files.
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
