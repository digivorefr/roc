---
description: Distill the user's email voice from the last 30 days of sent Gmail into ~/.roc/my-hand/tone.md. Use this command whenever the user invokes "/my-hand:tone-profile", says "tone profile", "voice profile", "analyse my style", "build my voice profile", "mon style", "analyse mon style", "profil de ton", "profil de voix", "construis mon profil de ton", "rafraichis mon profil de ton", or any similar request to capture or refresh their email voice.
argument-hint: [optional notes for the model]
allowed-tools:
  - mcp__*__search_threads
  - mcp__*__get_thread
  - Read
  - Write
  - Bash(mkdir:*)
---

You are building or refreshing the user's email voice profile. The output is a single markdown file at `~/.roc/my-hand/tone.md` that other my-hand commands (notably `/my-hand:inbox-reply`) read to ground reply drafts in the user's actual style.

Free-form notes from the user (may be empty): `$ARGUMENTS`

## No-send guarantee

This command is read-only with respect to Gmail. Use `search_threads` and `get_thread` only. Do not call any draft-creation, send, label-mutation, or archive tool.

## Workflow

1. Ensure the state directory exists by running `mkdir -p ~/.roc/my-hand/`.
2. If `~/.roc/my-hand/tone.md` already exists, `Read` it and treat it as a starting reference (not as required input).
3. Use the Gmail MCP `search_threads` tool with a query equivalent to `in:sent newer_than:30d`, capped at 50 threads. If the MCP returns fewer, use what is available.
4. For each returned thread, call `get_thread` and locate the user-composed message body. Drop quoted reply blocks (lines beginning with `>` or after `On <date> ... wrote:` markers), drop forwarded blocks, and drop verbatim signatures.
5. From the cleaned corpus, distill 5-10 saliency bullets describing voice traits: typical message length, openings, closings, formality register per context, FR/EN switching habits, signatures, idiomatic tics. Be specific, not generic.
6. Pick exactly three representative example messages — short, verbatim, covering distinct contexts (for example: formal client, internal casual, terse acknowledgment). Strip any quoted/forwarded fragments before including the body.
7. Compose the file using the canonical shape below, with `<YYYY-MM-DD>` filled in (today's UTC date) and `<N>` filled in (the number of sent emails actually used).

```
# my-hand tone profile

Generated <YYYY-MM-DD> from <N> sent emails over the last 30 days.

## Saliency

- <bullet 1>
- <bullet 2>
- ...

## Examples

### Context: <e.g. formal client>
<verbatim short email>

### Context: <e.g. internal casual>
<verbatim short email>

### Context: <e.g. terse acknowledgment>
<verbatim short email>
```

8. Cap the file at 5 KB. If the rendered content exceeds the cap, trim the example bodies first, then merge similar saliency bullets, until under 5 KB.
9. `Write` the file to `~/.roc/my-hand/tone.md`.
10. Return a one-line confirmation: `Voice profile written to ~/.roc/my-hand/tone.md (corpus: <N> sent emails, <K> bytes).`

## Failure handling

- If the Gmail MCP is unreachable, surface a single English line stating the failure and stop. Do not write a partial `tone.md`.
- If the user has zero sent mail in the last 30 days, surface `No sent mail in the last 30 days; cannot build a voice profile.` and stop.
- If `Write` fails, surface the error and stop. Do not leave a corrupted file.

## Free-form notes

If `$ARGUMENTS` is non-empty, treat it as additional guidance from the user (for example "ignore French replies", "focus on client mail"). Apply it during step 4-7 but do not record it in the file.
