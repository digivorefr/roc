# Roc agents and skills

This repo is containing skills and agents made to assist a human senior developer during development process.

## Agents
### roc:spec-writer
Writes specification for a given topic following precise instructions: `write a spec with roc:spec-writer`
Call back agent to refine specification: `relaunch agent with thoses details: ...`

### roc:spec-maker
Implements specification files, plans, complex instructions autonomously. Run final checks.
`Implement with roc:spec-maker`


## Skills
### roc:commit-writer
Proposes 3 inline commit message from diff with main branch or specified context.
`/roc:commit-writer`
`/roc:commit-writer only for thoses files: ...`

### roc:pr-writer
Proposes a short PR description
`/roc:pr-writer`

### roc:myself
Indicates the user wants to code itself. Agent will provide instructions and insights

### roc:no-code
Prevent the agent to write any code. Useful for long chat about technical approaches, architecture, debugging

### roc:review
Review the last changes with specific standards, provides insights on several topics: Issues, DRY, contigous patterns, spec conformity, tests quality
