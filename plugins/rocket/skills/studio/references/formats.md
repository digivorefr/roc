# Studio — file shapes

Every file studio writes follows its shape here: headings, field names and order are fixed. Content is in English, except lexicon words and a piece's copy (the product's copy language) and the operator's remarks (verbatim). Dates are `YYYY-MM-DD`.

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
### <medium>
- Stroke: <…>
- Spacing rhythm: <…>
- Typography: <…>
- Color roles: <…>

## Motion
### <medium>
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

- One lexicon, one intent sentence and one do/avoid serve every medium. Signature and motion are written per medium, one `### <medium>` block each, because stroke and timing do not transfer from a screen to a printed page; a block is added the first time a piece is validated in that medium, from the values that piece uses. In the web medium the fields are the ones above; another medium keeps those that apply and adds its own, and its Motion block reads `none` when its pieces do not move.
- A language written before media existed carries signature and motion with no medium heading: they are the web medium's, and the `### web` heading is added the next time the language is written.
- With a design system, signature and motion name its tokens and components by their names and never restate or alter a color, spacing value or component it defines; each conflict goes under Design system gaps. Without one, they hold the values the validated prototype uses.
- A do/avoid line replaced by a newer remark is rewritten in place with the new date; the history stays in the corpus.
- A refuted hypothesis stays under avoid for good.

## Proposal — `design/proposals/<slug>.md`

```markdown
# <Piece> proposal

Language: design/language.md | none · <date>
Medium: <medium>

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
Deliverable: design/proposals/<slug>/<file> · <file type> · made with <tool>
Raw materials: design/materials/<file> · identity | accessory
```

Measurable outcomes hold only what passes or fails without judging looks: a state exists and what it shows, an action triggers a transition, a keyboard path, AA contrast. Every aesthetic choice is a settled decision.

- `Medium:` is omitted in the web medium, as are `Deliverable:` and `Raw materials:` when the run made none; a web proposal without raw materials keeps the shape it had.
- Outside the web medium the piece is its own deliverable: `Deliverable:` lists one line per file, copied to `design/proposals/<slug>/`, and replaces `Prototype:`. States, Transitions, Keyboard path and Contrast keep only the rows the medium's rules give a meaning to; an empty section reads `none`.
- `Language: none` marks a piece made for a product without a language.

## Critique corpus — `~/.roc/rocket/studio/`

`remarks/<piece type>.md`, one entry per remark, newest last:

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
- <rule> · <date> · from: <date> <project> (<piece type>); <date> <project> (<piece type>) · replaces: <older rule> | none
```

`types.md`, the closed list, extended only on the operator's go:

```markdown
## Piece types
- <piece type> · <medium>

## Aspects
- <aspect> · <medium>
```

- A piece type and an aspect belong to one medium; a remark matches past remarks of its own piece type only, so of its own medium only.
- A list written before media existed has a `## Screen types` heading and entries with no medium: every one of them reads as `· web`, and each `remarks/<screen type>.md` stays where it is, under the same name. The file takes the shape above the next time the operator confirms a new entry.
- A medium sheet's own list is where a medium's types and aspects start: they enter `types.md` on the go that validates the sheet.

`captures/<date>-<project>-<slug>-<n>.<ext>` — the capture shown when the remark was made.

## Medium sheet — `~/.roc/rocket/studio/media/<medium>.md`

One per medium, named after it in kebab-case. The web sheet ships with the skill as `references/web.md`; every other one is drafted on first contact and kept here.

```markdown
# <Medium> — medium sheet

## Medium
<medium> · draft | amended · <date>

## Rules
**<Title naming the decision>** · firm | default
Decision: <the decision to take while creating>
Breach: <how a violation shows on the rendered piece: what to look at, listen to or measure>
Source: <reference, with a locator the operator can open>

## Material
- Key image: <what it is built from>
- Piece: <what it is built from>
- Fallback: <what replaces a tool that is missing or fails>

## Show
- Key image: <how the operator sees or hears it>
- Piece: <how the operator sees or hears it>

## Judge
- Instrument: <what an agent measures or captures> · needs: <need>
- Stays with the operator: <what no instrument covers>

## Deliverable
- <file type> · <what it holds>

## Raw materials
- <usual raw material> · identity | accessory

## Piece types and aspects
- Type: <piece type>
- Aspect: <aspect>
```

- A rule's title is unique in the sheet; it is how workers cite the rule and how the operator amends it.
- `draft`: studio wrote the sheet and the operator changed nothing. Every rule reads `default`, and a worker treats every rule of a draft as a default whatever its mark.
- `amended`: the operator changed at least one line. Only a rule the operator amended or marked reads `firm`; the date is the last amendment's.
- A sheet that lists a second document of ways, as the web sheet lists its catalog, names it under Rules.

## Bench — `~/.roc/rocket/studio/bench/`

```
bench/
  <tool>.md      the tool sheet
  <tool>/        what studio installed for that tool; kind `installed` only
```

Nothing studio installs lives anywhere else: never globally, never in a project.

`<tool>.md`, one per tool, named after it in kebab-case:

```markdown
# <Tool> — tool sheet

- Need: <what it is used for, in plain words>
- Kind: installed | session | application
- Call: <the command, or the tool names in the session>
- Check: <how to tell it works>
- Concurrency: parallel | exclusive
- Limits: <what it cannot do; where it may read and write>
- Proven: <date> · <deliverable of the last successful probe> | none

## Pitfalls
- <date> · <what went wrong> · <way around it>
```

- `installed`: studio installed it under `bench/<tool>/`. `session`: a connector or built-in tooling, found among the session's tools and named in `Call` by those tools' names. `application`: the operator starts it; studio asks and waits.
- `Proven: none` until a probe ends on a real deliverable with the tool; a later probe replaces the line.
- A tool that keeps its own memory (a script library, recorded hints) gets one pitfall line `kept by the tool · <how to read it>` instead of a copy.

## Preview recipe — `<main checkout>/.roc/rocket/studio/preview.md`

```markdown
- Design system: <where it lives> | none
- Screen: <address or command; for kind tool, also the command that serves it>
- Story: <how to show one component in isolation> | none
- Kind: tool | environment | self-contained
- Check: <how to tell the preview is up>
- Discovered: <date> · from: <files>
```

## Restatement lines

Fixed wording, so the operator reads the same line from one run to the next:

```
Medium: <medium> · sheet: shipped | <draft | amended> <date> | none yet, drafted before anything is designed
deliverable: <what file or files> made with <tool>
Tool: <tool> for <need> · <installs under ~/.roc/rocket/studio/bench/<tool>/ | nothing installed: <session tooling | you start it>> · check: <how>
raw material: <name> · <identity | accessory> · <this product | this run only> · made with <tool>
judged by you alone: <what no instrument covered>
```

- `deliverable:` names the file type and the tool. A tool not on the bench yet reads `made with <kind of tool>, none on the bench yet`, and the line is restated complete with the `Tool:` line.
- `Tool:` is one line per tool; refusing it installs nothing.

## Raw materials

| What | Where | Committed |
|---|---|---|
| Raw materials of a run | `<checkout>/.roc/rocket/studio/materials/<slug>/` | No; removed with the run |
| Validated raw materials of the product | `design/materials/<name>.<ext>` | Yes |

## Run state — `<checkout>/.roc/rocket/studio/run.json`

```json
{
  "entry": "found-scratch | found-existing | decline | make | critique | fidelity",
  "subject": "<product or piece>",
  "slug": "<kebab-case>",
  "medium": "<medium>",
  "sheet": "<absolute path of the medium sheet>",
  "checkpoint": "brief | sheet | bench | words | language | material | intents | prototype | variant | findings | side-by-side",
  "screen_type": "<piece type, or null>",
  "copy_language": "<language of the piece's copy>",
  "brief": "<the validated brief>",
  "deliverable": "<the validated deliverable line>",
  "tools": [{ "name": "<tool>", "need": "<need>", "probed": true }],
  "materials": [
    {
      "name": "<raw material>",
      "carries_identity": true,
      "product": true,
      "status": "to make | made | validated",
      "made_with": "<tool | HTML | SVG | script>",
      "files": ["materials/<slug>/<file>"]
    }
  ],
  "tasks": ["<task in plain words>"],
  "chosen_intent": "<note, or the operator's mix, or null>",
  "returns": ["returns/<worker>-<n>.md"],
  "files": ["<every prototype, key-image, probe and study-page file this run created>"]
}
```

- `screen_type` keeps its key and holds the piece type, whatever the medium.
- `materials`: one entry per raw material the piece uses. `carries_identity` gives it its own checkpoint; `product` says it belongs to the product and is copied to `design/materials/` when the run is validated. `files` are relative to the checkout's `.roc/rocket/studio/`; a raw material that existed before the run is listed with its own path, `status: validated`, and is never deleted.
- `tools`: the bench tools this run uses; `probed` turns true when this run's probe ended on a real deliverable with the tool.

`checkpoint` is the last one validated. A resume re-shows it from `returns/` without running a worker again. The file is deleted when the run ends.
