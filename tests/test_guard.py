import json
import os
import subprocess
import sys
import tempfile
import unittest

GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks", "guard.py")


def run_guard(payload):
    result = subprocess.run(
        [sys.executable, GUARD], input=json.dumps(payload), capture_output=True, text=True, timeout=10
    )
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]


def bash(command, cwd):
    return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "-b", "claude/hopeful-bhabha", self.repo], check=True)

    def write_config(self, config):
        os.makedirs(os.path.join(self.repo, ".claude"), exist_ok=True)
        with open(os.path.join(self.repo, ".claude", "mcstack.json"), "w") as config_file:
            json.dump(config, config_file)

    def test_allows_ordinary_commands(self):
        self.assertIsNone(run_guard(bash("git status && ls", self.repo)))

    def test_denies_no_verify(self):
        self.assertEqual(run_guard(bash("git commit --no-verify -m x", self.repo)), "deny")

    def test_asks_before_merge_and_comments(self):
        for command in ("gh pr merge 12 --squash", "gh pr comment 12 -b hi", "gh pr review 12 --approve",
                        "gh api repos/o/r/pulls/12/comments -f body=x"):
            self.assertEqual(run_guard(bash(command, self.repo)), "ask", command)

    def test_asks_before_github_mcp_merge(self):
        payload = {"tool_name": "mcp__github__merge_pull_request", "tool_input": {}, "cwd": self.repo}
        self.assertEqual(run_guard(payload), "ask")

    def test_force_push_asks_but_lease_is_allowed(self):
        self.assertEqual(run_guard(bash("git push --force origin main", self.repo)), "ask")
        self.assertIsNone(run_guard(bash("git push --force-with-lease origin add/x", self.repo)))

    def test_branch_pattern_blocks_auto_generated_branch(self):
        self.write_config({"branchPattern": "^(fix|add|change|refactor|chore)/"})
        self.assertEqual(run_guard(bash("git commit -m x", self.repo)), "deny")
        subprocess.run(["git", "-C", self.repo, "checkout", "-q", "-b", "add/portfolio-filtering"], check=True)
        self.assertIsNone(run_guard(bash("git commit -m x", self.repo)))

    def test_branch_pattern_ignored_without_config(self):
        self.assertIsNone(run_guard(bash("git commit -m x", self.repo)))

    def test_forbidden_command_denied_with_its_message(self):
        self.write_config({"forbiddenCommands": [{"pattern": "vitest.*--environment=node", "message": "use the agreed command"}]})
        self.assertEqual(run_guard(bash("npx vitest run --environment=node", self.repo)), "deny")
        self.assertIsNone(run_guard(bash("npx vitest run", self.repo)))


if __name__ == "__main__":
    unittest.main()
