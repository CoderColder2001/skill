from __future__ import annotations

import hashlib


def run(*, prompt: str, profile: dict[str, str]) -> str:
    transport = profile.get("transport", "mock")
    if transport != "mock":
        raise NotImplementedError("Codex-thread review runner only supports `transport: mock` right now.")

    prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    return "\n".join(
        [
            "# Review",
            "",
            "## Backend",
            "",
            "- Runner: `codex_thread`",
            f"- Thread URL: `{profile.get('thread_url', 'mock://codex-thread')}`",
            f"- Prompt Digest: `{prompt_digest}`",
            "",
            "## Findings",
            "",
            "- This is a placeholder mock for thread-based review execution.",
            "- Use it for integration wiring checks before a real Codex thread backend is configured.",
        ]
    )
