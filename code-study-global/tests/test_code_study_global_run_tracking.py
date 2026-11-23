from pathlib import Path

from skill_tools.code_study_global.run_tracking import (
    append_run_event,
    finalize_run,
    start_run,
    sync_future_work,
)


def test_start_run_creates_global_knowledge_base_entrypoints(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "docs" / "code-study-global",
        run_id="csg-20260714-153000-runtime",
        objective="Map global runtime topology",
        status="in_progress",
        focus_topics=["runtime", "startup"],
    )
    assert run.index.exists()
    assert run.current_run.exists()
    assert run.history_run.exists()
    assert run.future_work.exists()
    assert "## Document Snapshot" in run.index.read_text()
    assert "runtime-topology.md" in run.index.read_text()
    assert "runtime, startup" in run.current_run.read_text()


def test_append_event_updates_current_run_and_history(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "docs" / "code-study-global",
        run_id="csg-20260714-153000-global",
        objective="Map repository-wide architecture",
        status="in_progress",
        focus_topics=[],
    )
    append_run_event(
        output_root=tmp_path / "docs" / "code-study-global",
        run_id=run.run_id,
        phase="repository_inventory",
        action="Mapped build files and runtime entrypoints",
        evidence=["package layout inspected"],
        outputs=["docs/code-study-global/index.md"],
        next_step="Trace startup flow",
    )
    history = run.history_run.read_text()
    current = run.current_run.read_text()
    assert "repository_inventory" in history
    assert "Trace startup flow" in current
    assert "docs/code-study-global/index.md" in current


def test_sync_future_work_records_rationale_and_suggested_doc(tmp_path: Path) -> None:
    sync_future_work(
        output_root=tmp_path / "docs" / "code-study-global",
        topics=[
            {
                "topic": "runtime-topology",
                "priority": "high",
                "status": "open",
                "rationale": "Entrypoints are known but lifecycle is not traced.",
                "suggested_doc": "maps/runtime-topology.md",
            },
        ],
    )
    future_work = (tmp_path / "docs" / "code-study-global" / "future-work.md").read_text()
    assert "runtime-topology" in future_work
    assert "maps/runtime-topology.md" in future_work
    assert "Entrypoints are known" in future_work


def test_finalize_run_updates_status_and_next_topics(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "docs" / "code-study-global",
        run_id="csg-20260714-153000-global",
        objective="Map repository-wide architecture",
        status="in_progress",
        focus_topics=["module map"],
    )
    finalize_run(
        output_root=tmp_path / "docs" / "code-study-global",
        run_id=run.run_id,
        status="partial",
        next_topics=["state-and-data-flow"],
    )
    assert "- Status: `partial`" in run.current_run.read_text()
    assert "state-and-data-flow" in run.history_run.read_text()
