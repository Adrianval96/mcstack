---
name: simplify
description: "Simplify a shipped feature. Once every slice of an epic has merged, run the simplifier on the feature's code, then take its proposals to refactor PRs that are ready to merge. Behaviour stays identical and no logic is added. Use for /simplify <epic>."
disable-model-invocation: true
---

# Simplify

You run in the main session, after a feature has shipped end to end. While slices are in flight, the code changes too fast for refactors to land cleanly. Once the whole epic has merged, the code holds still, so you can look at all of it together.

Read `../../rules/delivery.md`, `../../rules/engineering.md`, `../../rules/testing.md` and `../../rules/pull-requests.md` (relative to this skill's directory) before you start.

## Input gate

The user names an epic. Find its planning doc and the slice PRs it lists, and check with `gh pr view` that every one has merged. If one hasn't, stop and say which. The feature isn't shipped yet.

## Steps

Open a todo list with these steps before doing anything else:

1. **Gather project guidelines** the same way as the orchestrator's step 2.
2. **Simplify.** Spawn `mcstack:simplifier`. Its brief holds the epic, its definitions of done, the merged PR numbers, the files they touched, the project instructions, the absolute paths of the rules files and the project guidelines.
3. **Check the proposals yourself.** Re-run the evidence for each one marked apply. Drop any that changes behaviour or fails a check.
4. **Dispatch.** Group the apply proposals into refactor PRs, one concern each, under the size cap. Each PR gets a fresh `mcstack:developer` with a brief from `../orchestrate/references/dispatch-brief.md`:
   - **Task name:** `Simplify <feature>: <what>`.
   - **Definition of done:** "Behaviour unchanged: tests, type-check and lint pass, net lines go down", plus the epic's definition of done items the change touches, which must still pass.
   - **Approach:** the proposal, with its before and after.
   PRs that touch disjoint files run in parallel, each in its own worktree. They need no slice approval; the user's merge is the gate.
5. **Review and test** each PR as the orchestrator's steps 5, 6 and 8 say.
6. **Report,** then stop.

## Report

- **PRs:** the links, each with its net line change and whether it's ready to merge.
- **Left for you:** proposals marked consider, and anything outside the feature, each with the simplifier's reason.
- **Dropped:** proposals you rejected in step 3, and why.

The orchestrator's rules on fresh subagents, stopping and never merging apply unchanged.
