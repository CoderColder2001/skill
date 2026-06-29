from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text, write_json


@dataclass(frozen=True)
class DebugRun:
    skill_root: Path
    run_root: Path
    debug_log: Path
    artifact_index: Path
    review_request: Path


def start_debug_run(
    *,
    skill_root: Path,
    skill_name: str,
    debug_run_id: str,
    linked_skill_run_id: str,
    scope_slug: str,
    trigger_source: str,
    review_mode: str,
) -> DebugRun:
    resolved_skill_root = skill_root.resolve()
    run_root = _debug_runs_root(resolved_skill_root) / "runs" / _validate_debug_path_segment(debug_run_id)
    debug_log = run_root / "debug-log.md"
    artifact_index = run_root / "artifacts" / "artifact-index.md"
    review_request = run_root / "review-request.json"
    atomic_write_text(
        debug_log,
        "\n".join(
            [
                "# Debug Log",
                "",
                f"- Skill: `{skill_name}`",
                f"- Debug Run ID: `{debug_run_id}`",
                f"- Linked Skill Run ID: `{linked_skill_run_id}`",
                f"- Scope: `{scope_slug}`",
                f"- Trigger Source: `{trigger_source}`",
                f"- Review Mode: `{review_mode}`",
                "",
                "## Timeline",
                "",
            ]
        ),
    )
    atomic_write_text(artifact_index, "# Artifact Index\n\n")
    write_json(
        review_request,
        {
            "skill_name": skill_name,
            "debug_run_id": debug_run_id,
            "linked_skill_run_id": linked_skill_run_id,
            "review_mode": review_mode,
        },
    )
    return DebugRun(
        skill_root=resolved_skill_root,
        run_root=run_root,
        debug_log=debug_log,
        artifact_index=artifact_index,
        review_request=review_request,
    )


def load_debug_run(*, skill_root: Path, run_root: Path) -> DebugRun:
    resolved_skill_root = skill_root.resolve()
    allowed_root = (_debug_runs_root(resolved_skill_root) / "runs").resolve()
    resolved_run_root = run_root.resolve()
    if allowed_root != resolved_run_root.parent and allowed_root not in resolved_run_root.parents:
        raise ValueError(f"Debug run root `{resolved_run_root}` must stay under `{allowed_root}`.")
    return DebugRun(
        skill_root=resolved_skill_root,
        run_root=resolved_run_root,
        debug_log=resolved_run_root / "debug-log.md",
        artifact_index=resolved_run_root / "artifacts" / "artifact-index.md",
        review_request=resolved_run_root / "review-request.json",
    )


def append_debug_event(
    *,
    run: DebugRun,
    phase: str,
    action: str,
    evidence: list[str],
    artifact_refs: list[str],
) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    block = [
        f"### {phase}",
        f"- Action: {action}",
        f"- Evidence: {', '.join(evidence) if evidence else 'none'}",
        f"- Artifact Refs: {', '.join(artifact_refs) if artifact_refs else 'none'}",
        "",
    ]
    atomic_write_text(run.debug_log, current + "\n".join(block))


def finalize_debug_run(*, run: DebugRun, review_mode: str) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    atomic_write_text(run.debug_log, current + "## Review Trigger\n\n" + f"- Mode: `{review_mode}`\n")
    artifact_index = run.artifact_index.read_text(encoding="utf-8")
    atomic_write_text(
        run.artifact_index,
        artifact_index + "- `debug-log.md` - human-readable execution trace\n",
    )


def _debug_runs_root(skill_root: Path) -> Path:
    return skill_root / "skill-debug-logs"


def _validate_debug_path_segment(value: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute() or any(part in {"..", "."} for part in candidate.parts):
        raise ValueError(f"Invalid debug path segment `{value}`.")
    normalized = candidate.as_posix()
    if normalized in {"", "/"}:
        raise ValueError("Debug path segment cannot be empty.")
    return normalized
