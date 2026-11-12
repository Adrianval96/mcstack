# mcstack

A Claude Code plugin for role-based development. Each role in the workflow has a written contract. The roles that need you run in your main session. The roles that don't run as subagents. Hooks enforce the rules that keep getting broken, instead of restating them.

It's my own workflow, built for a solo developer shipping a live production app with agents. Fork it and make it yours.

## Install

```
/plugin marketplace add Adrianval96/mcstack
/plugin install mcstack@mcstack
```

Plugin skills are namespaced, so the skills below are invoked as `/mcstack:<name>`.

## The roles

| Role | Runs as | Model | What it does |
|---|---|---|---|
| Product | skill `/mcstack:product` | your session model | Decides whether to build something at all. Makes the case against the idea first; "not now" is a valid answer |
| Planner | skill `/mcstack:planner` | your session model | Turns an approved feature into vertical slices, each with a why-now and an observable definition of done. You approve each slice |
| Designer | skill `/mcstack:designer` | your session model | Mockups and UX ideas. Marks every contestable choice as a fork, with the case for the alternative |
| Orchestrator | skill `/mcstack:orchestrate` | your session model | Takes approved slices to PRs that are ready to merge, using the subagents below |
| Developer | agent `mcstack:developer` | Sonnet | Implements one slice as one PR. Adds nothing the brief didn't ask for |
| Debugger | agent `mcstack:debugger` | Opus | Reproduces the bug, finds the root cause, writes a failing test, then fixes |
| Reviewer | agent `mcstack:reviewer` | Opus | Tries to break the PR. Keeps only findings it can reproduce with a command |
| Security reviewer | agent `mcstack:security-reviewer` | Opus | Covers auth, webhooks, injection, secrets and payments, with demonstrated findings only |
| Tester | agent `mcstack:tester` | Sonnet | Checks the deployed preview against the definition of done, and runs the Playwright suite for money paths |

Product, Planner and Designer are conversations, so they never run as subagents. A subagent can't ask you a question, so it fills gaps with assumptions, and a plan built on assumptions looks just as settled as a real one.

## The feature workflow

```
/mcstack:product  →  /mcstack:planner  →  you approve a slice
        →  /mcstack:orchestrate: developer → reviewer + security-reviewer → tester
        →  you merge
```

There are two human gates: slice approval and merge. Everything between them runs unattended.

## Guard hooks

`hooks/guard.py` runs before every Bash call and every GitHub MCP tool call.

| Always on | Decision |
|---|---|
| `git ... --no-verify` | deny |
| `gh pr merge`, `gh pr review`, `gh pr comment`, `gh issue comment`, posting to comment, review or merge API endpoints, and GitHub MCP merge, review and comment tools | ask |
| `git push --force` or `-f` (`--force-with-lease` is allowed) | ask |

Per project, add `.claude/mcstack.json` at the repo root (see [`examples/mcstack.json`](examples/mcstack.json)):

| Key | Effect |
|---|---|
| `branchPattern` | `git commit` is denied unless the current branch matches this regex |
| `forbiddenCommands` | a list of `{pattern, message}` objects. Matching Bash commands are denied, and the message tells the agent what to do instead |

When a mistake keeps recurring, add it to `forbiddenCommands` with a message that names the fix. That beats adding another paragraph to `CLAUDE.md`, which nothing enforces.

Note: cloud sessions may start on an auto-generated branch. If your project sets `branchPattern`, the agent has to rename the branch before its first commit.

## Rules

The skills and the orchestrator's dispatch briefs point at three short rules files:

- [`rules/planning.md`](rules/planning.md) covers the why-now test, the observable definition of done, specs as proposals, verifying against the repo, and two levels only.
- [`rules/delivery.md`](rules/delivery.md) covers lean scope, vertical slices, verification, and never speaking as the user.
- [`rules/testing.md`](rules/testing.md) covers behaviour over implementation, mocks drifting from the real contract, and tests that can't fail.

Project-specific conventions belong in each project's `CLAUDE.md`, not here.

## Tests

```
python3 -m unittest discover -s tests
```

## Credits

The adversarial review rule (no reproduction, no finding), the fresh-subagent rule and the debugging steps borrow ideas from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by poteto (MIT).

## License

MIT
