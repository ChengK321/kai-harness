import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from kai_agent.cli import main
from kai_agent.runner import ClaudeCodeRunner, HarnessExecutionError, WorkspaceError


class RunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "workspaces"
        self.root.mkdir()
        self.workspace = self.root / "sandbox"
        self.workspace.mkdir()
        root_patch = patch("kai_agent.runner.WORKSPACE_ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        process_patch = patch("kai_agent.runner.subprocess.run")
        self.process = process_patch.start()
        self.addCleanup(process_patch.stop)
        self.payload = {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": "Found README.md",
            "session_id": "session-123",
            "num_turns": 3,
            "duration_ms": 2400,
            "total_cost_usd": 0.0123,
            "permission_denials": [],
        }
        self.set_output()
        self.runner = ClaudeCodeRunner()

    def set_output(self, returncode=0, stdout=None, stderr=""):
        self.process.return_value = subprocess.CompletedProcess(
            ["claude"], returncode,
            json.dumps(self.payload) if stdout is None else stdout,
            stderr,
        )

    def test_valid_workspace(self):
        self.assertEqual(self.runner.validate_workspace(self.workspace), self.workspace.resolve())

    def test_invalid_workspaces_do_not_launch_claude(self):
        file = self.root / "file.txt"
        file.write_text("test", encoding="utf-8")
        for workspace in (Path("relative"), self.root / "missing", file, self.root, self.base,
                          self.root / ".." / "..", Path("/etc")):
            with self.subTest(workspace=workspace):
                with self.assertRaises(WorkspaceError):
                    self.runner.run(workspace, "test")
        self.process.assert_not_called()

    def test_symlink_escape(self):
        link = self.root / "escape"
        link.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(WorkspaceError):
            self.runner.run(link, "test")
        self.process.assert_not_called()

    def test_internal_symlink_resolves_to_workspace(self):
        link = self.root / "inside"
        link.symlink_to(self.workspace, target_is_directory=True)
        self.runner.run(link, "test")
        self.assertEqual(self.process.call_args.kwargs["cwd"], self.workspace.resolve())

    def test_exact_command_and_process_options(self):
        prompt = "--tools Bash; $(touch /tmp/not-executed)"
        self.runner.run(self.workspace, prompt)
        self.process.assert_called_once_with(
            ["claude", "--bare", "--strict-mcp-config", "-p",
             "--tools", "Read,Glob,Grep", "--max-turns", "5",
             "--output-format", "json", "--no-session-persistence", "--", prompt],
            cwd=self.workspace.resolve(), shell=False, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=300, check=False,
        )
        self.assertNotIn("env", self.process.call_args.kwargs)

    def test_harness_isolation_flags_present(self):
        self.runner.run(self.workspace, "test")
        command = self.process.call_args.args[0]
        self.assertIn("--bare", command)
        self.assertIn("--strict-mcp-config", command)
        self.assertNotIn("--dangerously-skip-permissions", command)

    def test_success_json(self):
        self.payload["permission_denials"] = [{"tool_name": "Read"}]
        self.set_output(stderr="diagnostic\n")
        result = self.runner.run(self.workspace, "test")
        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.result, "Found README.md")
        self.assertEqual(result.session_id, "session-123")
        self.assertEqual(result.num_turns, 3)
        self.assertEqual(result.duration_ms, 2400)
        self.assertEqual(result.total_cost_usd, 0.0123)
        self.assertEqual(result.permission_denials, [{"tool_name": "Read"}])
        self.assertEqual(result.stderr, "diagnostic\n")

    def test_nonzero_exit(self):
        self.set_output(returncode=2, stdout="not JSON", stderr="provider unavailable")
        with self.assertRaisesRegex(HarnessExecutionError, "code 2: provider unavailable"):
            self.runner.run(self.workspace, "test")

    def test_nonzero_exit_uses_stdout_if_stderr_empty(self):
        self.set_output(returncode=1, stdout="provider error")
        with self.assertRaisesRegex(HarnessExecutionError, "provider error"):
            self.runner.run(self.workspace, "test")

    def test_invalid_json(self):
        self.set_output(stdout="not JSON")
        with self.assertRaisesRegex(HarnessExecutionError, "invalid JSON"):
            self.runner.run(self.workspace, "test")

    def test_invalid_result_shape(self):
        for payload in ([], None, {"result": []}):
            with self.subTest(payload=payload):
                self.set_output(stdout=json.dumps(payload))
                with self.assertRaises(HarnessExecutionError):
                    self.runner.run(self.workspace, "test")

    def test_timeout(self):
        self.process.side_effect = subprocess.TimeoutExpired(["claude"], 300)
        with self.assertRaisesRegex(HarnessExecutionError, "timed out after 300 seconds"):
            self.runner.run(self.workspace, "test")

    def test_missing_executable(self):
        self.process.side_effect = FileNotFoundError("claude not found")
        with self.assertRaisesRegex(HarnessExecutionError, "Cannot execute Claude Code"):
            self.runner.run(self.workspace, "test")

    def test_harness_error_with_zero_exit(self):
        self.set_output(stdout=json.dumps({
            "subtype": "error_max_turns", "is_error": True, "num_turns": 5,
        }))
        result = self.runner.run(self.workspace, "test")
        self.assertFalse(result.success)
        self.assertEqual(result.result, "error_max_turns")

    def test_cli_success(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--workspace", str(self.workspace), "test"])
        self.assertEqual(code, 0)
        for expected in ("Status: succeeded", "Turns: 3", "Cost: $0.0123",
                         "Duration: 2.4s", "Session: session-123", "Found README.md"):
            self.assertIn(expected, output.getvalue())

    def test_cli_execution_failure(self):
        self.set_output(returncode=1, stderr="provider unavailable")
        output = io.StringIO()
        with redirect_stderr(output):
            code = main(["--workspace", str(self.workspace), "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("provider unavailable", output.getvalue())

    def test_cli_workspace_failure(self):
        with redirect_stderr(io.StringIO()):
            code = main(["--workspace", "relative", "test"])
        self.assertNotEqual(code, 0)
        self.process.assert_not_called()

    def test_cli_harness_failure(self):
        self.set_output(stdout=json.dumps({"is_error": True, "subtype": "error_max_turns"}))
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--workspace", str(self.workspace), "test"])
        self.assertNotEqual(code, 0)
        self.assertIn("Status: failed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
