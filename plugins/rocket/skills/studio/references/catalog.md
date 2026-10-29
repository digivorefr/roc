# Catalog

Ways to solve interface problems, grouped by the problem the user faces. Each way states what the user sees and does, when it serves, when it fails, and a reference that names it; "Avoid when" cites frame rules by their title. Tidwell pattern names are those of *Designing Interfaces*, third edition, as its public table of contents lists them (for instance on helion.pl).

## Browse a collection and work on one item

**List and detail side by side**
What the user sees and does: the list stays on one side and the selected item opens beside it; on a narrow screen the detail replaces the list, with a way back.
Use when: people move from item to item and compare as they go.
Avoid when: the detail needs the full width, or items are opened rarely.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Two-Panel Selector or Split View".

**Drill down within one window**
What the user sees and does: choosing an item replaces the list with that item, and a back step returns to the list where they left it, on every width.
Use when: items are opened one at a time and each needs the whole screen.
Avoid when: people compare neighbouring items, since each comparison costs a round trip.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "One-Window Drilldown".

**Expand the item in place**
What the user sees and does: choosing an item opens its details inside the list, under its row, and choosing it again closes them; on a narrow screen the details take the full row width.
Use when: details are short and people check a few items without leaving the list.
Avoid when: details are long, or people leave several open and lose their place in the list.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "List Inlay"; NN/g, "Data Tables: Four Major User Tasks" (nngroup.com/articles/data-tables).

## Find something in a large set

**Search first**
What the user sees and does: a search field leads the screen and returns a list of results the user narrows or opens; on a narrow screen the field stays at the top.
Use when: people know what they are looking for and can name it.
Avoid when: people do not know the words the content uses, or want to see what exists.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Feature, Search, and Browse".

**Filter by facets**
What the user sees and does: beside or above the results, one filter per attribute of the content narrows the set as the user picks values, with the active filters shown; on a narrow screen the filters open in a panel.
Use when: the set is large and people narrow it along several attributes at once.
Avoid when: one or two filters would do, or the content lacks the data each facet needs; see "Offer few choices and one primary action".
Source: NN/g, "Filters vs. Facets: Definitions" (nngroup.com/articles/filters-vs-facets); Tidwell, Brewer and Valencia, *Designing Interfaces*, "Dynamic Queries".

**Browse by category**
What the user sees and does: the set is arranged in a few named categories that the user opens one level at a time until they reach the item.
Use when: people recognise the kind of thing they want without knowing its name, or want to see what exists.
Avoid when: categories overlap, so people cannot guess which one holds an item.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Feature, Search, and Browse".

**Overview first, then zoom and filter**
What the user sees and does: the whole set appears at once in a compact form such as a map, a chart or a grid; the user zooms into or filters a region, then opens one item for its details.
Use when: the items have positions or values that make clusters, gaps and outliers visible.
Avoid when: the items share no attribute to draw them by, or people look for one known item.
Source: Shneiderman, "The Eyes Have It", section 2 (drum.lib.umd.edu/items/155a868e-fb83-4115-9899-9187ea8c0498).

## Edit

**Edit in place**
What the user sees and does: the value or the row turns into fields where it is shown, looks clearly different while editing, and is saved or cancelled there; on a narrow screen this suits single values only.
Use when: the change touches one value or a short row, and people glance at the neighbouring items while editing.
Avoid when: the record has many fields or the table is wide.
Source: NN/g, "Data Tables: Four Major User Tasks", edit in place (nngroup.com/articles/data-tables).

**Edit in a side panel**
What the user sees and does: the whole record opens in a panel beside the collection, which stays visible; on a narrow screen the panel covers the collection and closes back to it.
Use when: the record has more fields than a row can hold, and people check other records for reference.
Avoid when: the form needs the full width, or editing is the screen's only task.
Source: NN/g, "Data Tables: Four Major User Tasks", side panel (nngroup.com/articles/data-tables).

**A page of its own for the form**
What the user sees and does: editing opens a dedicated page that holds every property of the item, grouped in titled sections and saved together; it reads the same on every width.
Use when: the item has many properties that people change rarely and deliberately.
Avoid when: people change one value at a time while scanning a list.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Settings Editor".

**Direct manipulation with an alternative to dragging**
What the user sees and does: the user moves, resizes or reorders objects by acting on them and sees the result as they go, while move buttons or a menu reach the same result without dragging; on a touch screen draggable items show a handle and keep space around them.
Use when: the change is spatial, such as order, position or size, and seeing the result guides it.
Avoid when: the change is precise, repetitive or spans a long distance; see "Give every drag a single-pointer alternative".
Source: NN/g, "Direct Manipulation: Definition" (nngroup.com/articles/direct-manipulation); NN/g, "Designing Drag-and-Drop for Usability" (nngroup.com/articles/drag-drop).

## Complete a long task

**Step by step**
What the user sees and does: the task is cut into steps shown in order, with the list of steps and the current one in view and a way back from each; on a narrow screen the list of steps shrinks to a position such as "step 2 of 5".
Use when: the task is rare, people are new to it, and later steps depend on earlier answers.
Avoid when: people do the task often, compare information across steps, or are likely to be interrupted.
Source: NN/g, "Wizards: Definition and Design Recommendations" (nngroup.com/articles/wizards); Tidwell, Brewer and Valencia, *Designing Interfaces*, "Wizard".

**One question per page**
What the user sees and does: each page asks one thing, with the question as its heading, a back link to the previous answer and one button to move on, on every width.
Use when: occasional users fill the task in, on any device.
Avoid when: experienced users fill it in often and move fast, where related questions can share a page.
Source: GOV.UK Design System, "Question pages" (design-system.service.gov.uk/patterns/question-pages).

**A task list**
What the user sees and does: one page lists the parts of the task, each with its status; the user opens them in any order and can leave and come back over several sessions, while parts that cannot start yet show without a link.
Use when: the task has several parts that may take more than one session.
Avoid when: the task is short, or its parts must be done in a fixed order.
Source: GOV.UK Design System, "Complete multiple tasks" (design-system.service.gov.uk/patterns/complete-multiple-tasks).

**Check answers before sending**
What the user sees and does: before the last step, a page lists every answer by section with a change link beside each; a change returns the user to this page without redoing the rest, and the final button names the action.
Use when: the task ends in a submission that is hard to take back.
Avoid when: the task is a few fields long; a very large task checks each section instead of one page at the end.
Source: GOV.UK Design System, "Check answers" (design-system.service.gov.uk/patterns/check-answers).

## Show more without overwhelming

**Progressive disclosure**
What the user sees and does: the first view holds what most people need, and one clearly labelled step reveals the specialised options.
Use when: a few options serve most people and the rest serve a few.
Avoid when: people need the hidden options often; see "Keep rarely used options one step away".
Source: NN/g, progressive disclosure (nngroup.com/articles/progressive-disclosure).

**Details on demand**
What the user sees and does: each item shows a short summary, and selecting one shows its full details in a tip, a panel or an opened row; on a touch screen a tap does what hover does elsewhere.
Use when: people scan many items and need details for only a few.
Avoid when: the details are what people choose between items by, so they would open every item in turn.
Source: Shneiderman, "The Eyes Have It", section 3, "Details-on-demand" (drum.lib.umd.edu/items/155a868e-fb83-4115-9899-9187ea8c0498); Tidwell, Brewer and Valencia, *Designing Interfaces*, "Datatips".

**One main area at the centre**
What the user sees and does: the work itself, a document, a canvas or a record, takes the largest central area, with tools and navigation around it at lower weight; on a narrow screen the tools fold behind a control.
Use when: people spend most of their time on one piece of content.
Avoid when: the screen has no single main thing, such as a set of equal entry points.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Center Stage".

## Nothing to show yet

**An empty state that invites the first action**
What the user sees and does: where content will appear, a short message says why the area is empty, with a button that starts the task that fills it and a link to learn more.
Use when: a list, a board or a panel is empty because nothing has been created yet.
Avoid when: the area is empty because data is still loading or a search found nothing; see "Design the empty, loading, error and success states".
Source: NN/g, "Designing Empty States in Complex Applications: 3 Guidelines" (nngroup.com/articles/empty-state-interface-design); Wathan and Schoger, *Refactoring UI*, "Don't overlook empty states" (refactoringui.com/book).

**Sample content**
What the user sees and does: the empty product shows demo data, marked as such, that the user can explore safely, next to the way to bring in their own.
Use when: the product's value shows only once data is in, and bringing real data in takes time.
Avoid when: sample data could be mistaken for real records or end up in real results.
Source: NN/g, "Designing Empty States in Complex Applications: 3 Guidelines", demo data (nngroup.com/articles/empty-state-interface-design).

**A learning cue in the empty space**
What the user sees and does: the empty area explains in a sentence or two what the feature does and how it fills, at the moment the user first meets it.
Use when: the feature is not obvious and people meet it before using it.
Avoid when: the feature explains itself, where the first action alone is enough.
Source: NN/g, "Designing Empty States in Complex Applications: 3 Guidelines", learning cues (nngroup.com/articles/empty-state-interface-design); NN/g, "Help and Documentation (Usability Heuristic #10)", pull revelations (nngroup.com/articles/help-and-documentation).

## Act on something risky

**Undo after the fact**
What the user sees and does: the action takes effect at once and the user can reverse it right after, or step back through several past actions.
Use when: the action is frequent and can be reversed.
Avoid when: the action cannot be taken back, such as a payment or a message that has left; see "Prefer undo to confirmation".
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Multilevel Undo"; Nielsen, usability heuristic 3 "User control and freedom" (nngroup.com/articles/ten-usability-heuristics).

**Review before it takes effect**
What the user sees and does: before the action takes effect, the user sees exactly what will happen (the items, the amounts, the recipients), can correct any of it, then commits with a button naming the action.
Use when: the action commits legal, financial or stored data, or several answers at once.
Avoid when: the action is small and reversible, where undo costs less.
Source: WCAG 2.2, SC 3.3.4 Error Prevention (Legal, Financial, Data) (w3.org/TR/WCAG22); GOV.UK Design System, "Check answers" (design-system.service.gov.uk/patterns/check-answers).

**A confirmation kept for the irreversible**
What the user sees and does: a dialog interrupts only before an action that cannot be undone, names the object and the consequence, and offers buttons named by their outcome.
Use when: the loss is serious and permanent, such as closing an account.
Avoid when: the action is routine or reversible, since frequent confirmations teach people to click through; see "Prefer undo to confirmation".
Source: NN/g, "Confirmation Dialogs Can Prevent User Errors (If Not Overused)" (nngroup.com/articles/confirmation-dialog); GOV.UK Design System, "Button", warning buttons (design-system.service.gov.uk/components/button).

## Wait

**A skeleton of the page while it loads**
What the user sees and does: the page's layout appears at once as plain blocks where content will be, and fills in as the data arrives.
Use when: a full page or screen loads in roughly one to ten seconds.
Avoid when: the load takes under a second or over ten, or the wait is an upload or a conversion; see "Show progress on any wait over a second".
Source: NN/g, "Skeleton Screens 101" (nngroup.com/articles/skeleton-screens).

**Progress with how much is done**
What the user sees and does: a bar or a count shows how far the work has gone and roughly how long remains, in steps when there are steps, with a way to stop it.
Use when: the wait runs past about ten seconds, or the job works through a series of items.
Avoid when: the wait is short; see "Show progress on any wait over a second".
Source: NN/g, "Progress Indicators Make a Slow System Less Insufferable" (nngroup.com/articles/progress-indicators); Tidwell, Brewer and Valencia, *Designing Interfaces*, "Progress Indicator".

**Work in the background and say when it is done**
What the user sees and does: the long job runs while the user carries on elsewhere, and a notification that makes sense on its own says when it has finished and leads to the result.
Use when: the job takes long enough that people would rather do something else meanwhile.
Avoid when: nothing useful can be done until the result arrives.
Source: NN/g, response time limits (nngroup.com/articles/response-times-3-important-limits); NN/g, "Indicators, Validations, and Notifications: Pick the Correct Communication Option" (nngroup.com/articles/indicators-validations-notifications).

## Move between areas

**Persistent navigation**
What the user sees and does: a bar listing the main sections stays in view on every screen; on a narrow screen it becomes a tab bar of about five items, or folds behind a menu control when there are more.
Use when: people come back often, move between several tasks, and the sections follow no set order.
Avoid when: the service is one linear journey, where a task list or steps show the order instead.
Source: GOV.UK Design System, "Navigate a service" (design-system.service.gov.uk/patterns/navigate-a-service); NN/g, "Basic Patterns for Mobile Navigation: A Primer" (nngroup.com/articles/mobile-navigation-patterns).

**Step-by-step navigation**
What the user sees and does: a numbered list of the steps of a whole journey, each opening onto the pages or services for that step, shown beside every page of the journey or on a page of its own.
Use when: a journey with a clear start, end and order spans several services or pages.
Avoid when: the user is inside a single transaction, or the parts have no useful order.
Source: GOV.UK Design System, "Step by step navigation" (design-system.service.gov.uk/patterns/step-by-step-navigation).

**Breadcrumbs**
What the user sees and does: a trail at the top of the page links to each level above the current page, starting from home; on a narrow screen it shows only the parent level.
Use when: the structure is several levels deep and people land on inner pages from outside.
Avoid when: the structure is flat, or the pages form a linear process.
Source: GOV.UK Design System, "Breadcrumbs" (design-system.service.gov.uk/components/breadcrumbs); NN/g, "Breadcrumbs: 11 Design Guidelines for Desktop and Mobile" (nngroup.com/articles/breadcrumbs).

**A hub to return to between sections**
What the user sees and does: a home screen lists every main section, and the user goes back to it to move from one section to another.
Use when: people do one task per visit and the sections are independent.
Avoid when: people move between sections often, since every move costs a return to the hub.
Source: NN/g, "Basic Patterns for Mobile Navigation: A Primer", navigation hub (nngroup.com/articles/mobile-navigation-patterns).

## Compare

**One table with the items as columns**
What the user sees and does: each item is a column and each attribute a row labelled on the left, the item names stay in view while scrolling, and the user adds or removes items; on a narrow screen it holds two items at most.
Use when: people weigh a handful of similar options, up to about five, across shared attributes.
Avoid when: the items have few attributes in common, or the choice rests on looks.
Source: NN/g, "Comparison Tables for Products, Services, and Features" (nngroup.com/articles/comparison-tables).

**Only the differences**
What the user sees and does: a switch hides the attributes all items share, or the cells that differ are marked, so the eye lands on what sets the items apart.
Use when: the items share most attributes and a few differences decide.
Avoid when: people must check every attribute of each item, not only what differs, or the differing cells would be marked by colour alone; see "Never carry meaning by colour alone".
Source: NN/g, "Comparison Tables for Products, Services, and Features" (nngroup.com/articles/comparison-tables).

**Small multiples**
What the user sees and does: the same small chart repeats for each item on one shared scale, side by side, so differences in shape show at a glance; on a narrow screen the charts stack.
Use when: people compare how one measure behaves across many items or groups.
Avoid when: the items are few and exact values matter more than shapes.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Small Multiples".

## Create

**Create in place where the item will live**
What the user sees and does: an empty row at the end of the list takes a new item directly, which then sits among the others.
Use when: items are short, a title or a few fields, and people add several in a row.
Avoid when: a new item needs many fields, or a choice of kind first.
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "New-Item Row".

**Start from a template**
What the user sees and does: the user picks a ready-made starting point for a common kind of item and adapts it, instead of starting blank.
Use when: items of a kind share much of their structure, and a blank start leaves new users stuck.
Avoid when: items rarely resemble each other.
Source: NN/g, "Help and Documentation (Usability Heuristic #10)", templates (nngroup.com/articles/help-and-documentation).

**Build on a canvas from a palette**
What the user sees and does: a palette of parts sits beside a canvas, and the user places parts on the canvas and arranges them; on a narrow screen the palette folds into a drawer.
Use when: people compose something visual or structural from parts, such as a diagram or a layout.
Avoid when: the item is a set of fields rather than an arrangement; see "Give every drag a single-pointer alternative".
Source: Tidwell, Brewer and Valencia, *Designing Interfaces*, "Canvas Plus Palette".
