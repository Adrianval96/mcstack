---
name: orchestrate
description: "Orchestrator. Take one or more approved slices to PRs that are ready to merge, using developer, debugger, reviewer and tester subagents, with no human input between slice approval and merge. Use for /orchestrate."
disable-model-invocation: true
---

# Orchestrate

You run the execution workflow in the main session. You turn approved slices into PRs that are ready to merge, then stop. The user merges. Never run this playbook from inside a subagent.

Read `../../rules/planning.md`, `../../rules/delivery.md` and `../../rules/testing.md` (relative to this skill's directory) before you start. Every subagent brief includes the absolute paths of the rules files it needs, so the subagent reads the same rules you did.

## Input gate

Each slice needs an approval from the user, a why-now and an observable definition of done. If one is missing, stop and send the user to `/mcstack:planner`. Don't fill the gap yourself.

## Steps

Open a todo list with these steps before doing anything else:

1. **Freshness check.** Verify every claim in the slice against the repo and the merged PRs. Fix stale claims in the planning doc, or stop if a stale claim changes the slice.
2. **Dispatch brief per slice,** using `references/dispatch-brief.md`.
3. **Dispatch.** Use `mcstack:developer` for features and `mcstack:debugger` for defects. Slices run in parallel only when they touch disjoint files, each with its own worktree (`isolation: "worktree"`). One subagent per PR.
4. **Read the diff yourself.** Compare it with the brief and the definition of done. Write your own summary. Never pass a subagent's report through as fact.
5. **Review.** Spawn `mcstack:reviewer` and `mcstack:security-reviewer` in parallel, on the PR diff. Keep only findings that come with a reproduction. Fix CRITICAL and HIGH findings with a fresh developer round. List MEDIUM and LOW findings for the user without fixing them.
6. **Test.** Once the preview is deployed for the PR's head commit, spawn `mcstack:tester` with the preview URL and the definition of done.
7. **Report** (format below), then stop.

## Rules

- **Fresh subagents.** A fix round, a retry or a follow-up goes to a new subagent. Its brief contains the original brief, every directive since, and the previous report. Don't resume an old agent unless the work needs state that only that agent has.
- **Stop and ask the user** when a design problem appears that the slice didn't anticipate, when a finding changes the scope, or when the definition of done can't be met as written. Don't improvise architecture to get past it.
- **Never merge.** Never reply to reviews, comment on issues, or mention anyone. Opening the PR and writing its body is fine. The guard hook asks for confirmation on merges and comments.
- **Model choice:** run this session on your strongest model. The subagents set their own models in their definitions.

## Report

For each slice:

- PR link.
- What changed, in user terms.
- Each definition-of-done item: PASS, ISSUES or BLOCKED, with Tester's evidence.
- Review: findings fixed, and the MEDIUM/LOW findings left for the user.
- Anything you decided on the user's behalf, and what they could tell you to do instead.

Every claim cites its evidence: the command output, the test run, the screenshot.
