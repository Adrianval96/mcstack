# Planning rules

These rules apply to Product, Planner, and Orchestrator's freshness check. They exist because detailed planning tends to turn speculation into apparent requirements, and agents then build what the plan says.

## Every piece of work needs a "why now"

State in one sentence what breaks today if this isn't built. Then classify the answer:

| Answer | Verdict |
|---|---|
| "X is broken, unfulfillable or silently wrong right now" | Build it |
| "Nothing yet, but when we do Y it will matter" | Backlog. One line, then stop |
| "It would be cleaner, nicer or more complete" | Not a slice. Say so out loud |

Completeness is not a reason. A design that is coherent from end to end is not thereby justified from end to end.

## Every slice needs an observable definition of done

Write it as something checkable in the running app. "The push flow uses one master file" is not observable. "In the preview, push a two-variant product, and both variants show the same file id" is.

If you can't write an observable definition of done, the slice is a layer, not a capability. Go back and reshape it.

## A spec is a proposal until the user approves that slice

- Slice documents describe candidate work. Approval happens per slice, at dispatch time.
- Approving one slice never approves the next.
- If you catch yourself thinking "the spec says so", that is the moment to ask, not to build.

## Verify before acting

A stale spec is worse than no spec, because it carries authority it hasn't earned.

- Check every claim about what has already shipped against the repo and merged PRs.
- Check every piece of arithmetic and every worked example.
- When a claim turns out stale, fix the document in the same session.

## Shape

- **Two levels only: epic, then slice.** A slice is one PR. If a slice needs sub-slices, the epic was scoped wrong. Go back up; don't recurse down.
- **Every slice records:** why now, the observable definition of done, exclusions (what it explicitly does not include), and cost proxies.
- **Cost proxies, not time estimates:** how many PRs, whether it touches a migration, whether it touches a live production path. Agents are bad at wall-clock estimates, and the number gets planned against as if it were real.
- **Give the plan a picture.** Draw a mermaid DAG: slices are nodes, dependencies are edges, and labels carry status and PR number.
- **Every decision can end in "not now".** That outcome must be as cheap to reach as "yes".

## Defaults

- **Declared beats computed** for curated domain lists. When a set is a business decision (which sizes are sold, which options pair), declare it as data. Don't derive it from a rule that happens to fit today's members.
- **Internal tooling has a lower bar than the product.** Admin screens, scripts and dashboards are judged by "is the manual version tolerable?". Ask before building a custom admin UI. The default answer is no.
- **Lean specs make changes of direction nearly free.** When a pivot hurts, the cause is usually a spec that was too detailed, not the pivot.
