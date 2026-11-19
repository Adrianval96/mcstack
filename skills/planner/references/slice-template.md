# Slice template

```markdown
### <ID> — <capability, in user terms>

**Why now:** <what breaks today without it>
**Definition of done (observable):** <what to do in the running app, and what you see>
**Excludes:** <what this slice explicitly does not do>
**Cost proxies:** PRs: <1, or a stack of N under the size cap: each step, a thinner vertical that works on its own> · migration: yes/no · live production path: yes/no
**Depends on:** <slice IDs, or none>
**Contracts:** <exact schema or contract definitions this slice introduces (columns, types, payloads, migration), or none>
**Files likely touched:** <paths, from reading the repo>
**Open questions for the user:** <or none>
**Status:** proposed | approved | in progress | PR #<n> | merged
```

A slice is one dispatch: one PR, or a stack when it's over the size cap in `rules/pull-requests.md`. If the definition of done can't be checked in the running app, the slice is a layer. Reshape it until it can be checked.
