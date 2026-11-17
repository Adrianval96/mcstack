#!/usr/bin/env python3
"""Export one Claude Code session for later analysis, with secrets redacted.

Finds the session's transcript (and any subagent transcripts beside it), redacts
secrets and email addresses, writes gzipped copies plus a manifest into a sessions
directory, and commits and pushes that directory when it is a git repository.

Usage:
  export_session.py [--session-id ID] [--dest DIR] [--projects-dir DIR] [--dry-run] [--no-push]

The session is --session-id, else $CLAUDE_CODE_SESSION_ID, else the most recently
written transcript. The destination is --dest, else $MCSTACK_SESSIONS_DIR.
"""

import argparse
import collections
import datetime
import gzip
import json
import os
import re
import subprocess
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[private key]"),
    ("stripe_key", re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{10,}"), "[stripe key]"),
    ("webhook_secret", re.compile(r"\bwhsec_[A-Za-z0-9]{10,}"), "[webhook secret]"),
    ("api_key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), "[api key]"),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"), "[github token]"),
    ("aws_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[aws key]"),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "[slack token]"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "[jwt]"),
    ("bearer", re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]{16,}"), r"\1[token]"),
    ("url_password", re.compile(r"([a-z][a-z0-9+.-]*://[^:/\s@]+:)[^@\s]+@"), r"\1[password]@"),
    ("secret_assignment", re.compile(
        r"(?i)(\b[A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_KEY|APIKEY|PRIVATE_KEY|DSN)[A-Z0-9_]*\s*[=:]\s*[\"']?)"
        r"(?!process\.env|os\.environ|os\.getenv)[^\s\"',;()]{8,}(?![(\w])"), r"\1[redacted]"),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[email]"),
]

SECRET_FILE = re.compile(r"(^|/)(\.env[^/\s]*|[^/\s]*\.pem|id_[a-z0-9]+|credentials[^/\s]*)$")
SECRET_FILE_IN_COMMAND = re.compile(r"(^|[\s/'\"])(\.env[\w.-]*|[\w.-]*\.pem|id_(?:rsa|ed25519|ecdsa))\b")
SECRET_FILE_PLACEHOLDER = "[redacted: contents of a secrets file]"


class Redactor:
    def __init__(self):
        self.counts = collections.Counter()

    def text(self, value):
        for name, pattern, replacement in PATTERNS:
            value, hits = pattern.subn(replacement, value)
            self.counts[name] += hits
        return value

    def walk(self, value):
        if isinstance(value, str):
            return self.text(value)
        if isinstance(value, list):
            return [self.walk(item) for item in value]
        if isinstance(value, dict):
            return {key: self.walk(item) for key, item in value.items()}
        return value


def reads_secret_file(tool_use):
    tool_input = tool_use.get("input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if path and SECRET_FILE.search(path):
        return True
    command = tool_input.get("command") or ""
    return bool(command and SECRET_FILE_IN_COMMAND.search(command))


def content_blocks(event):
    message = event.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), list):
        return [block for block in message["content"] if isinstance(block, dict)]
    return []


def redact_events(events, redactor):
    secret_tool_ids = {
        block.get("id")
        for event in events
        for block in content_blocks(event)
        if block.get("type") == "tool_use" and reads_secret_file(block)
    }
    redacted = []
    for event in events:
        if any(block.get("type") == "tool_result" and block.get("tool_use_id") in secret_tool_ids
               for block in content_blocks(event)):
            for block in content_blocks(event):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in secret_tool_ids:
                    block["content"] = SECRET_FILE_PLACEHOLDER
            if "toolUseResult" in event:
                event["toolUseResult"] = SECRET_FILE_PLACEHOLDER
            redactor.counts["secret_file_read"] += 1
        redacted.append(redactor.walk(event))
    return redacted


def read_events(path):
    events = []
    with open(path) as transcript:
        for line in transcript:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except ValueError:
                    continue
    return events


def find_transcript(projects_dir, session_id):
    candidates = []
    for root, _, files in os.walk(projects_dir):
        if os.sep + "subagents" in root:
            continue
        for name in files:
            if name.endswith(".jsonl") and os.path.dirname(os.path.join(root, name)) != projects_dir:
                if session_id is None or name == f"{session_id}.jsonl":
                    candidates.append(os.path.join(root, name))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def subagent_transcripts(transcript):
    folder = transcript[: -len(".jsonl")]
    found = []
    for root, _, files in os.walk(folder):
        found.extend(os.path.join(root, name) for name in files if name.endswith(".jsonl"))
    return sorted(found)


def git(cwd, *args):
    try:
        result = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def plugin_version():
    try:
        with open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")) as manifest:
            return json.load(manifest).get("version")
    except (OSError, ValueError):
        return None


def first_prompt(events):
    for event in events:
        message = event.get("message")
        if event.get("type") == "user" and isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
            for block in content_blocks(event):
                if block.get("type") == "text" and block.get("text", "").strip():
                    return block["text"].strip()
    return ""


def summarize(session_id, events, subagent_files):
    tools, skills, agents, models = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    tokens = collections.Counter()
    for event in events:
        message = event.get("message")
        if event.get("type") == "assistant" and isinstance(message, dict):
            if message.get("model"):
                models[message["model"]] += 1
            for field, amount in (message.get("usage") or {}).items():
                if isinstance(amount, int):
                    tokens[field] += amount
        for block in content_blocks(event):
            if block.get("type") == "tool_use":
                tools[block.get("name")] += 1
                tool_input = block.get("input") or {}
                if block.get("name") == "Skill" and tool_input.get("skill"):
                    skills[tool_input["skill"]] += 1
                if block.get("name") in ("Agent", "Task") and tool_input.get("subagent_type"):
                    agents[tool_input["subagent_type"]] += 1
    last = next((event for event in reversed(events) if event.get("cwd")), {})
    cwd = last.get("cwd", "")
    toplevel = git(cwd, "rev-parse", "--show-toplevel") if cwd and os.path.isdir(cwd) else None
    return {
        "session_id": session_id,
        "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "started_at": next((event.get("timestamp") for event in events if event.get("timestamp")), None),
        "repo": os.path.basename(toplevel or cwd) or None,
        "branch": last.get("gitBranch"),
        "claude_code_version": next((event.get("version") for event in reversed(events) if event.get("version")), None),
        "mcstack_version": plugin_version(),
        "models": dict(models),
        "events": len(events),
        "subagent_transcripts": len(subagent_files),
        "tool_calls": dict(tools),
        "skills_invoked": dict(skills),
        "agents_spawned": dict(agents),
        "tokens": dict(tokens),
    }


def write_jsonl_gz(path, events):
    with gzip.open(path, "wt") as output:
        for event in events:
            output.write(json.dumps(event, ensure_ascii=False) + "\n")


def commit_and_push(dest, folder_name, push):
    if git(dest, "rev-parse", "--is-inside-work-tree") != "true":
        return "not a git repository: files written, nothing committed"
    git(dest, "add", "--", os.path.join("sessions", folder_name))
    if git(dest, "commit", "-m", f"session: {folder_name}") is None:
        return "commit failed: files written but not committed"
    if not push:
        return "committed, not pushed (--no-push)"
    if not git(dest, "remote"):
        return "committed, not pushed (no remote)"
    return "committed and pushed" if git(dest, "push") is not None else "committed, but the push failed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session-id", default=os.environ.get("CLAUDE_CODE_SESSION_ID") or None)
    parser.add_argument("--dest", default=os.environ.get("MCSTACK_SESSIONS_DIR") or None)
    parser.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args(argv)

    transcript = find_transcript(args.projects_dir, args.session_id)
    if transcript is None:
        print(f"No transcript found in {args.projects_dir}" + (f" for session {args.session_id}" if args.session_id else ""))
        return 1
    session_id = os.path.basename(transcript)[: -len(".jsonl")]
    events = read_events(transcript)
    subagent_files = subagent_transcripts(transcript)
    manifest = summarize(session_id, events, subagent_files)
    folder_name = f"{(manifest['started_at'] or manifest['exported_at'])[:10]}_{manifest['repo'] or 'unknown'}_{session_id[:8]}"

    print(f"Session:    {session_id}")
    print(f"Transcript: {transcript} ({len(events)} events, {len(subagent_files)} subagent transcripts)")
    print(f"Repo:       {manifest['repo']} on {manifest['branch']}")
    print(f"Opened with: {first_prompt(events)[:160]!r}")
    if args.dry_run:
        print(f"Dry run: would write sessions/{folder_name}/ under {args.dest or '$MCSTACK_SESSIONS_DIR (not set)'}")
        return 0
    if not args.dest:
        print("No destination. Set MCSTACK_SESSIONS_DIR to a local clone of your private sessions repo, or pass --dest.")
        return 1

    redactor = Redactor()
    folder = os.path.join(args.dest, "sessions", folder_name)
    os.makedirs(os.path.join(folder, "subagents"), exist_ok=True)
    write_jsonl_gz(os.path.join(folder, "transcript.jsonl.gz"), redact_events(events, redactor))
    for path in subagent_files:
        name = os.path.basename(path)[: -len(".jsonl")]
        write_jsonl_gz(os.path.join(folder, "subagents", f"{name}.jsonl.gz"), redact_events(read_events(path), redactor))
    manifest["redactions"] = {name: count for name, count in sorted(redactor.counts.items()) if count}
    with open(os.path.join(folder, "manifest.json"), "w") as output:
        json.dump(redactor.walk(manifest), output, indent=2)

    print(f"Wrote:      {folder}")
    print(f"Redacted:   {manifest['redactions'] or 'nothing matched'}")
    print(f"Git:        {commit_and_push(args.dest, folder_name, not args.no_push)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
