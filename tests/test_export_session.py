import gzip
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "export_session.py")
SESSION_ID = "11111111-2222-3333-4444-555555555555"
STRIPE_KEY = "sk_live_" + "A1b2C3d4E5f6G7h8"
GITHUB_TOKEN = "ghp_" + "abcdefghijklmnopqrstuvwxyz0123"
DB_PASSWORD = "hunter2hunter2"


def event(kind, content, **extra):
    return {"type": kind, "message": {"role": kind, "content": content}, **extra}


def session_events(cwd):
    return [
        event("user", "Build slice F3 for me", cwd=cwd, timestamp="2026-11-17T01:00:00Z", version="2.1.322", gitBranch="add/f3"),
        event("assistant", [
            {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": f"{cwd}/.env.local"}},
            {"type": "tool_use", "id": "t2", "name": "Skill", "input": {"skill": "mcstack:orchestrate"}},
            {"type": "tool_use", "id": "t3", "name": "Agent", "input": {"subagent_type": "mcstack:developer", "prompt": "brief"}},
        ], cwd=cwd),
        event("user", [{"type": "tool_result", "tool_use_id": "t1", "content": "POSTGRES_URL=postgres://app:secret@db"}],
              toolUseResult={"file": {"content": "POSTGRES_URL=postgres://app:secret@db"}}, cwd=cwd),
        event("assistant", [{"type": "text", "text": f"Found {STRIPE_KEY} and {GITHUB_TOKEN}; mail ada@example.com; "
                                                    f"db postgres://app:{DB_PASSWORD}@neon.tech/x; STRIPE_WEBHOOK_SECRET=abcdef123456"}],
              cwd=cwd, gitBranch="add/f3"),
    ]


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as output:
        output.write("\n".join(json.dumps(row) for row in rows) + "\n")


def read_gz(path):
    with gzip.open(path, "rt") as source:
        return source.read()


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=30,
                          env={**os.environ, "CLAUDE_CODE_SESSION_ID": "", "MCSTACK_SESSIONS_DIR": ""})


class ExportSessionTest(unittest.TestCase):
    def setUp(self):
        self.projects = tempfile.mkdtemp()
        self.dest = tempfile.mkdtemp()
        self.cwd = tempfile.mkdtemp()
        slug = os.path.join(self.projects, "-Users-adri-shop")
        write_jsonl(os.path.join(slug, f"{SESSION_ID}.jsonl"), session_events(self.cwd))
        write_jsonl(os.path.join(slug, SESSION_ID, "subagents", "agent-a1.jsonl"),
                    [event("assistant", f"developer report with {GITHUB_TOKEN}", cwd=self.cwd)])

    def export(self, *extra):
        return run("--projects-dir", self.projects, "--session-id", SESSION_ID, "--dest", self.dest, *extra)

    def folder(self):
        sessions = os.path.join(self.dest, "sessions")
        return os.path.join(sessions, os.listdir(sessions)[0])

    def test_dry_run_reports_the_session_and_writes_nothing(self):
        result = self.export("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(SESSION_ID, result.stdout)
        self.assertIn("Build slice F3", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dest, "sessions")))

    def test_secrets_and_emails_never_reach_the_export(self):
        self.assertEqual(self.export().returncode, 0)
        exported = read_gz(os.path.join(self.folder(), "transcript.jsonl.gz"))
        exported += read_gz(os.path.join(self.folder(), "subagents", "agent-a1.jsonl.gz"))
        for secret in (STRIPE_KEY, GITHUB_TOKEN, DB_PASSWORD, "ada@example.com", "abcdef123456", "app:secret@db"):
            self.assertNotIn(secret, exported, secret)
        self.assertIn("[redacted: contents of a secrets file]", exported)
        self.assertIn("Build slice F3", exported)

    def test_code_that_names_secrets_is_kept(self):
        code = ("tokens = shell_tokens(command)\nconst apiKey = process.env.STRIPE_SECRET_KEY\n"
                "SECRET_FILE = re.compile(pattern)")
        write_jsonl(os.path.join(self.projects, "-Users-adri-shop", f"{SESSION_ID}.jsonl"),
                    [event("assistant", code, cwd=self.cwd, timestamp="2026-11-17T01:00:00Z")])
        self.assertEqual(self.export().returncode, 0)
        exported = read_gz(os.path.join(self.folder(), "transcript.jsonl.gz"))
        for line in ("shell_tokens(command)", "process.env.STRIPE_SECRET_KEY", "re.compile(pattern)"):
            self.assertIn(line, exported, line)

    def test_manifest_records_versions_roles_and_redactions(self):
        self.assertEqual(self.export().returncode, 0)
        with open(os.path.join(self.folder(), "manifest.json")) as source:
            manifest = json.load(source)
        self.assertEqual(manifest["session_id"], SESSION_ID)
        self.assertEqual(manifest["branch"], "add/f3")
        self.assertEqual(manifest["claude_code_version"], "2.1.322")
        self.assertTrue(manifest["mcstack_version"])
        self.assertEqual(manifest["skills_invoked"], {"mcstack:orchestrate": 1})
        self.assertEqual(manifest["agents_spawned"], {"mcstack:developer": 1})
        self.assertEqual(manifest["subagent_transcripts"], 1)
        self.assertEqual(manifest["redactions"]["secret_file_read"], 1)
        self.assertGreaterEqual(manifest["redactions"]["github_token"], 2)

    def test_newest_transcript_is_used_without_a_session_id(self):
        result = run("--projects-dir", self.projects, "--dry-run")
        self.assertIn(SESSION_ID, result.stdout)

    def test_missing_destination_stops_without_writing(self):
        result = run("--projects-dir", self.projects, "--session-id", SESSION_ID)
        self.assertEqual(result.returncode, 1)
        self.assertIn("MCSTACK_SESSIONS_DIR", result.stdout)

    def test_commits_into_a_git_destination(self):
        subprocess.run(["git", "init", "-q", self.dest], check=True)
        subprocess.run(["git", "-C", self.dest, "config", "user.email", "test@test"], check=True)
        subprocess.run(["git", "-C", self.dest, "config", "user.name", "test"], check=True)
        result = self.export()
        self.assertIn("committed, not pushed (no remote)", result.stdout)
        log = subprocess.run(["git", "-C", self.dest, "log", "--oneline"], capture_output=True, text=True).stdout
        self.assertIn("session: 2026-11-17", log)


if __name__ == "__main__":
    unittest.main()
