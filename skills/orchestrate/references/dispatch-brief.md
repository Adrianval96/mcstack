# Dispatch brief template

The brief must stand on its own. The subagent hasn't seen this conversation.

```markdown
## Goal
<the user's goal in one or two sentences: who it is for, and what changes for them>

## Slice
<ID and capability>. Approved by the user on <date>.

## Definition of done (observable)
<copied verbatim from the slice>

## Excludes
<copied verbatim from the slice>

## Starting state (verified <date>)
<what exists today, with file paths and PR numbers. Only facts you checked in step 1>

## Approach
<files to touch, the shape of the change, and the tests expected. Leave out anything the developer can decide>

## Conventions
- Project instructions: <path to the repo's CLAUDE.md or AGENTS.md>
- Rules: <absolute paths to rules/delivery.md and rules/testing.md>
- Branch: <name matching the project's branch convention>
- Test command: <the project's agreed command, exactly>

## Prior rounds
<for a fix round: the earlier briefs, every directive since, and the previous report. Otherwise "none">

## Report back
The PR link, the files changed, the test command and its output, and anything you stopped on or could not do.
```
