# Engineering rules

These rules apply in every project, to Lead, Planner, Orchestrator, Developer, Debugger and Reviewer. A project's instructions can add to them, or set one aside by naming it. Where they say nothing, these rules hold.

## Architecture: ports and adapters

Business logic never depends on a framework, a database or a third-party API. Dependencies point inward.

| Layer | Holds | May depend on |
|---|---|---|
| Domain | Business rules and types. No I/O, no framework imports | Nothing outside itself |
| Application | Use cases. Declares the ports (interfaces) it needs for I/O | Domain |
| Adapters | HTTP routes, UI, database, third-party clients, CLIs. Each implements a port or calls a use case | Application, domain. Never another adapter |
| Composition root | The one place that builds adapters and hands them to use cases | Everything |

- **Put every change in a layer, and name the layer in plans and PRs.** A rule that decides what the user gets is domain or application code, even when it's one `if`.
- **When to add a port.** Where a project uses this layout, its ports are part of the architecture, and Reviewer doesn't flag them as over-engineering. Anywhere else, add a port only when a use case does I/O that a test needs to fake. Otherwise the lean rule in `delivery.md` applies.
- **Test use cases with in-memory fakes of their ports,** not mocks of classes you own. A fake implements the port, so a changed port signature breaks the test; a mock doesn't.
- **If the project enforces the layering with a tool** (import-linter, dependency-cruiser, ESLint boundaries), it's part of lint and must pass.
- **In a codebase that isn't laid out this way,** don't restructure existing code unless the slice asks for it. New business logic still goes in a framework-free module behind a narrow interface, called from the framework's file (a route, a collection hook). Framework configuration stays where the framework expects it. Reviewer flags new business logic written inside an adapter; it doesn't flag the existing layout.

## Dead code

Dead code is anything no running path reaches: unused exports, functions, types, components, files, config keys, env vars, flags stuck on one value, dependencies, and tests of deleted code.

- **Look for it on every change.** Before reporting, check what your change replaced or stopped calling, and the code around it. Use the project's dead-code tool if it has one (knip, ts-prune, vulture, deadcode). Otherwise search for every reference, including string and dynamic lookups.
- **In scope: delete it in the same PR.** Code your change left unused, or dead code belonging to the capability the slice changes, is part of the slice. Remove it with its tests. Leaving it behind is a Reviewer finding.
- **Out of scope: report it, don't touch it.** Dead code anywhere else goes in your report, with each search you ran and its output. The orchestrator sends a fresh developer to trace it and open a separate removal PR.
- **In doubt: flag it to the user.** Don't delete what something outside static search may still reach: public or exported API, routes and webhooks called from outside, CLI commands, cron and queue handlers, migrations, names built from strings or reflection, config read at runtime, a flag that's off but planned. Report what you checked and what you couldn't.

## Code

- **Reuse before writing.** Search for an existing helper, type or pattern first. Re-implementing one that lives a few files away is a finding.
- **No new dependency without the user's yes.** A few lines of code beat a package. Pin versions; never `latest` or `*`.
- **The simplest option that meets the definition of done.** No configuration for a value that never changes, and no code "for later".
- **Strict types.** No `any` or untyped escape hatch unless it's truly unavoidable, and then with a comment saying why. Use generated types; don't redeclare them.
- **Name every non-trivial shape.** A return type or parameter object with more than one field gets a named type, following the project's naming convention. Don't inline it in the signature.
- **Validate at trust boundaries:** user input, webhooks, third-party responses. Validate on the server, inside the adapter, before the data reaches a use case.
- **Never swallow an error.** Handle it, or let it reach a layer that can. Never send internal errors, stack traces or file paths to a client.
- **Secrets come from the environment.** Never in code, logs, test fixtures or PR bodies.
