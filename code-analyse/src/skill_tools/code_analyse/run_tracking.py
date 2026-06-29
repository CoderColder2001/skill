from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from skill_tools.common.files import atomic_write_text


@dataclass(frozen=True)
class RunPaths:
    run_id: str
    global_current: Path
    global_run: Path
    scope_current: Path | None
    scope_run: Path | None


def start_run(
    *,
    output_root: Path,
    run_id: str,
    scope_slug: str,
    objective: str,
    status: str,
    module_scoped: bool,
) -> RunPaths:
    global_current = output_root / "current-run.md"
    global_run = output_root / "runs" / f"{run_id}.md"
    scope_current = output_root / "scopes" / scope_slug / "current-run.md" if module_scoped else None
    scope_run = output_root / "scopes" / scope_slug / "runs" / f"{run_id}.md" if module_scoped else None

    current_body = _render_current_run(
        run_id=run_id,
        scope_slug=scope_slug,
        status=status,
        objective=objective,
        latest_event_lines=["- No events recorded yet."],
        output_lines=["- None recorded yet."],
        unresolved_lines=["- None recorded yet."],
        next_step_lines=["- Awaiting analysis activity."],
    )
    history_body = _render_run_history(
        run_id=run_id,
        scope_slug=scope_slug,
        status=status,
        objective=objective,
        timeline_lines=["- Run created."],
    )

    atomic_write_text(global_current, current_body)
    atomic_write_text(global_run, history_body)
    if scope_current is not None:
        atomic_write_text(scope_current, current_body)
    if scope_run is not None:
        atomic_write_text(scope_run, history_body)

    return RunPaths(
        run_id=run_id,
        global_current=global_current,
        global_run=global_run,
        scope_current=scope_current,
        scope_run=scope_run,
    )


def append_run_event(
    *,
    output_root: Path,
    run_id: str,
    phase: str,
    action: str,
    evidence: list[str],
    outputs: list[str],
    next_step: str,
) -> None:
    global_run = output_root / "runs" / f"{run_id}.md"
    scope_runs = list(output_root.glob(f"scopes/*/runs/{run_id}.md"))
    event_lines = _render_event_lines(
        phase=phase,
        action=action,
        evidence=evidence,
        outputs=outputs,
        next_step=next_step,
    )

    _append_lines(global_run, event_lines)
    for scope_run in scope_runs:
        _append_lines(scope_run, event_lines)

    latest_event_lines = _render_event_lines(
        phase=phase,
        action=action,
        evidence=evidence,
        outputs=outputs,
        next_step=next_step,
    )
    output_lines = _format_value_lines(outputs)
    next_step_lines = [f"- {next_step}"]

    global_current = output_root / "current-run.md"
    _update_current_run(
        current_path=global_current,
        latest_event_lines=latest_event_lines,
        output_lines=output_lines,
        next_step_lines=next_step_lines,
    )
    for scope_run in scope_runs:
        _update_current_run(
            current_path=scope_run.parents[1] / "current-run.md",
            latest_event_lines=latest_event_lines,
            output_lines=output_lines,
            next_step_lines=next_step_lines,
        )


def sync_future_work(*, output_root: Path, scope_slug: str, topics: list[dict[str, str]]) -> None:
    body = _render_future_work(topics)
    atomic_write_text(output_root / "future-work.md", body)
    if scope_slug != "repo":
        atomic_write_text(output_root / "scopes" / scope_slug / "future-work.md", body)


def finalize_run(*, output_root: Path, run_id: str, status: str, next_topics: list[str]) -> None:
    completion_lines = [
        "## Completion",
        "",
        f"- Status: `{status}`",
        f"- Next Topics: {', '.join(next_topics) if next_topics else 'none'}",
    ]
    global_run = output_root / "runs" / f"{run_id}.md"
    scope_runs = list(output_root.glob(f"scopes/*/runs/{run_id}.md"))

    _append_lines(global_run, completion_lines)
    for scope_run in scope_runs:
        _append_lines(scope_run, completion_lines)

    _update_current_status(
        current_path=output_root / "current-run.md",
        status=status,
        next_step_lines=[f"- Follow-up topics: {', '.join(next_topics) if next_topics else 'none'}"],
        latest_event_lines=[
            "### final_review",
            f"- Action: Finalized run `{run_id}`",
            f"- Evidence: status set to `{status}`",
            f"- Outputs: {global_run}",
            f"- Next Step: {', '.join(next_topics) if next_topics else 'none'}",
        ],
    )
    for scope_run in scope_runs:
        _update_current_status(
            current_path=scope_run.parents[1] / "current-run.md",
            status=status,
            next_step_lines=[f"- Follow-up topics: {', '.join(next_topics) if next_topics else 'none'}"],
            latest_event_lines=[
                "### final_review",
                f"- Action: Finalized run `{run_id}`",
                f"- Evidence: status set to `{status}`",
                f"- Outputs: {scope_run}",
                f"- Next Step: {', '.join(next_topics) if next_topics else 'none'}",
            ],
        )


def _render_current_run(
    *,
    run_id: str,
    scope_slug: str,
    status: str,
    objective: str,
    latest_event_lines: Iterable[str],
    output_lines: Iterable[str],
    unresolved_lines: Iterable[str],
    next_step_lines: Iterable[str],
) -> str:
    lines = [
        "# Current Run",
        "",
        f"- Run ID: `{run_id}`",
        f"- Scope: `{scope_slug}`",
        f"- Status: `{status}`",
        f"- Objective: {objective}",
        "",
        "## Latest Event",
        "",
        *latest_event_lines,
        "",
        "## Current Output Files",
        "",
        *output_lines,
        "",
        "## Unresolved Items",
        "",
        *unresolved_lines,
        "",
        "## Next Immediate Action",
        "",
        *next_step_lines,
        "",
    ]
    return "\n".join(lines)


def _render_run_history(
    *,
    run_id: str,
    scope_slug: str,
    status: str,
    objective: str,
    timeline_lines: Iterable[str],
) -> str:
    lines = [
        f"# Run {run_id}",
        "",
        f"- Scope: `{scope_slug}`",
        f"- Status: `{status}`",
        f"- Objective: {objective}",
        "",
        "## Timeline",
        "",
        *timeline_lines,
        "",
    ]
    return "\n".join(lines)


def _render_event_lines(
    *,
    phase: str,
    action: str,
    evidence: list[str],
    outputs: list[str],
    next_step: str,
) -> list[str]:
    return [
        f"### {phase}",
        f"- Action: {action}",
        f"- Evidence: {', '.join(evidence) if evidence else 'none'}",
        f"- Outputs: {', '.join(outputs) if outputs else 'none'}",
        f"- Next Step: {next_step}",
    ]


def _render_future_work(topics: list[dict[str, str]]) -> str:
    lines = ["# Future Work", ""]
    if not topics:
        lines.extend(["- No follow-up topics recorded.", ""])
        return "\n".join(lines)

    for topic in topics:
        lines.extend(
            [
                f"## {topic['topic']}",
                f"- Priority: `{topic['priority']}`",
                f"- Status: `{topic['status']}`",
                "",
            ]
        )
    return "\n".join(lines)


def _append_lines(path: Path, lines: Iterable[str]) -> None:
    document = path.read_text(encoding="utf-8").rstrip()
    addition = "\n".join(lines)
    atomic_write_text(path, f"{document}\n\n{addition}\n")


def _update_current_run(
    *,
    current_path: Path,
    latest_event_lines: list[str],
    output_lines: list[str],
    next_step_lines: list[str],
) -> None:
    document = current_path.read_text(encoding="utf-8")
    updated = _replace_section(document, "Latest Event", latest_event_lines)
    updated = _replace_section(updated, "Current Output Files", output_lines)
    updated = _replace_section(updated, "Next Immediate Action", next_step_lines)
    atomic_write_text(current_path, updated)


def _update_current_status(
    *,
    current_path: Path,
    status: str,
    next_step_lines: list[str],
    latest_event_lines: list[str],
) -> None:
    document = current_path.read_text(encoding="utf-8")
    updated = _replace_metadata_line(document, "Status", f"`{status}`")
    updated = _replace_section(updated, "Latest Event", latest_event_lines)
    updated = _replace_section(updated, "Next Immediate Action", next_step_lines)
    atomic_write_text(current_path, updated)


def _replace_section(document: str, heading: str, content_lines: list[str]) -> str:
    lines = document.rstrip().splitlines()
    heading_line = f"## {heading}"
    try:
        start = lines.index(heading_line)
    except ValueError:
        lines.extend(["", heading_line, "", *content_lines])
        return "\n".join(lines).rstrip() + "\n"

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    replacement = [heading_line, "", *content_lines]
    updated_lines = lines[:start] + replacement + lines[end:]
    return "\n".join(updated_lines).rstrip() + "\n"


def _replace_metadata_line(document: str, label: str, value: str) -> str:
    lines = document.rstrip().splitlines()
    prefix = f"- {label}: "
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{prefix}{value}"
            return "\n".join(lines).rstrip() + "\n"
    return document.rstrip() + f"\n{prefix}{value}\n"


def _format_value_lines(values: list[str]) -> list[str]:
    if not values:
        return ["- None recorded in this event."]
    return [f"- {value}" for value in values]
