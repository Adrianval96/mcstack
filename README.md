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
| Lead | skill `/mcstack:lead` | your session model | Reads the spec and the code, says where the project stands, what's left and what's feasible, and breaks the remaining work into epics |
| Planner | skill `/mcstack:planner` | your session model | Turns an approved feature into vertical slices, each with a why-now and an observable definition of done. You approve each slice |
| Designer | skill `/mcstack:designer` | your session model | Mockups and UX ideas. Marks every contestable choice as a fork, with the case for the alternative |
| Orchestrator | skill `/mcstack:orchestrate` | your session model | Takes approved slices to PRs that are ready to merge, using the subagents below |
| Simplify | skill `/mcstack:simplify` | your session model | Runs `/ponytail:ponytail-review` (and `/security-review` where it applies) and the simplifier on an epic's code, and takes the proposals to refactor PRs that are ready to merge |
| Bug intake | skill `/mcstack:bug` | your session model | Takes a bug you describe, logs it as an issue, reads the code it touches, and runs it to a PR that is ready to merge |
| Developer | agent `mcstack:developer` | Sonnet | Implements one slice as one PR, or a stack of PRs under 200 lines each. Adds nothing the brief didn't ask for |
| Debugger | agent `mcstack:debugger` | Opus | Reproduces the bug, finds the root cause, writes a failing test, then fixes |
| Reviewer | agent `mcstack:reviewer` | Opus | Tries to break the PR. Keeps only findings it can reproduce with a command |
| Security reviewer | agent `mcstack:security-reviewer` | Opus | Covers auth, webhooks, injection, secrets and payments, with demonstrated findings only |
| Tester | agent `mcstack:tester` | Sonnet | Checks the deployed preview against the definition of done, and runs the Playwright suite for money paths |
| Simplifier | agent `mcstack:simplifier` | Opus | Reads a shipped feature's code, questions the developers' decisions, and proposes refactors that keep behaviour identical and add no logic. Each one must be applied and tested before it counts |

Product, Lead, Planner and Designer are conversations, so they never run as subagents. A subagent can't ask you a question, so it fills gaps with assumptions, and a plan built on assumptions looks just as settled as a real one.

## The feature workflow

```
/mcstack:product  →  /mcstack:lead  →  /mcstack:planner  →  you approve a slice
        →  /mcstack:orchestrate: developer → reviewer + security-reviewer → tester
        →  you merge
        →  once the epic's last PR merges, the orchestrator runs simplifier → refactor PRs → you merge
```

There are two human gates: slice approval and merge.

## The bug workflow

```
/mcstack:bug <what you saw, where>  →  issue logged
        →  debugger → reviewer + security-reviewer → tester
        →  you merge
```

Your report is the approval for that one fix, so merge is the only gate. A bug that turns out to need a design change goes back to `/mcstack:planner`.

Tell the orchestrator where your coding guidelines live: files to load, or a lookup skill to run (a notes-vault reader, say). It gathers them once per run and puts the rules that apply into every subagent brief, so nothing machine-specific goes in the repo. Everything between them runs unattended.

## Use it in every session

Local: the install above, once per machine.

Cloud sessions start from a fresh container. To have the plugin there, declare it in the repo's `.claude/settings.json` so it installs automatically:

```json
{
  "extraKnownMarketplaces": {
    "mcstack": { "source": { "source": "github", "repo": "Adrianval96/mcstack" } }
  },
  "enabledPlugins": { "mcstack@mcstack": true }
}
```

## Updating

An install is a copy of the plugin, cached under its `version` and pinned to a git commit. Edits on GitHub don't reach an existing install by themselves.

1. Change the plugin and bump `version` in `.claude-plugin/plugin.json`.
2. Push to `main`.
3. On each machine, run `claude plugin update mcstack@mcstack`. It refreshes the marketplace first. Or turn on auto-update for the `mcstack` marketplace in `/plugin` → Marketplaces.
4. Start a new session. Running sessions keep the version they started with.

Cloud sessions that declare the plugin in `.claude/settings.json` install it fresh, so they always get the latest `main`.

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

The skills and the orchestrator's dispatch briefs point at five short rules files:

- [`rules/planning.md`](rules/planning.md) covers the why-now test, the observable definition of done, specs as proposals, verifying against the repo, and two levels only.
- [`rules/delivery.md`](rules/delivery.md) covers lean scope, vertical slices, verification, and never speaking as the user.
- [`rules/engineering.md`](rules/engineering.md) covers the rules that hold in every project: ports-and-adapters architecture with dependencies pointing inward, reuse before writing, no new dependencies without asking, strict types, and validation at trust boundaries.
- [`rules/pull-requests.md`](rules/pull-requests.md) covers how Developer and Debugger write a PR for human review: when to open one, the 200-line cap and stacked PRs, the title, the body sections, and keeping it true after fix rounds.
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
