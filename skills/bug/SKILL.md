---
name: bug
description: "Bug intake. Take a bug the user describes in a prompt, log it as an issue, gather the repo context and the code it touches, then run debugger → reviewer + security-reviewer → tester to a PR that is ready to merge. Use for /bug."
disable-model-invocation: true
---

# Bug

You turn a bug the user describes into a logged issue and a PR that is ready to merge, then stop. The user merges. You run in the main session because you dispatch subagents; never run this from inside a subagent.

Read `../../rules/delivery.md`, `../../rules/engineering.md`, `../../rules/testing.md` and `../orchestrate/SKILL.md` (relative to this skill's directory) before you start.

The user's report is the approval for this one fix. It does not approve anything beyond the defect.

## Steps

Open a todo list with these steps before doing anything else:

1. **Find the repo.** The one the user names, or the current directory. Read its `CLAUDE.md` or `AGENTS.md`, and note the branch convention, the test, type-check and lint commands, and how previews deploy.
2. **Gather project guidelines** the same way as the orchestrator's step 2: files the user pointed at, or a lookup skill they named. Otherwise the repo's instructions are the only source.
3. **Read the code the bug touches.** Search for the symptom: the route, page, error text, job or command the user named. Follow it to the files that produce it, and read them. Check `git log` and recent merged PRs on those files, since a fresh regression usually has an obvious suspect. Do not fix anything yourself.
4. **Ask only what blocks a reproduction.** If you can't tell where or how the bug shows (which page, which input, which environment), ask the user, once, in one message. Otherwise carry on.
5. **Log it.** Search open issues first (`gh issue list --search "<keywords>"`); if it's already logged, use that issue. Otherwise open one with `gh issue create`, or in the tracker the project instructions name. The user asked for it by running this skill, so this is your own work product, not speaking for them. The issue holds:
   - **What happens** and **what should happen**, in the user's words.
   - **Where:** the surface, the environment, the steps to reproduce.
   - **Suspected area:** the files from step 3, labelled as a suspicion, not a diagnosis.
6. **Write the debugger brief** with `../orchestrate/references/dispatch-brief.md`:
   - **Slice:** the issue, as `#<number>` plus a short task name. It goes at the end of the PR title, and the body says `Fixes #<number>`.
   - **Definition of done:** "Following the issue's steps on <surface> no longer shows <symptom>; it shows <expected>. A test that fails before the fix passes after it."
   - **Excludes:** "Other defects found on the way: report them, don't fix them."
   - **Starting state:** what you verified in step 3, with file paths and commits.
   - **Approach:** the suspected area and the reproduction steps. Leave the diagnosis to the debugger.
7. **Run the orchestrator's steps 4 to 9** with this one brief: dispatch `mcstack:debugger`, read the diff yourself, then review with `mcstack:reviewer` and `mcstack:security-reviewer`, handle dead code, test on the preview with `mcstack:tester`, and report. Its rules on fresh subagents, fix rounds and stopping apply unchanged.

## Stop and ask the user when

- The debugger reports `not reproduced`. Give the user what was tried and ask for the missing detail. Don't let a fix go ahead on a guess.
- The root cause needs a design change, a migration or a new capability. That's planned work: send it to `/mcstack:planner` with the issue link.
- The bug is in a third-party service or in data, not in the repo's code. Say what you found and stop.

## Report

The orchestrator's report, plus one line at the top: the issue link, and its state (open until the PR merges and closes it).
