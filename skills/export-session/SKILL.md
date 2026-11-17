---
name: export-session
description: "Export this session's transcript, with secrets redacted, to the user's private sessions repo for later analysis. Use for /export-session, at the end of a session the user wants included."
disable-model-invocation: true
---

# Export session

The user wants this session kept for later analysis: how the workflow ran, what each role did and what it cost. Export it with the bundled script, then report.

The script is `../../scripts/export_session.py`, relative to this skill's directory. Use the absolute path.

## Steps

1. **Dry run first.** Run `python3 <script> --dry-run`. It prints the session it picked, its repo and branch, and the first prompt. The session is `$CLAUDE_CODE_SESSION_ID` when it's set, otherwise the most recently written transcript.
2. **Confirm it's this session.** If the printed opening prompt isn't this conversation's, stop and tell the user. They can pass `--session-id`.
3. **Check the destination.** The script writes to `$MCSTACK_SESSIONS_DIR`, a local clone of the user's private sessions repo. If it isn't set, stop and ask the user for the path. Pass it as `--dest`; never guess one. Never write to a public repo.
4. **Export.** Run `python3 <script>`, adding `--dest` if needed. If the user asked not to push, add `--no-push`.
5. **Report** in a few lines: the folder written, the redaction counts, and the git result. If the push failed, say so and leave the commit in place.

## What the script does

- Copies the transcript and any subagent transcripts as gzipped JSONL into `sessions/<date>_<repo>_<id>/`.
- Redacts common secret formats (Stripe, GitHub, AWS, Slack, `sk-` keys, JWTs, bearer tokens, private keys, passwords in URLs, `*_SECRET=` / `*_TOKEN=` style assignments) and email addresses. It replaces whole any result from reading a `.env`, `.pem` or similar secrets file.
- Writes `manifest.json` with the repo, the branch, the Claude Code and mcstack versions, the models used, tool calls, skills invoked, agents spawned, token totals and redaction counts.
- Commits the folder and pushes, when the destination is a git repository with a remote.

Redaction is a pattern list, not a guarantee. The sessions repo must stay private.
