from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from skill_tools.common.files import atomic_write_text


@dataclass(frozen=True)
class RunPaths:
    run_id: str
    index: Path
    current_run: Path
    history_run: Path
    future_work: Path


def start_run(
    *,
    output_root: Path,
    run_id: str,
    objective: str,
    status: str,
    focus_topics: list[str],
) -> RunPaths:
    index = output_root / "index.md"
    current_run = output_root / "current-run.md"
    history_run = output_root / "runs" / f"{run_id}.md"
    future_work = output_root / "future-work.md"

    _ensure_index(index)
    current_body = _render_current_run(
        run_id=run_id,
        status=status,
        objective=objective,
        focus_topics=focus_topics,
        latest_event_lines=["- No events recorded yet."],
        output_lines=["- None recorded yet."],
        unresolved_lines=["- None recorded yet."],
        next_step_lines=["- Awaiting global study activity."],
    )
    history_body = _render_run_history(
        run_id=run_id,
        status=status,
        objective=objective,
        focus_topics=focus_topics,
        timeline_lines=["- Run created."],
    )

    atomic_write_text(current_run, current_body)
    atomic_write_text(history_run, history_body)
    if not future_work.exists():
        atomic_write_text(future_work, _render_future_work([]))

    return RunPaths(
        run_id=run_id,
        index=index,
        current_run=current_run,
        history_run=history_run,
        future_work=future_work,
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
    history_run = output_root / "runs" / f"{run_id}.md"
    event_lines = _render_event_lines(
        phase=phase,
        action=action,
        evidence=evidence,
        outputs=outputs,
        next_step=next_step,
    )

    _append_lines(history_run, event_lines)
    _update_current_run(
        current_path=output_root / "current-run.md",
        latest_event_lines=event_lines,
        output_lines=_format_value_lines(outputs),
        next_step_lines=[f"- {next_step}"],
    )


def sync_future_work(*, output_root: Path, topics: list[dict[str, str]]) -> None:
    atomic_write_text(output_root / "future-work.md", _render_future_work(topics))


def finalize_run(*, output_root: Path, run_id: str, status: str, next_topics: list[str]) -> None:
    completion_lines = [
        "## Completion",
        "",
        f"- Status: `{status}`",
        f"- Next Topics: {', '.join(next_topics) if next_topics else 'none'}",
    ]
    history_run = output_root / "runs" / f"{run_id}.md"
    _append_lines(history_run, completion_lines)

    _update_current_status(
        current_path=output_root / "current-run.md",
        status=status,
        next_step_lines=[f"- Follow-up topics: {', '.join(next_topics) if next_topics else 'none'}"],
        latest_event_lines=[
            "### final_review",
            f"- Action: Finalized run `{run_id}`",
            f"- Evidence: status set to `{status}`",
            f"- Outputs: {history_run}",
            f"- Next Step: {', '.join(next_topics) if next_topics else 'none'}",
        ],
    )


def _ensure_index(index: Path) -> None:
    if index.exists():
        return
    lines = [
        "# Code Study Global",
        "",
        "## Document Snapshot",
        "",
        "- Project root: `unknown`",
        "- Branch: `unknown`",
        "- HEAD: `unknown`",
        "- HEAD time: `unknown`",
        "- HEAD subject: `unknown`",
        "- Document update time: `unknown`",
        "- Working tree: `unknown`",
        "- Source link style: `unknown`",
        "- Docs ignored by git: `unknown`",
        "",
        "## Start Here",
        "",
        "- [Current Run](current-run.md)",
        "- [Future Work](future-work.md)",
        "",
        "## Recommended Structure",
        "",
        "```text",
        "maps/",
        "  module-map.md",
        "  runtime-topology.md",
        "  dependency-boundaries.md",
        "topics/",
        "  startup-flow.md",
        "  execution-flows.md",
        "  state-and-data-flow.md",
        "  integration-points.md",
        "```",
        "",
    ]
    atomic_write_text(index, "\n".join(lines))


def _render_current_run(
    *,
    run_id: str,
    status: str,
    objective: str,
    focus_topics: Iterable[str],
    latest_event_lines: Iterable[str],
    output_lines: Iterable[str],
    unresolved_lines: Iterable[str],
    next_step_lines: Iterable[str],
) -> str:
    lines = [
        "# Current Global Study Run",
        "",
        f"- Run ID: `{run_id}`",
        f"- Status: `{status}`",
        f"- Objective: {objective}",
        f"- Focus Topics: {_join_values(focus_topics)}",
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
    status: str,
    objective: str,
    focus_topics: Iterable[str],
    timeline_lines: Iterable[str],
) -> str:
    lines = [
        f"# Global Study Run {run_id}",
        "",
        f"- Status: `{status}`",
        f"- Objective: {objective}",
        f"- Focus Topics: {_join_values(focus_topics)}",
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
                f"- Rationale: {topic.get('rationale', 'not recorded')}",
                f"- Suggested Document: {topic.get('suggested_doc', 'not recorded')}",
                "",
            ]
        )
    return "\n".join(lines)


def _update_current_run(
    *,
    current_path: Path,
    latest_event_lines: list[str],
    output_lines: list[str],
    next_step_lines: list[str],
) -> None:
    current = current_path.read_text(encoding="utf-8")
    current = _replace_section(current, "## Latest Event", latest_event_lines)
    current = _replace_section(current, "## Current Output Files", output_lines)
    current = _replace_section(current, "## Next Immediate Action", next_step_lines)
    atomic_write_text(current_path, current)


def _update_current_status(
    *,
    current_path: Path,
    status: str,
    latest_event_lines: list[str],
    next_step_lines: list[str],
) -> None:
    current = current_path.read_text(encoding="utf-8")
    lines = [f"- Status: `{status}`" if line.startswith("- Status: `") else line for line in current.splitlines()]
    current = "\n".join(lines)
    current = _replace_section(current, "## Latest Event", latest_event_lines)
    current = _replace_section(current, "## Next Immediate Action", next_step_lines)
    atomic_write_text(current_path, current + "\n")


def _replace_section(document: str, heading: str, replacement_lines: list[str]) -> str:
    lines = document.splitlines()
    start = lines.index(heading) + 1
    while start < len(lines) and lines[start] == "":
        start += 1

    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1

    new_lines = lines[:start] + replacement_lines + [""] + lines[end:]
    return "\n".join(new_lines) + "\n"


def _append_lines(path: Path, lines: list[str]) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "" if existing.endswith("\n") or not existing else "\n"
    appended = "\n".join(lines)
    atomic_write_text(path, f"{existing}{separator}{appended}\n")


def _format_value_lines(values: list[str]) -> list[str]:
    if not values:
        return ["- None recorded yet."]
    return [f"- {value}" for value in values]


def _join_values(values: Iterable[str]) -> str:
    values = list(values)
    return ", ".join(values) if values else "not specified"
