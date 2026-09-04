---
name: condense
description: Condense a text, document, file, or conversation element into its essence without losing information. Use this skill whenever the user invokes "/rocket:condense", asks to synthesize, summarize, shorten, condense, or digest something, says "make it shorter", "shorter", "shorten this", "too long", "TL;DR", "too verbose", "synthétise", "résume", "fais plus court", "plus court", "raccourcis", "trop long", "trop verbeux", "plus digeste", "plus concis", or any similar request to reduce content while keeping its substance. The input may be a file path, a named element of the conversation (a previous answer, a spec, a report), several of them, or nothing (the last substantial output).
---

# Condense

Distil a verbose text into what a human needs to read: the essence first, then every fact, decision, constraint and causal link, in bullets, in the language of the source. Compression comes from removing redundancy and inference, never from dropping information — a condensed text that loses a condition, a number or a "because" has failed.

## Output contract

The output has exactly this shape, in this order, with nothing before or after it:

1. **Essence** — two to four lines of prose, no label, no heading: the output starts directly with them. What the text is about, why it matters, what results from it. Readable alone; a reader who stops here knows the point.
2. **Body** — one section per isolated concept, each a flat list of bullets (two levels at most). Headings only when there are at least three concepts; otherwise bullets under the essence.
   - One idea per bullet, stated as a fact or a rule, never a paraphrase of a heading.
   - A causal link is written out: `X because Y`, `X, so Y`, `X; otherwise Y`. Two facts the source links are never left as two unlinked bullets.
   - Numbers, identifiers, names, commands, thresholds and exceptions are kept verbatim.
   - A concept that appears in several places of the source appears once here, merged.
3. **Loss check** — set apart from the content: a horizontal rule, then one blockquote line `> Loss check: <n> items in the source, all kept`, optionally followed by the merges in parentheses. An item merged into another bullet is kept; only an item whose information appears nowhere in the output is lost, and a lost item is never delivered (see pass 5). The reader must see at a glance where the condensed text ends and its verification begins. Omitted when the user asked for no loss check (`/rocket:condense --no-check`, "sans le loss check", "without the check"); the check itself still runs.

The output is in the language of the source (French source, French output). Length follows the source's information content, not a ratio: a text with forty distinct facts yields forty bullets, a text with three yields three.

## Workflow

Five passes, each on the result of the previous one. Skipping a pass produces a hasty shortening: the essence is guessed instead of derived, and losses go unnoticed.

1. **Resolve the input.** The argument names a file (or several), a conversation element ("your last answer", "the spec above", "the review report"), or nothing — then the last substantial assistant output. Several inputs are condensed as one text. Ambiguous reference → one question, then proceed. Note whether the user asked to omit the loss-check block.
2. **Inventory.** Read the whole input and list every atomic item: fact, rule, decision, constraint, exception, number, named thing, causal link. This ledger is the reference for the loss check; write it before any rewriting.
3. **Structure.** Group the ledger by concept, not by the source's headings — the source's structure is often the reason it is long (a rule stated in the introduction, again in a step, again in a "never" list). Order groups from the general to the particular. Within each group, chain cause → effect → consequence explicitly.
4. **Compress.** Rewrite each group as bullets: one item per bullet, redundancies merged, examples reduced to the one that carries the rule, persona and filler removed, every "why" kept as a clause. A definition the source gives is kept ("thin client: a wrapper around HTTP calls with retry config"), not replaced by its label.
5. **Essence, then loss check.** Derive the essence from the compressed body, never from memory of the source. Then walk the ledger item by item: each is present or merged into a named bullet (both count as kept). An item that is neither is a lost notion, and a lost notion invalidates the draft: redo passes 3 to 5 from the ledger, never patch the missing bullet into the existing text — a draft that lost one notion has a structure that could not hold it. Deliver only a draft whose loss check reads "all kept"; write the loss-check line last, or keep it internal when the user asked to omit it.

Delivery: in the conversation. Write to a file only when asked; never overwrite the source unless asked.

## Good example

Source (French, 6 sentences):

> Le déploiement se fait via la CI. Il est important de noter que le déploiement ne se déclenche que sur la branche main. Par ailleurs, si les tests échouent, le déploiement est annulé automatiquement, ce qui garantit qu'aucune version cassée n'atteint la production. Il convient également de rappeler que les variables d'environnement sont lues depuis le vault. En résumé, la CI déploie main quand les tests passent. Le rollback prend environ 2 minutes.

Output (rendered markdown):

```markdown
La CI déploie automatiquement la branche `main` en production, uniquement si les tests passent ; le rollback prend environ 2 minutes.

- Le déploiement ne se déclenche que sur `main`.
- Un échec des tests annule le déploiement, donc aucune version cassée n'atteint la production.
- Les variables d'environnement sont lues depuis le vault.
- Rollback : environ 2 minutes.

---

> Loss check: 6 items in the source, all kept (the closing "En résumé" sentence merges into the first three bullets).
```

## Bad example

> Deployment runs through CI on main when tests pass. Env vars come from the vault.

Four failures: no essence lines distinct from the body, the causal consequence ("no broken version reaches production") and the 2-minute rollback are gone, the output changed language, and no loss check was run — the losses went unnoticed and the text was delivered anyway.
