# Pull request rules

These rules apply to Developer and Debugger when they open a PR, and to Reviewer when it checks one. A PR is read by a human who decides whether to merge. Write for that person: they haven't seen the brief, the conversation or your session.

## Before you open it

- **The work is complete and the brief asked for a PR.** Never open one to save progress.
- **It's one vertical slice.** If the body would have to explain why new code has no callers, it's a layer PR. Stop and report instead of opening it.
- **It fits the budget: about 200 changed lines,** not counting migrations, generated files, lockfiles and deleted lines. If it's going to be bigger, stop before writing the rest and report a split within the capability. Don't fall back to splitting by layer.
- **A migration was run locally** (up, down, then up again) against a real database, and the app still loads. If you couldn't run it, don't open the PR; report why.
- **Tests, type-check and lint pass** with the project's commands, in this session.

## Title

Follow the format of the repo's recent merged PRs (run `gh pr list --state merged --limit 10`). With no history, use `<type>: <the change, in user terms>`. Name what changes for the user, not the files touched.

**End the title with the task from the brief's Slice line, in parentheses:** the ID in full (`(SHOP-09k-b)`, never `(09k-b)`), or the task name when there's no ID. Every PR carries one, so the reviewer can trace it to the plan and anyone can find it by searching the ID.

> [Change] Hide variants Printful never confirmed from the shop (SHOP-09k-b)

## Body

Use these sections, in this order. Leave a section out only when it would say nothing; write "none" where the absence is information (no migration, nothing left out).

```markdown
## Why
<The same task as the title (ID in full, or the task name) and what breaks or changes for the user without this. One or two sentences.>

## What changed
<The behaviour first, then the mechanism. Group by concern, not by file. Name a file only where the reviewer needs to find it.>
- Migration: <yes, and what it does / none>
- Config, env vars, feature flags, dependencies: <each change / none>

## Definition of done
- [ ] <each item, copied from the brief. Tick only what you checked yourself, and say how>

## How to review
<Where to start reading, and the one or two places where a mistake would hide. For a wide mechanical change, the command that proves the pattern holds everywhere.>

## How to test
<Steps a person can follow on the preview: the page or URL, what to do, what they should see. A table when there are several cases. Any flag, data or account the test needs.>

## Tests
<The cases you added, as behaviour: what each one covers, including edge cases and error paths. Then what no test covers, and why.>

## Not verified
- [ ] <each thing you couldn't check, and what it would mean if it fails. "If X, don't merge" when it's a merge risk.>

## Left out
<The brief's exclusions, plus anything you noticed and deliberately didn't do.>
```

## Writing

- **Lead with the answer.** The first sentence of each section says the thing; no "this PR aims to".
- **Prose for reasons, lists for enumerable things.** No trailing summary, no marketing words, no emoji.
- **Label every claim.** Say what you measured, what you inferred and what you're guessing. "Inference, not proven" is a useful sentence.
- **Put merge risks where they'll be seen.** Anything unverified that could break production goes in Not verified, never inside a list of things that passed.
- **Write the PR as a description of the change, not as the user speaking.** Replies, review requests and mentions stay off-limits (see `delivery.md`).

## After a fix round

Rewrite the sections the fix changed so the body matches the diff as it is now. Don't append a changelog of rounds. Tick or untick Definition of done items to match what you checked on the final diff.
