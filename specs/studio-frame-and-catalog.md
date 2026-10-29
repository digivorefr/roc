# Studio frame and catalog

## What

The studio skill's agents need two reference documents that hold for any web interface.
The frame states the rules of web-interface craft in eight families; each rule is a decision to take while creating, how to spot its breach on the rendered screen, and the recognized reference it comes from, so the agents that design and the frame critic read the same text.
The catalog lists ways to solve interface problems, grouped by the problem the user faces: when the prototyper turns the chosen intent into concrete interaction, it names three different ways from it before fixing one, and the critic reads it too.
Claude writes the first draft of both from the references; Pierre amends it for fidelity to them, and his own taste stays in his taste file.
Cost: a claim no public page confirms is left out, so paid books contribute only what their public pages show.

## Where

- The frame (new): a reference document of the studio skill, holding the craft rules in eight families.
- The catalog (new): a reference document of the studio skill, holding ways to solve interface problems, grouped by the user's problem.

Unchanged: the studio skill's mechanics, Pierre's taste file and each product's language (all in the studio spec), the frontend-design skill.

## Decisions

- Both documents are universal: drawn from recognized references of the craft, never from one product or from Pierre's corrections; product specifics live in each product's language, Pierre's taste in his taste file, and taste never moves into the frame.
- Claude writes the first draft from the references and Pierre amends it; critiques he later promotes to rules go to his taste file.
- Pierre's amendments fix fidelity to the references (a misread source, a missing or extra rule, a weak check); a rule he dislikes on taste stays, and his counter-rule goes to his taste file; otherwise the frame turns into his taste one amendment at a time.
- The frame has eight families: perception, reading, writing, interaction, accessibility, adaptation, consistency and motion; the first seven keep the topics Pierre listed.
- The motion family covers what motion is for (feedback, change of state, where things come from and go, drawing the eye; never decoration), duration, easing, choreography (one movement at a time, in reading order) and reduced motion.
- Honouring the device's "reduce motion" setting is a rule even though WCAG ranks it above AA; it is the price of a frame that uses motion freely.
- Each rule appears once, in the family where the creator takes that decision, citing WCAG there when it applies; the accessibility family keeps only what has no other home (keyboard use, focus, text alternatives); otherwise contrast or target size would be written twice and drift apart.
- The frame's accessibility rules, whatever family holds them, cover the WCAG 2.2 AA criteria a design decides (contrast, target size, focus that is visible and never hidden, reflow, text resize and spacing, colour never used alone, an alternative to dragging, consistent navigation and help, labels, error messages); criteria that live only in code (page language, names and roles in markup) stay with whoever builds the page.
- Each rule is a decision to take while creating, then how to spot its breach, then its source; the same text serves the creator and the critic.
- The breach line says what to look at on the rendered screen: a still capture when a still shows it, otherwise the action to perform (tab through, trigger, turn on reduce motion) and what to watch; motion, feedback and keyboard rules cannot be judged from a still, so the frame critic needs to operate the page, not only receive captures.
- Each rule is marked firm (accessibility, and rules whose breach stops a user) or default (a product language or an agent may depart from it by saying why); without the mark, the critic either flags every deliberate departure or treats accessibility as negotiable.
- Short over exhaustive, bounded by structure: a rule enters only if it changes a decision a creator would otherwise leave to habit, a listed reference states it, and its breach can be seen; every rule keeps the one shape given under Reference.
- A rule's title names its decision in a few plain words and is unique in the frame; it is how agents cite the rule and how Pierre contests it, so rules carry no numbers or codes.
- Sources are the references Pierre named — Nielsen's heuristics, WCAG 2.2, the Gestalt principles, the laws of UX, Bringhurst, Butterick, Refactoring UI, the GOV.UK writing guidance, Tidwell's Designing Interfaces, Every Layout — plus, to cover his families: other Nielsen Norman Group articles, the GOV.UK Design System, Wroblewski's Mobile First, Shneiderman's visual information-seeking mantra and, for motion, NN/g's animation articles, MDN's reduced-motion reference, Val Head's Designing Interface Animation, the UX in Motion manifesto and Disney's principles of animation.
- Rules are written in our own words, never copied from the books, which are under copyright while the plugin is distributed; each source line gives a locator Pierre can open without buying a book, and the drafter cites only what it has read, so a claim no public page confirms is dropped.
- Where references disagree, the rule takes the range they share and cites both: line length becomes 45–75 characters (Bringhurst 45–75, Butterick 45–90).
- The frame neither copies nor points to the frontend-design skill's list of AI-generated tells: the list describes what generated pages look like "right now" and is Anthropic's observation, not a craft reference; its sound parts (line length, type scale, visible focus, reduced motion) enter the frame from their own sources.
- The catalog is organised by the problem the user faces, each problem listing at least three ways; that is the shape the prototyper's "name three different ways" step needs.
- Each way states what the user sees and does, when to use it, when to avoid it, and its source; "when to avoid" names a frame rule by its title instead of restating it, so the catalog holds no rules of its own.
- The catalog stays at the level of a screen or a flow, how information is arranged and how the user acts on it; single controls (button, select, toggle) stay out, as each product's component library covers them.
- Both documents are in English.
- Settled: universality, the first draft by Claude amended by Pierre, the families other than motion, the rule's three parts serving creator and critic, the sources Pierre named, short over exhaustive, English.

## Alternatives rejected

- No documents, agents rely on what the model already knows — results stay generic and no rule has a source Pierre can contest.
- Point the agents to the frontend-design skill instead — it targets showcase pages and its list of tells is dated.
- Send the agents to the references online — long pages, no breach checks, a fetch on every run.
- A separate review checklist for the critic — two texts on the same rules drift apart.
- Every WCAG 2.2 AA criterion in the frame — adds rules about code no designer acts on.
- Every rule firm — the critic would flag every deliberate departure.
- Apple's and Material's motion guidelines as sources — their pages could not be read to verify them.
- A catalog organised by component (card, modal, drawer, table) — keeps the very vocabulary it must widen.
- Single controls in the catalog — the product's component library already covers them.

## Done means

- Every frame rule has a unique title, a firm-or-default mark, a decision, a breach line and a source line, and nothing else.
- No decision appears in two rules.
- Opening a rule's source, without buying a book, shows that rule stated there.
- Every breach line names either what a still capture shows, or the action to perform and what to watch.
- Each of the eight families holds rules, and the motion family covers purpose, duration, easing, choreography and reduced motion.
- Every accessibility rule names its WCAG 2.2 criterion number.
- Every catalog problem lists at least three ways, each with what the user sees and does, when to use it, when to avoid it, and a source that names that way.
- No catalog way is a single control.
- No sentence in either document is copied from a source.
- Neither document names MerciYanis, its products, Pierre or a date, and neither says "currently" or "right now".
- Both documents are in English.

## Reference

### Rule shape

| Field | Content | Cap |
|---|---|---|
| Title | The decision in a few plain words; unique in the frame | One line |
| Mark | `firm` or `default` | One word |
| Decision | What to do while creating, including when it does not apply | One or two sentences |
| Breach | What a still capture shows, or the action to perform and what to watch | One sentence |
| Source | Reference and locator | One line |

Accepted example (shape approved, content illustrative):

> **Keep body text between 45 and 75 characters per line** · default
> Decision: set the width of running text so a line holds 45 to 75 characters, spaces included; wider screens add margin, not longer lines.
> Breach: on a wide capture, paragraph lines run past about 75 characters.
> Source: Bringhurst, *The Elements of Typographic Style*, 2.1.2 (webtypography.net/2.1.2); Butterick, *Practical Typography*, "Line length".

### Frame families

| Family | Its rules decide | Drawn mainly from |
|---|---|---|
| Perception | Grouping by proximity and alignment; contrast and size that set the hierarchy | Gestalt principles, Refactoring UI |
| Reading | The eye's path, type scale and rhythm, line length, density | Bringhurst, Butterick, Refactoring UI |
| Writing | Plain words, labels that say the action, one word per thing, the empty, loading, error and success states | GOV.UK writing guidance and Design System, Nielsen's heuristics |
| Interaction | Immediate feedback, visible affordance, target size, number of choices, undo rather than confirm, progressive disclosure | Nielsen's heuristics, NN/g articles, laws of UX (Fitts, Hick, Doherty), WCAG |
| Accessibility | WCAG 2.2 AA criteria a design decides that have no other home: keyboard use, focus, text alternatives | WCAG 2.2 |
| Adaptation | Content first, mobile first, layout that adapts to its content rather than to fixed screen widths | Wroblewski, Every Layout, WCAG |
| Consistency | Same thing, same look, same place; the habits users bring from elsewhere | Nielsen's heuristics, Jakob's law, WCAG |
| Motion | Purpose, duration, easing, choreography, reduced motion | NN/g animation articles, Val Head, UX in Motion manifesto, Disney's principles, MDN, WCAG |

### Sources and their locators

| Reference | Locator Pierre can open |
|---|---|
| Nielsen, 10 usability heuristics | Heuristic number; nngroup.com/articles/ten-usability-heuristics |
| Nielsen Norman Group articles | Article address: response time limits, progressive disclosure, confirmation dialogs, the role of animation, animation duration |
| WCAG 2.2 | Success criterion number; w3.org/TR/WCAG22 |
| Gestalt principles | Their pages on lawsofux.com: proximity, similarity, common region, uniform connectedness, Prägnanz |
| Laws of UX | Law name; lawsofux.com |
| Bringhurst, *The Elements of Typographic Style* | Section number, read through its public web adaptation, webtypography.net |
| Butterick, *Practical Typography* | Page title; practicaltypography.com |
| Wathan and Schoger, *Refactoring UI* | Section title from the public table of contents, refactoringui.com/book |
| GOV.UK writing guidance | "Writing to GOV.UK standards", guidance.publishing.service.gov.uk |
| GOV.UK Design System | Pattern or component name; design-system.service.gov.uk |
| Tidwell, Brewer and Valencia, *Designing Interfaces* | Pattern name, as confirmed on a public page (the publisher's table of contents refuses automated reading) |
| Pickering and Bell, *Every Layout* | Its free pages on every-layout.dev |
| Wroblewski, *Mobile First* | The free edition on lukew.com |
| Shneiderman, "The Eyes Have It" | The public paper: overview first, zoom and filter, then details on demand |
| MDN, `prefers-reduced-motion` | developer.mozilla.org |
| Head, *Designing Interface Animation* | Public excerpts and the publisher's page |
| Willenskomer, "Creating Usability with Motion: The UX in Motion Manifesto" | uxmag.com |
| Thomas and Johnston, Disney's twelve principles of animation | Public summaries of the principles |

### Catalog way shape

| Field | Content | Cap |
|---|---|---|
| Name | The way in plain words | One line |
| What the user sees and does | The arrangement and the action, including on a narrow screen | One or two sentences |
| Use when | The situations it serves | One sentence |
| Avoid when | The situations it fails, naming a frame rule by its title when one applies | One sentence |
| Source | A reference that names this way | One line |

Accepted example (shape approved, content illustrative):

> **List and detail side by side** — under "Browse a collection and work on one item"
> What the user sees and does: the list stays on one side and the selected item opens beside it; on a narrow screen the detail replaces the list.
> Use when: people move from item to item and compare as they go.
> Avoid when: the detail needs the full width, or items are opened rarely.
> Source: Tidwell, *Designing Interfaces*, "Two-Panel Selector or Split View".

### Catalog problems

The ways listed are starting points, held to the same sourcing rule as every entry.

| Problem the user faces | Ways to start from |
|---|---|
| Browse a collection and work on one item | List and detail side by side, drill down within one window, expand the item in place in the list |
| Find something in a large set | Search first, filter by facets, browse by category, overview first then zoom |
| Edit | Edit in place, a page of its own for the form, direct manipulation with an alternative to dragging |
| Complete a long task | Step by step, one question per page, a task list, check answers before sending |
| Show more without overwhelming | Progressive disclosure, details on demand, one main area at the centre of the screen |
| Nothing to show yet | An empty state that invites the first action, sample content, a guided first step |
| Act on something risky | Undo after the fact, check before sending, a confirmation kept for the irreversible |
| Wait | Show the result at once and finish quietly, progress with how much is done, work in the background and say when it is done |
| Move between areas | Persistent navigation, step-by-step navigation, breadcrumbs, a hub with spokes |
| Compare | Side by side, one table with the items as columns, the differences highlighted over one item |
| Create | Create in place where the item will live, start from a template, duplicate an existing item |
