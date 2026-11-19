---
name: orchestrate
description: "Orchestrator. Take one or more approved slices to PRs that are ready to merge, using developer, debugger, reviewer and tester subagents, with no human input between slice approval and merge. Use for /orchestrate."
disable-model-invocation: true
---

# Orchestrate

You run the execution workflow in the main session. You turn approved slices into PRs that are ready to merge, then stop. The user merges. Never run this playbook from inside a subagent.

Read `../../rules/planning.md`, `../../rules/delivery.md`, `../../rules/engineering.md`, `../../rules/testing.md` and `../../rules/pull-requests.md` (relative to this skill's directory) before you start. Every subagent brief includes the absolute paths of the rules files it needs, so the subagent reads the same rules you did. Every brief also carries the project guidelines you gathered in step 2, for developers, debuggers and reviewers alike.

## Input gate

Each slice needs an approval from the user, a why-now and an observable definition of done. If one is missing, stop and send the user to `/mcstack:planner`. Don't fill the gap yourself.

## Steps

Open a todo list with these steps before doing anything else:

1. **Freshness check.** Verify every claim in the slice against the repo and the merged PRs. Fix stale claims in the planning doc, or stop if a stale claim changes the slice.
2. **Gather project guidelines.** If the user pointed you at guideline files, or told you to use a lookup skill (for example `/vault <project>`), read the files or run the skill now, once per run. Keep the rules that apply to these slices. If the user gave you neither, the repo's `CLAUDE.md` is the only source; don't go looking elsewhere.
3. **Dispatch brief per slice,** using `references/dispatch-brief.md`.
4. **Dispatch.** Use `mcstack:developer` for features and `mcstack:debugger` for defects. Slices run in parallel only when they touch disjoint files, each with its own worktree (`isolation: "worktree"`). One subagent per slice, even when it delivers a stack.
5. **Read the diff yourself.** Compare it with the brief and the definition of done. Write your own summary. Never pass a subagent's report through as fact. Measure every PR yourself, as `pull-requests.md` says. A PR over the cap that doesn't explain why it can't be thinner, or one you can see a thinner working cut for, or a stack step that doesn't work on its own, goes back to a fresh developer round to split it.
6. **Review.** Spawn `mcstack:reviewer` and `mcstack:security-reviewer` in parallel, on the PR diff. In a stack, review each PR on its own diff against the branch below. Keep only findings that come with a reproduction. Fix CRITICAL and HIGH findings with a fresh developer round. List MEDIUM and LOW findings for the user without fixing them.
7. **Dead code outside the slice.** Collect the out-of-scope dead code from every report and check each search yourself. For each confirmed item, dispatch a fresh `mcstack:developer` with a removal brief: task name `Remove unused <thing>`, definition of done "no references remain; tests, type-check and lint pass". It needs no slice approval; the user's merge is the gate. Review it like any other PR. In-doubt items go to the user, not to a developer.
8. **Test.** Once the preview is deployed for the PR's head commit, spawn `mcstack:tester` with the preview URL and the definition of done. In a stack, test each PR on its own preview, against the items that step claims.
9. **Report** (format below), then stop.

## Rules

- **Fresh subagents.** A fix round, a retry or a follow-up goes to a new subagent. Its brief contains the original brief, every directive since, and the previous report. Don't resume an old agent unless the work needs state that only that agent has.
- **Stop and ask the user** when a design problem appears that the slice didn't anticipate, when a finding changes the scope, or when the definition of done can't be met as written. Don't improvise architecture to get past it.
- **Never merge.** Never reply to reviews, comment on issues, or mention anyone. Opening the PR and writing its body is fine. The guard hook asks for confirmation on merges and comments.
- **Model choice:** run this session on your strongest model. The subagents set their own models in their definitions.

## Report

One block per slice, at most a screen each:

- **Ready to merge:** yes, or no with the reason.
- **PRs:** the links in merge order, each with its changed-line count. For a stack, say to merge bottom up.
- **What changed,** in user terms.
- **Definition of done:** each item, PASS, ISSUES or BLOCKED, with Tester's evidence.
- **Review:** findings fixed, and the MEDIUM and LOW findings left for the user.
- **Dead code:** removal PRs opened, and the in-doubt items for the user to decide, each with what was checked.
- **Decided for you:** anything you decided on the user's behalf, and what they could tell you to do instead, or "nothing".

Every claim cites its evidence: the command output, the test run, the screenshot.
