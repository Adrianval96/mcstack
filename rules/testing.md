# Testing rules

These rules apply to Developer, Debugger and Reviewer.

## What to test

- **Test what a caller or user can observe:** the request that goes in and the response or rendered data that comes out. Don't test internal structure.
- **Prefer one integration test through a real call path** over several unit tests that re-check the same logic through different callers.
- **Before adding a unit test for a helper,** check whether a higher-level test already exercises it. If one does, the unit test is redundant.
- **New behaviour still gets its own test:** edge cases, error branches, a quirk specific to one caller.

## A mock that drifts from the real contract is worse than no test

Green tests can hide broken code when the mock no longer matches the thing it replaces.

- **When code calls a member of a mocked module, open the mock and confirm the member exists.** If the new code calls `toast.warning`, every factory that stubs `toast` needs `warning`.
- **Check a third-party stub against the package's own type definitions in `node_modules`,** not against what you assume the API looks like.
- **Never hand-build a framework's callback arguments from docs or memory.** Read what the framework actually passes. If you can't, say the test is unverified.
- **When a diff deletes or changes something, re-read that thing's tests.** A test that still passes after its reason to exist is gone asserts nothing.

## Tests that can't fail

Ask of every test: what change to the code would make this fail? If the answer is "none", the test is not protecting anything. Fix it or delete it.
