"""Minimal command-line entry point for the Kai thin harness runner."""

import argparse
import sys

from .runner import ClaudeCodeRunner, HarnessExecutionError, WorkspaceError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run read-only Claude Code in a Kai workspace.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("prompt")
    args = parser.parse_args(argv)
    try:
        result = ClaudeCodeRunner().run(args.workspace, args.prompt)
    except (WorkspaceError, HarnessExecutionError) as exc:
        print(f"Status: failed\nError: {exc}", file=sys.stderr)
        return 1

    cost = result.total_cost_usd
    duration = result.duration_ms
    print(f"Status: {'succeeded' if result.success else 'failed'}")
    print(f"Turns: {result.num_turns if result.num_turns is not None else 'unknown'}")
    print(f"Cost: ${cost:.4f}" if isinstance(cost, (int, float)) else "Cost: unknown")
    print(f"Duration: {duration / 1000:.1f}s" if isinstance(duration, (int, float)) else "Duration: unknown")
    print(f"Session: {result.session_id or 'unknown'}")
    print(f"\nResult:\n{result.result}")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
