from __future__ import annotations

from typing import Protocol


class ReviewRunner(Protocol):
    def run(self, *, prompt: str, profile: dict[str, str]) -> str:
        ...
