from __future__ import annotations


def run(*, prompt: str, profile: dict[str, str]) -> str:
    return "# Review\n\n- Runner: `noop`\n- Result: review skipped for offline or test execution\n"
