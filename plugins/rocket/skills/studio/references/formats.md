# Studio — file shapes

Every file studio writes follows its shape here: headings, field names and order are fixed. Content is in English, except lexicon words and interface copy (the product's copy language) and the operator's remarks (verbatim). Dates are `YYYY-MM-DD`.

## Product language — `design/language.md`

```markdown
# <Product> language

## Intent
<one sentence>

## Lexicon
| Word | What it designates | Relations | Actions | Events |
|---|---|---|---|---|

Renames: <current word> → <word> · <date> (one line each, or none)

## Visual signature
- Stroke: <…>
- Spacing rhythm: <…>
- Typography: <…>
- Color roles: <…>

## Motion
- What moves: <…>
- How: <…>
- Duration: <…>
- Easing: <…>
- When nothing moves: <…>

## References
- <reference> · <what it brings> · given | validated · <date>

## Do / avoid
- Do · <rule> · <date> · from: remark | hypothesis "<hypothesis>"
- Avoid · <rule> · <date> · from: remark | refuted hypothesis "<hypothesis>"

## Departures from default frame rules
- "<frame rule title>" · <reason>

## Design system gaps
- <conflict> · <what the language wanted> · for the designer
```

- With a design system, signature and motion name its tokens and components by their names and never restate or alter a color, spacing value or component it defines; each conflict goes under Design system gaps. Without one, they hold the values the validated prototype uses.
- A do/avoid line replaced by a newer remark is rewritten in place with the new date; the history stays in the corpus.
- A refuted hypothesis stays under avoid for good.

## Proposal — `design/proposals/<slug>.md`

```markdown
# <Screen or flow> proposal

Language: design/language.md · <date>

## Settled decisions
- <decision, one line>

### Lexicon additions
| Word | What it designates | Actions | Events |
|---|---|---|---|

Renames: <current word> → <word> · reaches beyond this screen (or none)

### Hypotheses
- Validated · <hypothesis>
- Refuted · <hypothesis>

### Accessibility
- <point>

### Design system gaps
- <conflict> · for the designer

## Measurable outcomes

### States
| State | What it shows |
|---|---|
| Empty | <…> |
| Loading | <…> |
| Error | <…> |
| Success | <…> |

### Transitions
| Trigger | What moves | Duration | Easing |
|---|---|---|---|

### Keyboard path
1. <key> → <where focus goes, what happens>

### Contrast
- Text and controls meet WCAG AA contrast.

## Evidence
| State | Capture |
|---|---|
| <state> | design/captures/<slug>/<state>.png, or missing |

Prototype: <how to open it> · files: <every file, repository-relative or absolute> · removed after the fidelity comparison
```

Measurable outcomes hold only what passes or fails without judging looks: a state exists and what it shows, an action triggers a transition, a keyboard path, AA contrast. Every aesthetic choice is a settled decision.

## Critique corpus — `~/.roc/rocket/studio/`

`remarks/<screen type>.md`, one entry per remark, newest last:

```markdown
## <date> · <project> · <aspect> · active | superseded by <date> | promoted to "<taste rule>"
- Capture: captures/<file> | missing
- Zone: <zone>
- Remark: "<verbatim, in the operator's words>"
- Rule: <one English line>
- Level: this product | everywhere
- Replaces: <older rule> | none
```

`taste.md`, active taste rules only:

```markdown
- <rule> · <date> · from: <date> <project> (<screen type>); <date> <project> (<screen type>) · replaces: <older rule> | none
```

`types.md`, the closed list, extended only on the operator's go:

```markdown
## Screen types
- <screen type>

## Aspects
- <aspect>
```

`captures/<date>-<project>-<slug>-<n>.<ext>` — the capture shown when the remark was made.

## Preview recipe — `<main checkout>/.roc/rocket/studio/preview.md`

```markdown
- Design system: <where it lives> | none
- Screen: <address or command; for kind tool, also the command that serves it>
- Story: <how to show one component in isolation> | none
- Kind: tool | environment | self-contained
- Check: <how to tell the preview is up>
- Discovered: <date> · from: <files>
```

## Run state — `<checkout>/.roc/rocket/studio/run.json`

```json
{
  "entry": "found-scratch | found-existing | decline | critique | fidelity",
  "subject": "<product or screen>",
  "slug": "<kebab-case>",
  "checkpoint": "brief | words | language | intents | prototype | variant | findings | side-by-side",
  "screen_type": "<screen type, or null>",
  "copy_language": "<language of the interface copy>",
  "brief": "<the validated brief>",
  "tasks": ["<task in plain words>"],
  "chosen_intent": "<note, or the operator's mix, or null>",
  "returns": ["returns/<worker>-<n>.md"],
  "files": ["<every prototype and key-image file this run created>"]
}
```

`checkpoint` is the last one validated. A resume re-shows it from `returns/` without running a worker again. The file is deleted when the run ends.
