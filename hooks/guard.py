#!/usr/bin/env python3
"""PreToolUse guard for mcstack.

Always on:
  - deny `--no-verify` on git commands
  - ask before merging, reviewing or commenting (git hosting CLIs and GitHub MCP tools)
  - ask before force-pushing

Per project, from `.claude/mcstack.json` at the repo root:
  - branchPattern: regex the current branch must match before `git commit`
  - forbiddenCommands: [{"pattern": regex, "message": text}] denied with that message

Reads the hook payload on stdin. Prints a PreToolUse decision as JSON, or nothing to allow.
"""

import json
import os
import re
import subprocess
import sys

CONFIG_RELATIVE_PATH = os.path.join(".claude", "mcstack.json")

OUTWARD_BASH_PATTERNS = [
    (re.compile(r"\bgh\s+pr\s+merge\b"), "merges a pull request"),
    (re.compile(r"\bgh\s+pr\s+review\b"), "submits a review"),
    (re.compile(r"\bgh\s+(pr|issue)\s+comment\b"), "posts a comment"),
    (re.compile(r"\bgh\s+api\b.*\b(comments|reviews|merge)\b"), "posts to a review, comment or merge endpoint"),
]

OUTWARD_MCP_TOOLS = re.compile(
    r"^mcp__.*github.*__(merge_pull_request|add_issue_comment|add_reply_to_pull_request_comment"
    r"|pull_request_review_write|add_comment_to_pending_review|update_issue_comment)$"
)

FORCE_PUSH = re.compile(r"\bgit\b[^;&|]*\bpush\b[^;&|]*(\s--force(?!-with-lease)\b|\s-f\b)")
NO_VERIFY = re.compile(r"\bgit\b[^;&|]*\s--no-verify\b")
GIT_COMMIT = re.compile(r"\bgit\b[^;&|]*\bcommit\b")


def decision(kind, reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": kind,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def git_output(cwd, *args):
    try:
        result = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def load_config(cwd):
    root = git_output(cwd, "rev-parse", "--show-toplevel") or cwd
    path = os.path.join(root, CONFIG_RELATIVE_PATH)
    try:
        with open(path) as config_file:
            return json.load(config_file)
    except (OSError, ValueError):
        return {}


def check_bash(command, cwd):
    if NO_VERIFY.search(command):
        decision("deny", "--no-verify skips the project's checks. Fix what the hook reports instead.")

    for pattern, action in OUTWARD_BASH_PATTERNS:
        if pattern.search(command):
            decision("ask", f"This command {action}, which speaks as the user. It needs an explicit request in this session.")

    if FORCE_PUSH.search(command):
        decision("ask", "Force-push rewrites remote history. Prefer --force-with-lease, and only on your own branch.")

    config = load_config(cwd)

    for rule in config.get("forbiddenCommands", []):
        if re.search(rule.get("pattern", r"(?!)"), command):
            decision("deny", rule.get("message", "This command is forbidden by .claude/mcstack.json."))

    branch_pattern = config.get("branchPattern")
    if branch_pattern and GIT_COMMIT.search(command):
        branch = git_output(cwd, "symbolic-ref", "--short", "HEAD")
        if branch and not re.search(branch_pattern, branch):
            decision(
                "deny",
                f"Branch '{branch}' does not match this project's branch pattern {branch_pattern}. "
                "Rename it first: git branch -m <prefix>/<short-description>",
            )


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()

    if OUTWARD_MCP_TOOLS.match(tool_name):
        decision("ask", "This GitHub action speaks as the user. It needs an explicit request in this session.")

    if tool_name == "Bash":
        check_bash(tool_input.get("command", ""), cwd)

    sys.exit(0)


if __name__ == "__main__":
    main()
