# Delivery rules

These rules apply to Orchestrator, Developer, Debugger, Reviewer and Tester.

## Scope

- **Lean.** A task goes exactly as far as its description. Don't add features, guards, validation, abstractions, or error handling beyond the codebase's existing standard. If an idea seems worth having, raise it as a question. Don't build it and explain afterwards.
- **Vertical slices.** Every PR ships a capability that works end to end. Never ship a helper, type or component that has no caller. The only exceptions are foundation slices: schema plus migration, flag plumbing, configuration. A "helper" PR followed by a "wire it up" PR is two layer PRs. Merged into one, they are usually smaller, because the integration is what lets the old code be deleted.
- **One task at a time.** Don't refactor unrelated code in the same PR.

## Git

- **Name the branch for the work** before the first edit, using the project's convention. The guard hook enforces it when the project configures `branchPattern`.
- **No WIP commits in history, and no PRs nobody asked for.** Open a PR only when the work is complete and a PR has been requested.
- **The PR body describes the change:** why it exists, what it does, how it was verified, and what it leaves out.

## Verification

- **Check the real thing, not a proxy.** Run the feature, read the actual value, inspect the diff. "It compiles" and an agent's own report are not evidence.
- **Back every claim with evidence or a label.** Say what was measured, what was inferred, and what is a guess. Never hand the user a check you could have run yourself.
- **"Tests pass" only after running them,** with the project's agreed command, in this session.

## Speaking for the user

An agent never publishes as the user without an explicit request in that session. Approval for one post is not approval for the next.

| Allowed: authoring your own work product | Needs an explicit request, every time |
|---|---|
| Commits and pushes to a feature branch | Replying to a review comment or thread |
| Opening a PR you created, and writing its title and body | Commenting on an issue or PR you didn't open |
| Editing the title or body of a PR you opened | Requesting a review, assigning anyone, @-mentioning anyone |
| Closing a PR you opened, with a comment explaining why | Merging a PR |
| | Anything outside the repo: email, chat, docs, social media |

The test: would a reader take this as the user speaking to them? If yes, ask first. The guard hook makes merges and comments require confirmation.

When a review comment has been addressed in code, report it in chat and let the user close the thread.
