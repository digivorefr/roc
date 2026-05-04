---
name: context-clear
disable-model-invocation: true
description: Wipe the project's rocket-managed contextualization files (lexicon, logs, locks) under .roc/rocket/. Use this skill whenever the user invokes "/rocket:context-clear", says "clear context", "reset the lexicon", "wipe the lexicon", "clean context files", "nettoie le contexte", "supprime les fichiers de contextualisation", "réinitialise le lexique", "vide le lexique", "remets le contexte à zéro", or any similar request to discard the rocket contextualization state for the current project.
---

# Project rocket-context cleaner

Wipe the rocket contextualization files in the current project: the lexicon, the wrapper logs, leftover lock dirs, and any leftover atomic-write temp files. Two-step UX: first invocation lists, second invocation with `force` deletes.

## Scope

Strictly the **current project**, under `.roc/rocket/`:

- `.roc/rocket/lexicon.md` — the project lexicon.
- `.roc/rocket/lexicon.md.tmp` — leftover atomic-write temp file (if any).
- `.roc/rocket/lexicon-update.log`, `.log.1`, `.log.2`, `.log.3` — wrapper logs (rotated).
- `.roc/rocket/lexicon.md.lock.d/` — atomic lock directory (transient).
- `.roc/rocket/` itself — removed only if empty after cleanup.
- `.roc/` itself — removed only if empty (other plugins may still use it).

This skill does **not** touch:

- `CLAUDE.md` — the `## Project semantic context` block stays. To remove it, edit `CLAUDE.md` manually.
- `~/.roc/...` — user-global state (other plugins, voice profiles, mail state). Out of scope.
- Other plugins' state under `.roc/<other-plugin>/`.

## Workflow

The argument from the user is `$ARGUMENTS` (whitespace-trimmed, lowered).

### Empty argument — list mode

1. Run `ls -la .roc/rocket/ 2>/dev/null` as a single Bash call to enumerate what is there.
2. If `.roc/rocket/` does not exist or is empty, print exactly: `No rocket contextualization files in this project.` and stop.
3. Otherwise, print the listing with sizes followed by exactly:

```
Run /rocket:context-clear force to actually delete these files. Re-run /rocket:setup afterwards if you want to re-bootstrap the lexicon.
```

4. Stop. Do not delete anything in list mode.

### `force` — delete mode

Issue every Bash call as a **single atomic command**. Do not chain with `&&`, `||`, `;`. Each step below is one separate Bash invocation.

1. `rm -f .roc/rocket/lexicon.md`
2. `rm -f .roc/rocket/lexicon.md.tmp`
3. `rm -f .roc/rocket/lexicon-update.log`
4. `rm -f .roc/rocket/lexicon-update.log.1`
5. `rm -f .roc/rocket/lexicon-update.log.2`
6. `rm -f .roc/rocket/lexicon-update.log.3`
7. `rmdir .roc/rocket/lexicon.md.lock.d/` (Bash exit code may be non-zero if missing — fine).
8. `rmdir .roc/rocket/` (Bash exit code may be non-zero if other rocket files remain — fine).
9. `rmdir .roc/` (Bash exit code may be non-zero if other plugins still occupy it — fine).
10. Confirm to the user: `Cleared rocket context files for this project. Run /rocket:setup to re-bootstrap if needed.`

### Any other argument

Print exactly: `Unknown argument "<arg>". Use /rocket:context-clear (list mode) or /rocket:context-clear force (delete).` and stop.

## What NOT to do

- Do NOT use `rm -rf .roc/` indiscriminately. Other plugins may live there. Step 7-9 above use plain `rmdir`, which fails (and that's fine) when the directory still has content.
- Do NOT touch `CLAUDE.md`.
- Do NOT touch `~/.roc/...` (user-global state).
- Do NOT chain multiple deletions in a single Bash call. The harness's permission matcher inspects each command literally; one-shot batch deletes are harder to pre-approve.
- Do NOT confirm-and-delete in a single invocation. The list step is mandatory before destruction — it gives the user a chance to back out.

## Good example — list mode

User: `/rocket:context-clear`

```
total 32
-rw-r--r--  1 user  staff   8217 May  4 13:00 lexicon.md
-rw-r--r--  1 user  staff   1190 May  4 13:30 lexicon-update.log

Run /rocket:context-clear force to actually delete these files. Re-run /rocket:setup afterwards if you want to re-bootstrap the lexicon.
```

## Good example — force mode

User: `/rocket:context-clear force`

```
Cleared rocket context files for this project. Run /rocket:setup to re-bootstrap if needed.
```

## Bad examples

- Auto-deleting on `/rocket:context-clear` without the explicit `force` confirmation step. Always two-step.
- Touching `CLAUDE.md` to remove the `## Project semantic context` section. Out of scope.
- Recursively deleting `.roc/` with `rm -rf`. Other plugins may occupy it.
- Wiping `~/.roc/rocket/` (user-global). This skill is project-scoped.
