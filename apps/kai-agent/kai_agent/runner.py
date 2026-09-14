"""Validate a workspace and run the read-only Claude Code CLI."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


WORKSPACE_ROOT = Path("/srv/kai/workspaces")


class WorkspaceError(ValueError):
    """The workspace is missing or outside the permitted directory."""


class HarnessExecutionError(RuntimeError):
    """Claude Code could not execute or return a usable JSON result."""


@dataclass
class HarnessResult:
    success: bool
    exit_code: int
    result: str
    session_id: str | None
    num_turns: int | None
    duration_ms: int | None
    total_cost_usd: float | None
    permission_denials: list
    stderr: str


class ClaudeCodeRunner:
    """Delegate agent execution to Claude Code; inherit the process environment."""

    def __init__(self, timeout: float = 300):
        self.timeout = timeout

    @staticmethod
    def validate_workspace(workspace: str | Path) -> Path:
        path = Path(workspace)
        if not path.is_absolute():
            raise WorkspaceError("Workspace must be an absolute path.")
        try:
            resolved = path.resolve(strict=True)
            root = WORKSPACE_ROOT.resolve(strict=True)
            if resolved == root or not resolved.is_relative_to(root):
                raise WorkspaceError(f"Workspace must be below {WORKSPACE_ROOT}.")
            if not resolved.is_dir():
                raise WorkspaceError("Workspace must be a directory.")
        except (OSError, RuntimeError) as exc:
            raise WorkspaceError(f"Cannot resolve workspace: {exc}") from exc
        return resolved

    def run(self, workspace: str | Path, prompt: str) -> HarnessResult:
        cwd = self.validate_workspace(workspace)
        command = [
            "claude", "-p",
            "--tools", "Read,Glob,Grep",
            "--max-turns", "5",
            "--output-format", "json",
            "--no-session-persistence",
            "--", prompt,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise HarnessExecutionError(
                f"Claude Code timed out after {self.timeout:g} seconds."
            ) from exc
        except OSError as exc:
            raise HarnessExecutionError(f"Cannot execute Claude Code: {exc}") from exc

        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "No output."
            raise HarnessExecutionError(
                f"Claude Code exited with code {completed.returncode}: {detail}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise HarnessExecutionError(
                f"Claude Code returned invalid JSON: {exc}. Stderr: {completed.stderr}"
            ) from exc
        if not isinstance(payload, dict):
            raise HarnessExecutionError("Claude Code JSON result must be an object.")

        # Error results (for example max-turn exhaustion) may omit result text.
        success = not payload.get("is_error", False) and payload.get("subtype") == "success"
        result = payload.get("result", "")
        if not isinstance(result, str):
            raise HarnessExecutionError("Claude Code JSON 'result' must be a string.")
        if not success and not result:
            result = str(payload.get("errors") or payload.get("subtype") or "Unsuccessful harness result.")
        return HarnessResult(
            success=success,
            exit_code=completed.returncode,
            result=result,
            session_id=payload.get("session_id"),
            num_turns=payload.get("num_turns"),
            duration_ms=payload.get("duration_ms"),
            total_cost_usd=payload.get("total_cost_usd"),
            permission_denials=payload.get("permission_denials", []),
            stderr=completed.stderr,
        )
