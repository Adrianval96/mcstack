---
name: simplify
description: "Simplify a feature. Run an over-engineering review and, where it applies, a security review on an epic's code, then the simplifier, then take its proposals to refactor PRs that are ready to merge. Behaviour stays identical and no logic is added. Use for /simplify <epic>."
disable-model-invocation: true
---

# Simplify

You run in the main session. The orchestrator runs these steps as its last action, once every PR of an epic has merged: while slices are in flight, the code changes too fast for refactors to land cleanly. The user can also run `/mcstack:simplify <epic>` at any time; then you run on whatever has landed, without checking.

Read `../../rules/delivery.md`, `../../rules/engineering.md`, `../../rules/testing.md` and `../../rules/pull-requests.md` (relative to this skill's directory) before you start.

## Input

An epic. Find its planning doc and the slice PRs it lists.

## Steps

Open a todo list with these steps before doing anything else:

1. **Gather project guidelines** the same way as the orchestrator's step 2.
2. **Review the feature.** Spawn a general-purpose subagent that runs `/ponytail:ponytail-review` on the files the epic's PRs touched. If those files include routes, auth, payments, webhooks, forms or environment configuration, spawn a second one in parallel that runs `/security-review` on them. Each returns its findings with file and line. If the ponytail plugin isn't installed, say so in the report and go on without it.
3. **Simplify.** Spawn `mcstack:simplifier`. Its brief holds the epic, its definitions of done, its PR numbers, the files they touched, the project instructions, the absolute paths of the rules files, the project guidelines, and the ponytail findings as leads to apply and test like its own.
4. **Check the proposals yourself.** Re-run the evidence for each one marked apply. Drop any that changes behaviour or fails a check.
5. **Dispatch.** Group the apply proposals into refactor PRs, one concern each, under the size cap. Each PR gets a fresh `mcstack:developer` with a brief from `../orchestrate/references/dispatch-brief.md`:
   - **Task name:** `Simplify <feature>: <what>`.
   - **Definition of done:** "Behaviour unchanged: tests, type-check and lint pass, net lines go down", plus the epic's definition of done items the change touches, which must still pass.
   - **Approach:** the proposal, with its before and after.
   PRs that touch disjoint files run in parallel, each in its own worktree. They need no slice approval; the user's merge is the gate.
6. **Review and test** each PR as the orchestrator's steps 5, 6 and 8 say.
7. **Report,** then stop.

## Report

- **Security:** each finding from step 2 you could confirm, most severe first. A fix changes behaviour, so it never goes in a simplify PR: propose each one as a side session (`delivery.md`). Or "not run", or "none".
- **PRs:** the links, each with its net line change and whether it's ready to merge.
- **Left for you:** proposals marked consider, each with the simplifier's reason.
- **Outside the feature:** each item proposed as a side session or logged to the backlog (`delivery.md`), or "none".
- **Dropped:** proposals and ponytail findings you rejected in step 4, and why.

The orchestrator's rules on fresh subagents, stopping and never merging apply unchanged.
