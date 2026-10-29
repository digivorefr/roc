# Frame

The rules of web-interface craft, in eight families. Each rule gives the decision to take while creating, how its breach shows on the rendered screen, and the reference it comes from. `firm` marks accessibility and rules whose breach stops a user; `default` marks rules a product may depart from with a stated reason.

## Perception

**Group with space before lines and boxes** · default
Decision: keep the gap inside a group clearly smaller than the gap between groups, so a label sits nearer its field than the field above and a heading nearer its content than the section before; add a border or a shared background only where space alone cannot show the grouping.
Breach: on a capture, a heading or label sits as close to the block before it as to the block it names, or borders and boxes frame items that spacing already separates.
Source: Laws of UX, "Law of Proximity" and "Law of Common Region" (lawsofux.com); NN/g, "Visual Hierarchy in UX: Definition" (nngroup.com/articles/visual-hierarchy-ux-definition); Wathan and Schoger, *Refactoring UI*, "Avoid ambiguous spacing" (refactoringui.com/book).

**Make the most important element stand out first** · default
Decision: rank what the screen shows and give the top rank the strongest contrast, and the largest size only when contrast is not enough, with no more than two large elements; push lower ranks down with muted colour and lighter weight instead of raising everything.
Breach: blur or squint at a capture: the first thing that stands out is not the screen's main content or action, or several elements pull equally.
Source: NN/g, "Visual Hierarchy in UX: Definition" (nngroup.com/articles/visual-hierarchy-ux-definition); *Refactoring UI*, "Size isn't everything" and "De-emphasize to emphasize" (refactoringui.com/book); Laws of UX, "Von Restorff Effect".

**Never carry meaning by colour alone** · firm
Decision: wherever colour marks a status, a category, an error, a selection or a link, add a second cue such as text, an icon, a shape or an underline; colour that only decorates needs none.
Breach: view a capture in greyscale: a status, an error, a selection or a link can no longer be told apart.
Source: WCAG 2.2, SC 1.4.1 Use of Color (w3.org/TR/WCAG22); *Refactoring UI*, "Don't rely on color alone" (refactoringui.com/book).

**Give text a contrast of at least 4.5 to 1** · firm
Decision: every piece of text, secondary and hint text included, reaches 4.5:1 against its background, and large text reaches 3:1.
Breach: on a capture, sample the palest text and its background: body text measures under 4.5:1, or large text under 3:1.
Source: WCAG 2.2, SC 1.4.3 Contrast (Minimum) (w3.org/TR/WCAG22).

**Give controls and meaningful graphics a contrast of 3 to 1** · firm
Decision: the edge or fill that makes a control visible (a field outline, a checkbox, a toggle) and the parts of icons and charts needed to understand them reach 3:1 against the colours next to them.
Breach: on a capture, a field outline, a meaningful icon or a chart line measures under 3:1 against its neighbouring colour.
Source: WCAG 2.2, SC 1.4.11 Non-text Contrast (w3.org/TR/WCAG22).

## Reading

**Keep body text between 45 and 75 characters per line** · default
Decision: set the width of running text so a line holds 45 to 75 characters, spaces included; wider screens add margin, not longer lines.
Breach: on a wide capture, paragraph lines run past about 75 characters.
Source: Bringhurst, *The Elements of Typographic Style*, 2.1.2 (webtypography.net/2.1.2); Butterick, *Practical Typography*, "Line length" (practicaltypography.com/line-length.html).

**Set body line spacing between 1.3 and 1.45** · default
Decision: give running text a line spacing of 1.3 to 1.45 times its size, set as a unitless multiple so it follows the size, nearer the top of the range for longer lines; headings and short labels may go tighter as long as letters of adjacent lines never touch.
Breach: on a capture of a paragraph, the distance from one baseline to the next is under 1.3 or over 1.45 times the text size, or the lines of a heading collide.
Source: Butterick, *Practical Typography*, "Line spacing" (practicaltypography.com/line-spacing.html); Bringhurst, *The Elements of Typographic Style*, 2.2.1 (webtypography.net/2.2.1).

**Draw text sizes from one short scale** · default
Decision: choose a few related sizes before laying out, about three per screen for body, subheading and heading, and use nothing in between; raise a heading by the smallest step that still shows, and keep to two or three heading levels.
Breach: on a capture, one screen shows more than three text sizes, sizes that differ by a hair, or a heading about twice the body size where weight or space would do.
Source: Bringhurst, *The Elements of Typographic Style*, 3.1.1 (webtypography.net/3.1.1); Butterick, *Practical Typography*, "Headings" (practicaltypography.com/headings.html); NN/g, "Visual Hierarchy in UX: Definition".

**Set body text between 15 and 25 pixels** · default
Decision: set running text between 15 and 25 CSS pixels, placing it within that range by how large the typeface looks at a given size.
Breach: on a capture at 100 % zoom, paragraph text is smaller than 15 pixels.
Source: Butterick, *Practical Typography*, "Point size" (practicaltypography.com/point-size.html).

**Take every space from one scale** · default
Decision: derive a short set of spacing values from the body line height and take every gap, padding and margin from it, so vertical space changes in measured steps.
Breach: on a capture, gaps that play the same role measure slightly differently from one place to another instead of repeating a few values.
Source: Bringhurst, *The Elements of Typographic Style*, 2.2.2 (webtypography.net/2.2.2); *Refactoring UI*, "Establish a spacing and sizing system" (refactoringui.com/book); Pickering and Bell, *Every Layout*, "The Stack" (every-layout.dev/layouts/stack).

**Align running text to its start edge** · default
Decision: align paragraphs to the start edge of the reading direction with a ragged end, centre only a line or two such as a title or a short notice, and leave text unjustified.
Breach: on a capture, a paragraph of three lines or more is centred, or justified with uneven gaps between words.
Source: Bringhurst, *The Elements of Typographic Style*, 2.1.3 (webtypography.net/2.1.3); Butterick, *Practical Typography*, "Summary of key rules" (practicaltypography.com/summary-of-key-rules.html).

**Keep capitals to short labels, and space them** · default
Decision: set text in capitals only when it fits on one line, such as a label or a small heading, and add 5 to 10 % of the type size as letter spacing.
Breach: on a capture, a sentence or a paragraph is set in capitals, or a label in capitals keeps normal letter spacing.
Source: Butterick, *Practical Typography*, "Letterspacing" and "All caps" (practicaltypography.com/letterspacing.html); Bringhurst, *The Elements of Typographic Style*, 2.1.6 (webtypography.net/2.1.6).

**Break long text with headings and lists** · default
Decision: give text that runs past a few paragraphs descriptive headings, keep paragraphs to five sentences, and turn series and steps into lists, so a reader skimming down the start edge finds their way; interface labels and short messages need none of this.
Breach: on a capture, more than five sentences or a series of items run on with no heading or list to land on.
Source: GOV.UK, Writing to GOV.UK standards, "Create a clear structure for your content" and "Use clear language" (guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines).

**Remove what the task does not need** · default
Decision: keep on the screen only what serves one of its tasks, because every unrelated element competes with the ones that matter.
Breach: on a capture, name the task each element serves: some serve none.
Source: Nielsen, usability heuristic 8 "Aesthetic and minimalist design" (nngroup.com/articles/ten-usability-heuristics).

## Writing

**Write in the user's everyday words** · default
Decision: use the words people use for the subject, short everyday words over formal ones, the active voice and sentences under 25 words; a specialist term the audience needs is explained the first time it appears.
Breach: on a capture, a sentence runs past 25 words, or a label or message uses internal terms, codes or system names the user would not say.
Source: GOV.UK, Writing to GOV.UK standards, "Use clear language" (guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language); Nielsen, usability heuristic 2 "Match between the system and the real world".

**Put the key words first** · default
Decision: open headings, labels, links, messages and paragraphs with the words that carry their meaning, the most important information first and the detail after.
Breach: on a capture, a heading, a link or a message opens with filler before the words that say what it is about.
Source: GOV.UK, Writing to GOV.UK standards, "Create a clear structure for your content" and "Write effective links" (guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines).

**Label each action with what it does** · default
Decision: a button names its outcome with a verb and, when needed, its object (such as "Archive project"), and a link says where it leads or, for a task, starts with the verb.
Breach: on a capture, an action reads only "OK", "Yes", "Submit" or "Click here", or a link says nothing of where it goes.
Source: GOV.UK Design System, "Button" (design-system.service.gov.uk/components/button); NN/g, "Confirmation Dialogs Can Prevent User Errors (If Not Overused)" (nngroup.com/articles/confirmation-dialog); GOV.UK, "Write effective links".

**Give every input a visible label** · firm
Decision: each field, choice and group of choices carries visible text saying what it asks for, with any format it expects and "(optional)" on the ones that are; a heading or label describes the purpose of what it heads.
Breach: on a capture, a field or a group of choices has no visible text saying what to enter, or a label or heading does not describe its purpose.
Source: WCAG 2.2, SC 3.3.2 Labels or Instructions and SC 2.4.6 Headings and Labels (w3.org/TR/WCAG22); GOV.UK Design System, "Question pages" (design-system.service.gov.uk/patterns/question-pages).

**Use one word per thing** · firm
Decision: one thing keeps one name on every screen, one name never stands for two things, and links with the same text lead to the same place.
Breach: walk through the screens: an object or action appears under two names, or one label leads to two different places.
Source: WCAG 2.2, SC 3.2.4 Consistent Identification (w3.org/TR/WCAG22); Nielsen, usability heuristic 4 "Consistency and standards"; GOV.UK, "Write effective links".

**Say what went wrong and how to fix it** · firm
Decision: an error names the field or item at fault, in text next to it, and says in plain words what is wrong and how to put it right, without blame or codes; when a form holds several errors, a summary at the top links to each, worded as the message by the field.
Breach: submit a form empty, then with a wrong value: a message is missing, far from its field, generic, or worded differently in the summary and by the field.
Source: WCAG 2.2, SC 3.3.1 Error Identification and SC 3.3.3 Error Suggestion (w3.org/TR/WCAG22); GOV.UK Design System, "Error message" and "Recover from validation errors" (design-system.service.gov.uk); Nielsen, usability heuristic 9.

**Validate on submit and keep what was typed** · default
Decision: check a field when the user submits or continues, not while they type or as they leave it, except where live feedback helps such as a character count; on error, show the page again with everything they entered.
Breach: type a wrong value and move to the next field: an error appears before submitting; or submit with one error: other fields come back empty.
Source: GOV.UK Design System, "Recover from validation errors" (design-system.service.gov.uk/patterns/validation).

**Design the empty, loading, error and success states** · firm
Decision: every area that shows data has a state for nothing yet that says so and offers the first action, a loading state that never reports "nothing" before the data has arrived, a failure state that says what failed and what to do, and a success state that confirms what happened and what comes next.
Breach: reach each state (no data yet, a slow load, a failed load, a finished task): an area is blank, shows "no results" while still loading, or a finished task gives no confirmation.
Source: NN/g, "Designing Empty States in Complex Applications: 3 Guidelines" (nngroup.com/articles/empty-state-interface-design); GOV.UK Design System, "Confirmation pages" (design-system.service.gov.uk/patterns/confirmation-pages); Nielsen, usability heuristic 1 "Visibility of system status".

## Interaction

**Answer every action at once** · firm
Decision: each click, tap or key press changes something visible within about a tenth of a second, the result itself or a sign that the action was received, so nobody repeats it wondering whether it worked.
Breach: trigger each action, also on a throttled connection: for a noticeable moment nothing on screen changes.
Source: NN/g, response time limits (nngroup.com/articles/response-times-3-important-limits); Nielsen, usability heuristic 1 "Visibility of system status"; Laws of UX, "Doherty Threshold" (lawsofux.com/doherty-threshold).

**Show progress on any wait over a second** · default
Decision: under a second, show only the result; from about one to ten seconds, a busy indicator where the content will appear, or the page's skeleton for a full-page load; past ten seconds, how much is done or how long is left, and a way to stop.
Breach: throttle the connection and trigger slow actions: a wait of several seconds shows nothing, a long wait shows only a spinner, or a quick one flashes an indicator.
Source: NN/g, "Progress Indicators Make a Slow System Less Insufferable" (nngroup.com/articles/progress-indicators); NN/g, "Skeleton Screens 101" (nngroup.com/articles/skeleton-screens); NN/g, response time limits (nngroup.com/articles/response-times-3-important-limits).

**Make what can be acted on look actionable** · firm
Decision: links and controls look different from static content, and every action a task needs is in view without hovering or a hidden gesture.
Breach: on a capture, a link or a button cannot be told from plain text; on a touch screen, an action appears only on mouse hover or after a gesture nothing signals.
Source: Laws of UX, "Law of Similarity" (lawsofux.com/law-of-similarity); Nielsen, usability heuristic 6 "Recognition rather than recall"; NN/g, "Basic Patterns for Mobile Navigation: A Primer" (nngroup.com/articles/mobile-navigation-patterns).

**Let content shown on hover stay, close and be hovered** · firm
Decision: a tip, popover or menu that appears on hover or focus can be dismissed without moving the pointer or focus, stays while the pointer moves onto it, and stays until the user dismisses it or leaves.
Breach: hover a trigger and move the pointer onto what appears: it vanishes; or it covers content and cannot be closed without moving away.
Source: WCAG 2.2, SC 1.4.13 Content on Hover or Focus (w3.org/TR/WCAG22).

**Make targets at least 24 by 24 pixels** · firm
Decision: every pointer target measures at least 24 by 24 CSS pixels, or is spaced so a 24-pixel circle centred on it overlaps no other target; links inside a sentence are exempt; frequent and primary targets go larger, and sit near where the hand or pointer already is.
Breach: on a capture with measurements, an icon button, a close control or a row action is under 24 pixels with a neighbour closer than that.
Source: WCAG 2.2, SC 2.5.8 Target Size (Minimum) (w3.org/TR/WCAG22); Laws of UX, "Fitts's Law" (lawsofux.com/fittss-law).

**Offer few choices and one primary action** · default
Decision: at each point of decision show only the options that point needs, flag the recommended one, and give each view a single primary action with the others visibly secondary.
Breach: on a capture, two or more actions share the primary look, or a menu offers options most people never need at that point.
Source: Laws of UX, "Hick's Law" (lawsofux.com/hicks-law); GOV.UK Design System, "Button" (design-system.service.gov.uk/components/button).

**Prefer undo to confirmation** · firm
Decision: make deleting, sending and other committing actions reversible, with undo offered right after; confirm only what cannot be undone, in a dialog that names the object and the consequence; an action with legal, financial or data consequences is reversible, reviewed before it takes effect, or confirmed.
Breach: delete or send something: no way back appears and nothing asked first; or a routine, reversible action asks for confirmation.
Source: NN/g, "Confirmation Dialogs Can Prevent User Errors (If Not Overused)" (nngroup.com/articles/confirmation-dialog); Nielsen, usability heuristic 3 "User control and freedom"; WCAG 2.2, SC 3.3.4 Error Prevention (Legal, Financial, Data).

**Keep rarely used options one step away** · default
Decision: show first what most people need and put specialised options behind one clearly labelled step, never more than two levels deep.
Breach: on a capture, rare settings sit beside the common ones with equal weight; or open the deferred options: they lead to a third level.
Source: NN/g, progressive disclosure (nngroup.com/articles/progressive-disclosure); Laws of UX, "Hick's Law" (lawsofux.com/hicks-law).

**Give every drag a single-pointer alternative** · firm
Decision: whatever is done by dragging (reordering, moving, resizing, sliding) can also be done with single clicks or taps, such as move buttons or a menu, unless dragging is essential to it.
Breach: for each draggable thing, try to reach the same result without dragging: there is no way.
Source: WCAG 2.2, SC 2.5.7 Dragging Movements (w3.org/TR/WCAG22); NN/g, "Designing Drag-and-Drop for Usability" (nngroup.com/articles/drag-drop).

**Always offer a way out** · firm
Decision: every dialog, panel, step of a flow and long operation shows a visible way to cancel, close, go back or stop, and going back returns to the previous state as the user left it.
Breach: open each dialog and panel, walk each step of a flow and start a long operation: one offers no visible close, cancel, back or stop.
Source: Nielsen, usability heuristic 3 "User control and freedom" (nngroup.com/articles/ten-usability-heuristics); NN/g, response time limits (nngroup.com/articles/response-times-3-important-limits); GOV.UK Design System, "Question pages" (design-system.service.gov.uk/patterns/question-pages).

## Accessibility

**Make every action reachable by keyboard** · firm
Decision: everything a pointer can do, the keyboard alone can do, with no timing on keystrokes, and focus can always leave a component it entered.
Breach: put the mouse aside and tab through the screen: an action cannot be reached or triggered, or focus gets stuck inside a component.
Source: WCAG 2.2, SC 2.1.1 Keyboard and SC 2.1.2 No Keyboard Trap (w3.org/TR/WCAG22).

**Move focus in a meaningful order** · firm
Decision: focus moves through the screen in an order that keeps its meaning, preferably the visual reading order; a modal dialog takes focus when it opens and gives it back to its trigger when it closes, and a non-modal panel comes right after its trigger in the order.
Breach: tab through the screen and open each dialog and panel: focus jumps against the reading order, stays behind an open dialog, or lands at the top of the page when a dialog closes.
Source: WCAG 2.2, SC 2.4.3 Focus Order (w3.org/WAI/WCAG22/Understanding/focus-order).

**Keep focus visible and uncovered** · firm
Decision: the focused element always shows a visible indicator, and no sticky bar, banner or panel hides it entirely.
Breach: tab through the whole screen while it scrolls: at some stop focus cannot be seen, or a sticky header, footer or banner covers the focused element.
Source: WCAG 2.2, SC 2.4.7 Focus Visible and SC 2.4.11 Focus Not Obscured (Minimum) (w3.org/TR/WCAG22).

**Give every non-text element a text alternative** · firm
Decision: images, icons and charts that carry meaning get a text equivalent serving the same purpose, an icon-only button gets a name saying its action, and purely decorative images are marked as decoration.
Breach: inspect each icon-only button, image and chart through the accessibility tree or a screen reader: one has no text equivalent, or a decorative image is announced.
Source: WCAG 2.2, SC 1.1.1 Non-text Content (w3.org/TR/WCAG22).

## Adaptation

**Design the narrow screen first** · default
Decision: design first for the narrowest screen, keeping the content and actions that matter most and putting content before navigation; wider screens add room and secondary material, not new priorities.
Breach: narrow the window to phone width: navigation, promotions or secondary material push the main content out of the first view, or a core action is missing at that width.
Source: Wroblewski, *Mobile First*, chapter 2 "Constraints" and chapter 4 "Organization" (lukew.com/mobilefirst).

**Let the content decide where the layout changes** · default
Decision: a group of elements switches between side by side and stacked when its own content would get too narrow, using the space of its container rather than fixed device widths.
Breach: widen the window slowly from narrow to wide: at some width a component squeezes its content into a cramped column or row, or leaves one item stranded on a row of its own.
Source: Pickering and Bell, *Every Layout*, "The Switcher" and "The Sidebar" (every-layout.dev/layouts); Wroblewski, *Mobile First*, chapter 7 "Layout" (lukew.com/mobilefirst).

**Fit 320 pixels wide without sideways scrolling** · firm
Decision: at a width of 320 CSS pixels, all content and every function remain available, and reading needs vertical scrolling only.
Breach: set the window to 320 pixels wide: content is cut off or overlaps, or the page scrolls sideways.
Source: WCAG 2.2, SC 1.4.10 Reflow (w3.org/TR/WCAG22).

**Survive larger text and wider spacing** · firm
Decision: boxes that hold text grow with it instead of having fixed sizes, so text zoomed to 200 %, or set with line height 1.5, paragraph spacing 2, letter spacing 0.12 and word spacing 0.16 times the size, loses nothing.
Breach: zoom text to 200 %, then apply those spacing values: text is clipped or overlaps, or a control can no longer be read.
Source: WCAG 2.2, SC 1.4.4 Resize Text and SC 1.4.12 Text Spacing (w3.org/TR/WCAG22); Pickering and Bell, *Every Layout*, "Boxes" (every-layout.dev/rudiments/boxes).

## Consistency

**Give the same function the same look** · default
Decision: elements that do the same thing look and behave alike on every screen, and elements that do different things do not share a look.
Breach: walk two or more screens: the same kind of action, status or control appears in two styles, or unrelated elements share one.
Source: Nielsen, usability heuristic 4 "Consistency and standards" (nngroup.com/articles/ten-usability-heuristics); Laws of UX, "Law of Similarity" (lawsofux.com/law-of-similarity).

**Follow the conventions users already know** · default
Decision: for common needs such as signing in, searching, navigating and filling forms, use the arrangement, words and behaviour people know from the products they use most, and depart only where the task clearly gains.
Breach: on a capture or in use, a common element sits or behaves unlike its usual form with no task reason.
Source: Laws of UX, "Jakob's Law" (lawsofux.com/jakobs-law); Nielsen, usability heuristic 4 "Consistency and standards".

**Keep navigation and help in the same place** · firm
Decision: navigation repeated across screens keeps the same order, and a way to get help appears in the same place relative to the rest on every screen, unless the user changes it.
Breach: walk three screens: a navigation item changes position, or the way to get help moves or disappears.
Source: WCAG 2.2, SC 3.2.3 Consistent Navigation and SC 3.2.6 Consistent Help (w3.org/TR/WCAG22).

## Motion

**Animate only to explain a change** · default
Decision: motion confirms an action, shows a change of state, shows where an element comes from or goes, or draws the eye to one change; nothing moves for decoration alone.
Breach: trigger each transition and say what it tells the user: one tells nothing, such as a flourish on load or a decorative loop.
Source: NN/g, "The Role of Animation and Motion in UX" (nngroup.com/articles/animation-purpose-ux); Head, *Designing Interface Animation*, chapter 4 excerpt (boxesandarrows.com/book-in-brief-designing-interface-animation); Willenskomer, "Creating Usability with Motion: The UX in Motion Manifesto" (uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto).

**Keep motion between 100 and 400 milliseconds** · default
Decision: about 100 ms for small feedback such as a toggle, 200 to 300 ms for larger changes such as a panel or a dialog, up to 400 ms only for long travel on large screens; exits run a little shorter than entrances, and the more often a motion is seen, the shorter it is.
Breach: trigger each transition, or read its declared duration: one lasts longer than 400 ms, or a frequent one lasts as long as a rare one.
Source: NN/g, "Executing UX Animations: Duration and Motion Characteristics" (nngroup.com/articles/animation-duration).

**Ease every movement** · default
Decision: nothing that moves goes at constant speed; elements entering or responding ease out, starting fast and settling gently, and elements leaving may ease in.
Breach: trigger each transition, or read its timing function: something moves at constant speed, or an entrance starts slowly.
Source: NN/g, "Executing UX Animations: Duration and Motion Characteristics" (nngroup.com/articles/animation-duration); Willenskomer, UX in Motion Manifesto, principle "Easing" (uxmag.com); Thomas and Johnston, Disney principle "Slow in and slow out" (en.wikipedia.org/wiki/Twelve_basic_principles_of_animation).

**Move one thing at a time** · default
Decision: a change has one main movement; elements that follow it start after short offsets so they read as one sequence, and any secondary motion supports the main one instead of competing with it.
Breach: trigger a change that moves several elements: they all start together and compete, or a secondary movement pulls the eye away from the main one.
Source: NN/g, "The Role of Animation and Motion in UX" (nngroup.com/articles/animation-purpose-ux); Willenskomer, UX in Motion Manifesto, principle "Offset & Delay" (uxmag.com); Thomas and Johnston, Disney principles "Staging" and "Secondary action" (en.wikipedia.org/wiki/Twelve_basic_principles_of_animation).

**Honour the reduce motion setting** · firm
Decision: when the device asks for reduced motion, movement that is not essential is removed or replaced by a change that does not travel, such as a fade or an instant switch, and the information the motion carried stays.
Breach: turn on the system's reduce motion setting and trigger every transition: something still slides, scales, zooms or moves in parallax.
Source: MDN, "prefers-reduced-motion" (developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion); WCAG 2.2, SC 2.3.3 Animation from Interactions (w3.org/TR/WCAG22); Head, "Designing Safer Web Animation for Motion Sensitivity" (alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity).

**Let people stop motion that plays on its own** · firm
Decision: anything that moves, blinks or scrolls by itself for more than five seconds, such as a carousel, a ticker or a looping illustration, can be paused, stopped or hidden.
Breach: open the screen and wait five seconds: something still moves with no way to pause, stop or hide it.
Source: WCAG 2.2, SC 2.2.2 Pause, Stop, Hide (w3.org/TR/WCAG22).

**Keep movement small relative to the screen** · default
Decision: prefer short travel and changes of opacity or colour to full-screen sweeps, deep zooms and layers moving at different speeds; keep large motion for when it explains a change of place, and let the user know before it happens.
Breach: trigger each transition on a large screen: something sweeps across most of the view, zooms through a large distance, or moves against the scroll.
Source: Head, "Designing Safer Web Animation for Motion Sensitivity" (alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity).
